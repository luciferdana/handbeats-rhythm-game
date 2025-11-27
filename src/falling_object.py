"""
Falling Object - Rhythm Notes
Represents the falling instrument notes that players must hit
Synchronized with audio beats
"""

import pygame
from typing import Tuple
from config.constants import (
    OBJECT_SIZE,
    OBJECT_SPAWN_Y,
    OBJECT_TARGET_Y,
    TRACK_POSITIONS,
    IMAGE_KICK,
    IMAGE_SNARE,
    IMAGE_HIHAT
)


class FallingObject:
    """
    A falling note/object that players must hit
    Moves from top to bottom at constant speed
    """

    def __init__(self, instrument: str, spawn_time: float, falling_speed: float):
        """
        Initialize falling object

        Args:
            instrument: 'kick', 'snare', or 'hihat'
            spawn_time: Game time when object should spawn
            falling_speed: Pixels per frame
        """
        self.instrument = instrument
        self.spawn_time = spawn_time
        self.falling_speed = falling_speed

        # Position
        self.x = TRACK_POSITIONS[instrument]
        self.y = OBJECT_SPAWN_Y
        self.size = OBJECT_SIZE

        # State
        self.is_spawned = False
        self.is_hit = False
        self.is_missed = False
        self.is_dead = False  # Should be removed

        # Load image
        image_map = {
            'kick': IMAGE_KICK,
            'snare': IMAGE_SNARE,
            'hihat': IMAGE_HIHAT
        }

        try:
            self.image = pygame.image.load(image_map[instrument])
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except:
            self.image = None
            print(f"⚠ Could not load image for {instrument}")

        # Visual effects
        self.alpha = 255
        self.scale = 1.0

    def update(self, dt: float, current_time: float):
        """
        Update object position and state

        Args:
            dt: Delta time in seconds
            current_time: Current game time in seconds
        """
        # Check if should spawn
        if not self.is_spawned and current_time >= self.spawn_time:
            self.is_spawned = True

        # Only update if spawned and not dead
        if self.is_spawned and not self.is_dead:
            # Move downward
            self.y += self.falling_speed

            # Check if missed (passed target zone)
            if self.y > OBJECT_TARGET_Y + 100 and not self.is_hit:
                self.is_missed = True
                self.is_dead = True

            # Fade out if hit
            if self.is_hit:
                self.alpha = max(0, self.alpha - 15)
                self.scale += 0.05
                if self.alpha <= 0:
                    self.is_dead = True

    def render(self, screen: pygame.Surface):
        """
        Render the falling object

        Args:
            screen: Pygame surface to draw on
        """
        if not self.is_spawned or self.is_dead:
            return

        if self.image:
            # Apply visual effects (scale, alpha)
            scaled_size = int(self.size * self.scale)
            scaled_image = pygame.transform.scale(self.image, (scaled_size, scaled_size))

            # Apply alpha
            scaled_image.set_alpha(self.alpha)

            # Center the scaled image
            draw_x = self.x + (self.size - scaled_size) // 2
            draw_y = self.y + (self.size - scaled_size) // 2

            screen.blit(scaled_image, (draw_x, draw_y))
        else:
            # Fallback: draw colored circle
            color_map = {
                'kick': (74, 144, 226),
                'snare': (255, 107, 53),
                'hihat': (255, 215, 0)
            }
            color = color_map.get(self.instrument, (255, 255, 255))

            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            pygame.draw.circle(screen, color, (center_x, center_y), self.size // 2)

    def get_rect(self) -> pygame.Rect:
        """Get bounding box for collision detection"""
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def mark_hit(self):
        """Mark object as hit"""
        self.is_hit = True

    def mark_missed(self):
        """Mark object as missed"""
        self.is_missed = True
        self.is_dead = True

    def get_distance_from_target(self) -> float:
        """
        Get vertical distance from target zone (for timing accuracy)

        Returns:
            Distance in pixels (negative = before target, positive = after)
        """
        return self.y - OBJECT_TARGET_Y

    def is_in_hit_window(self, window_distance: float) -> bool:
        """
        Check if object is within hit window

        Args:
            window_distance: Allowed distance in pixels

        Returns:
            True if within hit window
        """
        distance = abs(self.get_distance_from_target())
        return distance <= window_distance


class FallingObjectManager:
    """Manages all falling objects in the game"""

    def __init__(self, beatmap: list, falling_speed: float):
        """
        Initialize falling object manager

        Args:
            beatmap: List of (timestamp, instrument) tuples
            falling_speed: Falling speed in pixels per frame
        """
        self.beatmap = beatmap
        self.falling_speed = falling_speed
        self.objects = []

        # Create all objects (they will spawn at their designated time)
        for spawn_time, instrument in beatmap:
            obj = FallingObject(instrument, spawn_time, falling_speed)
            self.objects.append(obj)

        print(f"✓ Created {len(self.objects)} falling objects from beatmap")

    def update(self, dt: float, current_time: float):
        """
        Update all falling objects

        Args:
            dt: Delta time in seconds
            current_time: Current game time in seconds
        """
        for obj in self.objects:
            obj.update(dt, current_time)

        # Remove dead objects
        self.objects = [obj for obj in self.objects if not obj.is_dead]

    def render(self, screen: pygame.Surface):
        """Render all visible objects"""
        for obj in self.objects:
            obj.render(screen)

    def get_active_objects(self) -> list:
        """Get all spawned, non-dead objects"""
        return [obj for obj in self.objects if obj.is_spawned and not obj.is_dead and not obj.is_hit]

    def get_objects_in_hit_zone(self) -> list:
        """Get objects currently in the hit zone"""
        hit_zone_objects = []
        for obj in self.get_active_objects():
            # Within reasonable range of target
            if abs(obj.get_distance_from_target()) < 150:
                hit_zone_objects.append(obj)
        return hit_zone_objects

    def get_object_by_instrument_in_zone(self, instrument: str) -> FallingObject:
        """
        Get the closest object of a specific instrument in hit zone

        Args:
            instrument: 'kick', 'snare', or 'hihat'

        Returns:
            Closest matching object, or None
        """
        matching_objects = [obj for obj in self.get_objects_in_hit_zone()
                          if obj.instrument == instrument]

        if not matching_objects:
            return None

        # Return the one closest to target
        return min(matching_objects, key=lambda obj: abs(obj.get_distance_from_target()))

    def count_total_objects(self) -> int:
        """Get total number of objects (for stats)"""
        return len(self.beatmap)

    def count_remaining_objects(self) -> int:
        """Get number of objects still alive"""
        return len(self.objects)
