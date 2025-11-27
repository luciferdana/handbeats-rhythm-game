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

    def render(self, camera_frame, score_manager, game_time, total_time, hand_bboxes=None):
        """
        Render complete game screen
        VIDEO PROCESSING: Composite video and graphics

        Args:
            camera_frame: OpenCV frame from camera (BGR)
            score_manager: ScoreManager instance
            game_time: Current game time in seconds
            total_time: Total game duration
            hand_bboxes: Optional dict of hand bounding boxes
        """
        # Background
        self.screen.fill(COLOR_BG)

        # Render camera feed as background
        # VIDEO PROCESSING: Convert camera frame to pygame surface
        if camera_frame is not None:
            self._render_camera_feed(camera_frame, hand_bboxes)

        # Dark overlay for better UI visibility
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Top bar (score, combo, timer)
        self._render_top_bar(score_manager, game_time, total_time)

        # Render feedback text (PERFECT, GOOD, MISS, etc.)
        self._render_feedback()

    def _render_camera_feed(self, frame, hand_bboxes=None):
        """
        Render camera feed to screen
        VIDEO PROCESSING: Convert OpenCV BGR to Pygame surface

        Args:
            frame: OpenCV BGR frame
            hand_bboxes: Optional hand bounding boxes (already in screen coordinates)
        """
        # VIDEO PROCESSING: Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize to fit screen if needed
        frame_resized = cv2.resize(frame_rgb, (SCREEN_WIDTH, SCREEN_HEIGHT - TOPBAR_HEIGHT))

        # VIDEO PROCESSING: Convert to pygame surface
        # Rotate and transpose for proper orientation
        frame_surface = pygame.surfarray.make_surface(np.rot90(frame_resized))

        # Apply alpha/brightness if needed
        if GameSettings.CAMERA_ALPHA < 1.0:
            frame_surface.set_alpha(int(255 * GameSettings.CAMERA_ALPHA))

        # Blit to screen
        self.screen.blit(frame_surface, (0, TOPBAR_HEIGHT))

        # Draw hand bounding boxes if provided
        if hand_bboxes and GameSettings.SHOW_HAND_BBOX:
            self._draw_hand_bboxes(hand_bboxes)

    def _draw_hand_bboxes(self, hand_bboxes):
        """
        Draw hand bounding boxes on screen
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
        # Background for top bar
        top_bar_bg = pygame.Surface((SCREEN_WIDTH, TOPBAR_HEIGHT), pygame.SRCALPHA)
        top_bar_bg.fill((0, 0, 0, 200))  # Dark semi-transparent
        self.screen.blit(top_bar_bg, (0, 0))

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
