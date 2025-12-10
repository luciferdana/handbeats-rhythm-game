"""
Lane/Zone Management - Target Areas for Hand Detection
Manages the 3 instrument zones (Kick, Snare, Hi-Hat) with visual effects
"""

import pygame
from typing import Tuple
from config.constants import ZONES, COLOR_ZONE_INACTIVE, COLOR_ZONE_ACTIVE, COLOR_ZONE_HIT


class Lane:
    """
    Represents a single instrument lane/zone
    Visual effects: glow, activation, hit feedback
    """

    def __init__(self, zone_config: dict, image_path: str):
        """
        Initialize lane with zone configuration

        Args:
            zone_config: Zone dict from constants (x, y, width, height, color, name, etc.)
            image_path: Path to instrument icon image
        """
        # Collision coordinates (for hit detection)
        self.x = zone_config['x']
        self.y = zone_config['y']
        self.width = zone_config['width']
        self.height = zone_config['height']

        # Visual coordinates (inverted X for display to match flipped video)
        from config.constants import SCREEN_WIDTH
        self.visual_x = SCREEN_WIDTH - self.x - self.width

        self.color = zone_config['color']
        self.name = zone_config['name']
        self.instrument = zone_config['instrument']
        self.hand_preference = zone_config['hand_preference']

        # Load instrument image
        try:
            self.image = pygame.image.load(image_path)
            # Resize to fit in zone (smaller than zone)
            icon_size = min(self.width, self.height) - 40
            self.image = pygame.transform.scale(self.image, (icon_size, icon_size))
        except:
            self.image = None
            print(f"[WARNING] Could not load image: {image_path}")

        # State
        self.is_active = False  # Hand is in zone
        self.is_hit = False     # Just hit
        self.hit_timer = 0      # Timer for hit flash effect

        # Visual effects
        self.glow_intensity = 0.0  # 0.0 to 1.0
        self.border_thickness = 3

    def update(self, dt: float):
        """
        Update lane state and animations

        Args:
            dt: Delta time in seconds
        """
        # Update hit flash effect
        if self.is_hit:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.is_hit = False

        # Update glow intensity based on state
        if self.is_hit:
            self.glow_intensity = 1.0
        elif self.is_active:
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 5)
        else:
            self.glow_intensity = max(0.0, self.glow_intensity - dt * 3)

    def activate(self, active: bool):
        """Set active state (hand in zone)"""
        self.is_active = active

    def trigger_hit(self):
        """Trigger hit visual effect"""
        self.is_hit = True
        self.hit_timer = 0.2  # Flash for 200ms

    def render(self, screen: pygame.Surface):
        """
        Render the lane with visual effects

        Args:
            screen: Pygame surface to draw on
        """
        # Create surface for zone
        zone_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Determine alpha based on state
        if self.is_hit:
            alpha = 200
        elif self.is_active:
            alpha = 120
        else:
            alpha = 40

        # Background fill with color and alpha
        bg_color = (*self.color, alpha)
        pygame.draw.rect(zone_surface, bg_color, (0, 0, self.width, self.height), border_radius=15)

        # Use visual_x for rendering (inverted to match flipped video)
        render_x = self.visual_x

        # Blit zone surface to screen at visual position
        screen.blit(zone_surface, (render_x, self.y))

        # Draw border
        border_alpha = int(100 + (self.glow_intensity * 155))
        border_color = (*self.color, border_alpha)

        # Create border surface
        border_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        thickness = int(self.border_thickness + self.glow_intensity * 3)
        pygame.draw.rect(border_surface, border_color, (0, 0, self.width, self.height),
                        width=thickness, border_radius=15)
        screen.blit(border_surface, (render_x, self.y))

        # Draw instrument image
        if self.image:
            img_x = render_x + (self.width - self.image.get_width()) // 2
            img_y = self.y + (self.height - self.image.get_height()) // 2 + 20
            screen.blit(self.image, (img_x, img_y))

        # Draw label
        font = pygame.font.Font(None, 32)
        text = font.render(self.name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(render_x + self.width // 2, self.y + 30))
        screen.blit(text, text_rect)

        # Glow effect when active
        if self.glow_intensity > 0.3:
            self._draw_glow(screen)

    def _draw_glow(self, screen: pygame.Surface):
        """Draw glow effect around zone"""
        glow_surface = pygame.Surface((self.width + 40, self.height + 40), pygame.SRCALPHA)

        # Multiple layers for glow
        for i in range(5):
            alpha = int(self.glow_intensity * 30 * (5 - i) / 5)
            glow_color = (*self.color, alpha)
            offset = i * 8
            pygame.draw.rect(
                glow_surface,
                glow_color,
                (offset, offset, self.width + 40 - offset * 2, self.height + 40 - offset * 2),
                width=2,
                border_radius=20
            )

        screen.blit(glow_surface, (self.visual_x - 20, self.y - 20))

    def get_rect(self) -> pygame.Rect:
        """Get pygame Rect for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_hand_collision(self, hand_bbox: dict) -> bool:
        """
        Check if hand bounding box overlaps this lane

        Args:
            hand_bbox: Dict with x, y, width, height

        Returns:
            True if hand is in this lane
        """
        lane_rect = self.get_rect()
        hand_rect = pygame.Rect(hand_bbox['x'], hand_bbox['y'],
                               hand_bbox['width'], hand_bbox['height'])

        return lane_rect.colliderect(hand_rect)


class LaneManager:
    """Manages all three lanes"""

    def __init__(self):
        """Initialize all lanes with their respective images"""
        from config.constants import IMAGE_KICK, IMAGE_SNARE, IMAGE_HIHAT

        self.lanes = []

        # Create lanes for each zone
        for zone in ZONES:
            # Map instrument to image path
            image_map = {
                'kick': IMAGE_KICK,
                'hihat': IMAGE_HIHAT,
                'snare': IMAGE_SNARE
            }

            image_path = image_map.get(zone['instrument'])
            lane = Lane(zone, image_path)
            self.lanes.append(lane)

        print(f"[OK] Created {len(self.lanes)} lanes")

    def update(self, dt: float):
        """Update all lanes"""
        for lane in self.lanes:
            lane.update(dt)

    def render(self, screen: pygame.Surface):
        """Render all lanes"""
        for lane in self.lanes:
            lane.render(screen)

    def get_lane_by_instrument(self, instrument: str) -> Lane:
        """Get lane by instrument name"""
        for lane in self.lanes:
            if lane.instrument == instrument:
                return lane
        return None

    def check_collisions(self, fingertip_positions: dict, chin_position: dict) -> dict:
        """
        Check which lanes are activated
        Hi-Hat uses chin, Kick/Snare use fingertips

        Args:
            fingertip_positions: Dict of fingertip zones {'Left': {...}, 'Right': {...}}
            chin_position: Dict with chin zone or None

        Returns:
            Dict of {instrument: label} for active lanes
        """
        active_lanes = {}

        for lane in self.lanes:
            lane_active = False

            # Hi-Hat uses chin detection
            if lane.instrument == 'hihat':
                if chin_position and lane.check_hand_collision(chin_position):
                    lane_active = True
                    active_lanes[lane.instrument] = 'Chin'

            # Kick and Snare use fingertip detection
            else:
                for hand_label, fingertip_zone in fingertip_positions.items():
                    if lane.check_hand_collision(fingertip_zone):
                        lane_active = True
                        active_lanes[lane.instrument] = hand_label
                        break

            lane.activate(lane_active)

        return active_lanes

    def check_collisions_with_velocity(self, fingertip_positions: dict, chin_position: dict,
                                       fingertip_velocities: dict, chin_velocity: float,
                                       velocity_threshold: float) -> dict:
        """
        Check which lanes are activated WITH velocity check for gesture detection.
        Prevents "idle farming" - player must MOVE FAST to hit!

        Args:
            fingertip_positions: Dict of fingertip zones
            chin_position: Dict with chin zone or None
            fingertip_velocities: Dict of fingertip velocities
            chin_velocity: Chin velocity
            velocity_threshold: Minimum speed required for valid hit

        Returns:
            Dict of {instrument: label} for active lanes
        """
        active_lanes = {}

        for lane in self.lanes:
            lane_active = False

            # Hi-Hat uses chin detection WITH velocity check
            if lane.instrument == 'hihat':
                if chin_position and lane.check_hand_collision(chin_position):
                    # Check velocity - must be moving fast enough!
                    if chin_velocity >= velocity_threshold:
                        lane_active = True
                        active_lanes[lane.instrument] = 'Chin'

            # Kick and Snare use fingertip detection WITH velocity check
            else:
                for hand_label, fingertip_zone in fingertip_positions.items():
                    if lane.check_hand_collision(fingertip_zone):
                        # Check velocity - must be moving fast enough!
                        if hand_label in fingertip_velocities and fingertip_velocities[hand_label] >= velocity_threshold:
                            lane_active = True
                            active_lanes[lane.instrument] = hand_label
                            break

            lane.activate(lane_active)

        return active_lanes
