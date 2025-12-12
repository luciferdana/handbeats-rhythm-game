"""
Menu Screen - Main Menu and Difficulty Selection
Clean UI for game start
"""

import pygame
import os
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WHITE
from config.settings import DifficultySettings


class MenuScreen:
    """Main menu with difficulty selection"""

    def __init__(self, screen: pygame.Surface):
        """
        Initialize menu screen

        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.selected_difficulty = 'MEDIUM'

        # Menu options
        self.difficulties = ['EASY', 'MEDIUM', 'HARD']
        self.current_selection = 1  # Start at MEDIUM

        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.option_font = pygame.font.Font(None, 48)
        self.desc_font = pygame.font.Font(None, 28)

        # Menu state
        self.should_start = False

        # Load menu background image
        menu_image_path = os.path.join('assets', 'image', 'menu.png')
        try:
            self.background_image = pygame.image.load(menu_image_path)
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print(f"Could not load menu background: {menu_image_path}")
            self.background_image = None

    def handle_events(self, events):
        """
        Handle menu input events

        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.current_selection = max(0, self.current_selection - 1)
                elif event.key == pygame.K_DOWN:
                    self.current_selection = min(len(self.difficulties) - 1, self.current_selection + 1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.selected_difficulty = self.difficulties[self.current_selection]
                    self.should_start = True

    def update(self, dt: float):
        """Update menu (animations, etc.)"""
        pass

    def render(self):
        """Render menu screen"""
        # Background - use image if available, otherwise fill with color
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(COLOR_BG)

        # Semi-transparent dark overlay for better text visibility
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        # Title with shadow
        self._draw_text_with_shadow("HAND BEATS", self.title_font, COLOR_WHITE, (SCREEN_WIDTH // 2, 120), shadow_offset=4)

        # Subtitle with shadow
        self._draw_text_with_shadow("Gesture Rhythm Game", self.subtitle_font, (200, 200, 200), (SCREEN_WIDTH // 2, 180), shadow_offset=2)

        # Difficulty selection
        self._render_difficulty_options()

        # Instructions with shadow
        self._draw_text_with_shadow("Use UP/DOWN to select, ENTER to start", self.desc_font, (220, 220, 220), (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), shadow_offset=2)

    def _render_difficulty_options(self):
        """Render difficulty options"""
        y_start = 300
        y_spacing = 100

        for i, difficulty in enumerate(self.difficulties):
            y = y_start + i * y_spacing

            # Get difficulty settings
            diff_settings = DifficultySettings.get_difficulty(difficulty)

            # Highlight selected
            is_selected = (i == self.current_selection)

            if is_selected:
                # Background box for selected with stronger opacity
                box_width = 520
                box_height = 85
                box_x = (SCREEN_WIDTH - box_width) // 2
                box_y = y - 33

                # Shadow box
                shadow_box = pygame.Surface((box_width + 10, box_height + 10), pygame.SRCALPHA)
                shadow_box.fill((0, 0, 0, 100))
                self.screen.blit(shadow_box, (box_x - 5, box_y - 5))

                # Draw selection box with opacity
                box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                box_surface.fill((*diff_settings['color'], 220))
                self.screen.blit(box_surface, (box_x, box_y))

                # Border
                pygame.draw.rect(
                    self.screen,
                    COLOR_WHITE,
                    (box_x, box_y, box_width, box_height),
                    width=4,
                    border_radius=12
                )

                text_color = COLOR_WHITE
                desc_color = (255, 255, 255)
            else:
                # Add semi-transparent background for unselected options
                box_width = 480
                box_height = 75
                box_x = (SCREEN_WIDTH - box_width) // 2
                box_y = y - 28

                # Darker and more opaque background for better visibility
                box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                box_surface.fill((0, 0, 0, 200))  # More opaque black
                self.screen.blit(box_surface, (box_x, box_y))

                # Add subtle border for unselected
                pygame.draw.rect(
                    self.screen,
                    (60, 60, 60),  # Dark gray border
                    (box_x, box_y, box_width, box_height),
                    width=2,
                    border_radius=10
                )

                text_color = (255, 255, 255)  # White text for better contrast
                desc_color = (200, 200, 200)  # Lighter description

            # Difficulty name with shadow
            self._draw_text_with_shadow(difficulty, self.option_font, text_color, (SCREEN_WIDTH // 2, y), shadow_offset=3)

            # Description with shadow
            self._draw_text_with_shadow(diff_settings['description'], self.desc_font, desc_color, (SCREEN_WIDTH // 2, y + 30), shadow_offset=2)

    def _draw_text_with_shadow(self, text, font, color, position, shadow_offset=2):
        """
        Draw text with shadow for better readability

        Args:
            text: Text to render
            font: Pygame font object
            color: Text color (RGB tuple)
            position: (x, y) center position
            shadow_offset: Pixel offset for shadow
        """
        # Draw shadow (black)
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(position[0] + shadow_offset, position[1] + shadow_offset))
        self.screen.blit(shadow, shadow_rect)

        # Draw main text
        main_text = font.render(text, True, color)
        main_rect = main_text.get_rect(center=position)
        self.screen.blit(main_text, main_rect)

    def get_selected_difficulty(self):
        """Get selected difficulty settings"""
        return DifficultySettings.get_difficulty(self.selected_difficulty)

    def should_start_game(self):
        """Check if should start game"""
        return self.should_start

    def reset(self):
        """Reset menu state"""
        self.should_start = False
        self.current_selection = 1
