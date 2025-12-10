"""
Game Screen - Main Game UI with Video Overlay
VIDEO PROCESSING: Renders camera feed with overlay graphics
Displays score, combo, falling objects, and hit feedback
"""

import pygame
import cv2
import numpy as np
from config.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TOPBAR_HEIGHT, TOPBAR_PADDING,
    COLOR_BG, COLOR_WHITE, COLOR_SCORE, COLOR_COMBO,
    GAME_AREA_Y, GAME_AREA_HEIGHT,
    CAMERA_OVERLAY_X, CAMERA_OVERLAY_Y,
    CAMERA_OVERLAY_WIDTH, CAMERA_OVERLAY_HEIGHT
)
from config.settings import GameSettings


class GameScreen:
    """
    Main game screen with video overlay and UI
    VIDEO PROCESSING: Combines camera feed with game graphics
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize game screen

        Args:
            screen: Pygame display surface
        """
        self.screen = screen

        # Fonts
        self.score_font = pygame.font.Font(None, 48)
        self.combo_font = pygame.font.Font(None, 56)
        self.timer_font = pygame.font.Font(None, 42)
        self.feedback_font = pygame.font.Font(None, 72)

        # Feedback display
        self.feedback_text = ""
        self.feedback_color = COLOR_WHITE
        self.feedback_timer = 0
        self.feedback_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)

    def render(self, camera_frame, score_manager, game_time, total_time, fingertip_positions=None, chin_position=None):
        """
        Render complete game screen
        VIDEO PROCESSING: Composite video and graphics

        Args:
            camera_frame: OpenCV frame from camera (BGR)
            score_manager: ScoreManager instance
            game_time: Current game time in seconds
            total_time: Total game duration
            fingertip_positions: Dict of fingertip zones
            chin_position: Dict with chin zone or None
        """
        # Background
        self.screen.fill(COLOR_BG)

        # Render camera feed as background
        # VIDEO PROCESSING: Convert camera frame to pygame surface
        if camera_frame is not None:
            self._render_camera_feed(camera_frame, fingertip_positions, chin_position)

        # Dark overlay for better UI visibility (DISABLED for full video view)
        # overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # overlay.fill((0, 0, 0, 100))  # Semi-transparent black
        # self.screen.blit(overlay, (0, 0))

        # Top bar (score, combo, timer)
        self._render_top_bar(score_manager, game_time, total_time)

        # Render feedback text (PERFECT, GOOD, MISS, etc.)
        self._render_feedback()

    def _render_camera_feed(self, frame, fingertip_positions=None, chin_position=None):
        """
        Render camera feed to screen using ASPECT FILL (ZOOM TO COVER).
        VIDEO PROCESSING: Aggressively resize and center-crop to fill entire screen.

        Args:
            frame: OpenCV BGR frame
            fingertip_positions: Dict of fingertip zones
            chin_position: Dict with chin zone or None
        """
        # VIDEO PROCESSING: Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Target dimensions (fullscreen)
        target_width = SCREEN_WIDTH   # 1280
        target_height = SCREEN_HEIGHT # 720

        # Source dimensions
        src_h, src_w = frame_rgb.shape[:2]

        if src_w == 0 or src_h == 0:
            return

        # Calculate scale ratios
        scale_w = target_width / src_w
        scale_h = target_height / src_h

        # Use max scale to ensure image covers screen
        scale = max(scale_w, scale_h)

        # Calculate new dimensions after scaling
        new_w = int(src_w * scale)
        new_h = int(src_h * scale)

        # Ensure dimensions are AT LEAST target size (add 1 pixel if needed to avoid rounding errors)
        if new_w < target_width:
            new_w = target_width
        if new_h < target_height:
            new_h = target_height

        # Resize frame with the calculated scale
        frame_resized = cv2.resize(frame_rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Center-crop: Calculate crop offsets to center the image
        crop_x = max(0, (new_w - target_width) // 2)
        crop_y = max(0, (new_h - target_height) // 2)

        # Crop to EXACT target dimensions
        frame_cropped = frame_resized[crop_y:crop_y + target_height, crop_x:crop_x + target_width]

        # Ensure output is EXACTLY the target size
        actual_h, actual_w = frame_cropped.shape[:2]
        if actual_w != target_width or actual_h != target_height:
            frame_cropped = cv2.resize(frame_cropped, (target_width, target_height), interpolation=cv2.INTER_LINEAR)

        # Convert to pygame surface
        frame_transposed = np.transpose(frame_cropped, (1, 0, 2))
        frame_surface = pygame.surfarray.make_surface(frame_transposed)

        # Apply alpha/brightness if needed
        if GameSettings.CAMERA_ALPHA < 1.0:
            frame_surface.set_alpha(int(255 * GameSettings.CAMERA_ALPHA))

        # Blit to screen at (0, 0) for fullscreen camera
        self.screen.blit(frame_surface, (0, 0))

        # Draw fingertip indicators (for Kick and Snare)
        if fingertip_positions:
            self._draw_fingertip_indicators(fingertip_positions)

        # Draw chin indicator (for Hi-Hat)
        if chin_position:
            self._draw_chin_indicator(chin_position)

    def _draw_fingertip_indicators(self, fingertip_zones):
        """
        Draw fingertip detection indicators

        Args:
            fingertip_zones: Dict of fingertip zones from hand tracker
        """
        for hand_label, zone in fingertip_zones.items():
            center_x = zone['center_x']
            center_y = zone['center_y']

            # Color based on hand
            color = (74, 144, 226) if hand_label == 'Left' else (255, 107, 53)

            # Draw outer circle (detection zone)
            pygame.draw.circle(self.screen, color, (center_x, center_y), 20, 3)

            # Draw inner dot (exact fingertip position)
            pygame.draw.circle(self.screen, color, (center_x, center_y), 5, -1)

    def _draw_chin_indicator(self, chin_zone):
        """
        Draw chin detection indicator (for Hi-Hat)

        Args:
            chin_zone: Dict with chin position
        """
        center_x = chin_zone['center_x']
        center_y = chin_zone['center_y']

        # Gold/Yellow color for chin (Hi-Hat color)
        color = (255, 215, 0)

        # Draw larger outer circle for chin
        pygame.draw.circle(self.screen, color, (center_x, center_y), 25, 4)

        # Draw inner dot
        pygame.draw.circle(self.screen, color, (center_x, center_y), 6, -1)

        # Draw label
        font = pygame.font.Font(None, 20)
        label = font.render("CHIN", True, color)
        label_rect = label.get_rect(center=(center_x, center_y - 35))
        self.screen.blit(label, label_rect)

    def _draw_hand_bboxes(self, hand_bboxes):
        """
        Draw hand bounding boxes on screen (legacy, for debugging)
        IMAGE PROCESSING: Visual feedback overlay

        Args:
            hand_bboxes: Dict of hand bounding boxes in screen coordinates
        """
        for hand_label, bbox in hand_bboxes.items():
            x = bbox['x']
            y = bbox['y']
            w = bbox['width']
            h = bbox['height']

            # Color based on hand
            color = (0, 255, 0) if hand_label == 'Left' else (255, 100, 0)

            # Draw rectangle
            pygame.draw.rect(
                self.screen,
                color,
                (x, y, w, h),
                width=GameSettings.HAND_BBOX_THICKNESS
            )

            # Draw label
            font = pygame.font.Font(None, 24)
            label = font.render(hand_label, True, color)
            self.screen.blit(label, (x, y - 25))

    def _render_top_bar(self, score_manager, game_time, total_time):
        """
        Render top bar with score, combo, and timer

        Args:
            score_manager: ScoreManager instance
            game_time: Current time in seconds
            total_time: Total duration in seconds
        """
        # No background for top bar - full video visibility

        # Score (left)
        score_text = self.score_font.render(f"Score: {score_manager.score}", True, COLOR_SCORE)
        self.screen.blit(score_text, (TOPBAR_PADDING, TOPBAR_PADDING))

        # Combo (center)
        combo_color = COLOR_COMBO if score_manager.combo > 0 else (100, 100, 100)
        combo_text = self.combo_font.render(f"{score_manager.combo}x", True, combo_color)
        combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH // 2, TOPBAR_HEIGHT // 2))
        self.screen.blit(combo_text, combo_rect)

        # Multiplier indicator
        if score_manager.current_multiplier > 1.0:
            mult_font = pygame.font.Font(None, 24)
            mult_text = mult_font.render(f"x{score_manager.current_multiplier:.1f}", True, COLOR_COMBO)
            mult_rect = mult_text.get_rect(center=(SCREEN_WIDTH // 2, TOPBAR_HEIGHT - 15))
            self.screen.blit(mult_text, mult_rect)

        # Timer (right)
        remaining_time = max(0, total_time - game_time)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        timer_text = self.timer_font.render(f"{minutes}:{seconds:02d}", True, COLOR_WHITE)
        timer_rect = timer_text.get_rect(topright=(SCREEN_WIDTH - TOPBAR_PADDING, TOPBAR_PADDING))
        self.screen.blit(timer_text, timer_rect)

    def show_feedback(self, text: str, color: tuple, position=None):
        """
        Show hit feedback text (PERFECT, GOOD, MISS, etc.)

        Args:
            text: Feedback text
            color: Text color (RGB tuple)
            position: Optional custom position
        """
        self.feedback_text = text
        self.feedback_color = color
        self.feedback_timer = 0.5  # Show for 500ms

        if position:
            self.feedback_position = position

    def _render_feedback(self):
        """Render feedback text with fade out"""
        if self.feedback_timer > 0:
            # Calculate alpha based on timer (fade out)
            alpha = int(255 * min(1.0, self.feedback_timer * 2))

            # Render text
            feedback_surface = self.feedback_font.render(self.feedback_text, True, self.feedback_color)
            feedback_surface.set_alpha(alpha)

            # Center on screen
            feedback_rect = feedback_surface.get_rect(center=self.feedback_position)
            self.screen.blit(feedback_surface, feedback_rect)

    def update(self, dt: float):
        """
        Update screen animations

        Args:
            dt: Delta time in seconds
        """
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

    def render_countdown(self, count: int):
        """
        Render countdown before game starts

        Args:
            count: Countdown number (3, 2, 1)
        """
        self.screen.fill(COLOR_BG)

        # Countdown text
        countdown_font = pygame.font.Font(None, 200)
        text = countdown_font.render(str(count), True, COLOR_WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # "Get Ready!" text
        ready_font = pygame.font.Font(None, 48)
        ready_text = ready_font.render("Get Ready!", True, (200, 200, 200))
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        self.screen.blit(ready_text, ready_rect)
