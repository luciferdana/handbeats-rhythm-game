"""
Menu Screen - Main Menu and Difficulty Selection
Clean UI for game start
"""

import pygame
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
        # Background
        self.screen.fill(COLOR_BG)

        # Title
        title = self.title_font.render("HAND BEATS", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.subtitle_font.render("Gesture Rhythm Game", True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)

        # Difficulty selection
        self._render_difficulty_options()

        # Instructions
        instructions = self.desc_font.render("Use UP/DOWN to select, ENTER to start", True, (200, 200, 200))
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
        self.screen.blit(instructions, inst_rect)

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
                # Background box for selected
                box_width = 500
                box_height = 80
                box_x = (SCREEN_WIDTH - box_width) // 2
                box_y = y - 30

                # Draw selection box
                pygame.draw.rect(
                    self.screen,
                    diff_settings['color'],
                    (box_x, box_y, box_width, box_height),
                    width=0,
                    border_radius=10
                )
                pygame.draw.rect(
                    self.screen,
                    COLOR_WHITE,
                    (box_x, box_y, box_width, box_height),
                    width=3,
                    border_radius=10
                )

                text_color = COLOR_BG
            else:
                text_color = diff_settings['color']

            # Difficulty name
            diff_text = self.option_font.render(difficulty, True, text_color if not is_selected else COLOR_BG)
            diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(diff_text, diff_rect)

            # Description
            desc_text = self.desc_font.render(diff_settings['description'], True,
                                             (200, 200, 200) if not is_selected else (50, 50, 50))
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30))
            self.screen.blit(desc_text, desc_rect)

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
