"""
Result Screen - End Game Statistics Display
Shows final score, accuracy, combo, and performance rank
"""

import pygame
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_BG, COLOR_WHITE, COLOR_SCORE


class ResultScreen:
    """End game result screen with statistics"""

    def __init__(self, screen: pygame.Surface):
        """
        Initialize result screen

        Args:
            screen: Pygame display surface
        """
        self.screen = screen

        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.rank_font = pygame.font.Font(None, 120)
        self.stat_font = pygame.font.Font(None, 48)
        self.label_font = pygame.font.Font(None, 36)
        self.instruction_font = pygame.font.Font(None, 32)

        # State
        self.should_retry = False
        self.should_menu = False

    def handle_events(self, events):
        """
        Handle result screen input

        Args:
            events: List of pygame events
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.should_retry = True
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    self.should_menu = True

    def render(self, score_manager, difficulty_name):
        """
        Render result screen

        Args:
            score_manager: ScoreManager instance with final stats
            difficulty_name: Name of difficulty played
        """
        # Background
        self.screen.fill(COLOR_BG)

        # Title
        title = self.title_font.render("GAME OVER", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        # Rank
        stats = score_manager.get_stats_dict()
        rank = stats['rank']
        rank_color = self._get_rank_color(rank)

        rank_text = self.rank_font.render(f"RANK: {rank}", True, rank_color)
        rank_rect = rank_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(rank_text, rank_rect)

        # Statistics
        self._render_statistics(stats, difficulty_name)

        # Instructions
        self._render_instructions()

    def _render_statistics(self, stats, difficulty_name):
        """Render detailed statistics"""
        y_start = 300
        y_spacing = 60

        # Difficulty
        self._render_stat_line("Difficulty", difficulty_name, y_start, COLOR_WHITE)

        # Score
        self._render_stat_line("Score", f"{stats['score']}", y_start + y_spacing, COLOR_SCORE)

        # Accuracy
        accuracy_color = self._get_accuracy_color(stats['accuracy'])
        self._render_stat_line("Accuracy", f"{stats['accuracy']:.1f}%", y_start + y_spacing * 2, accuracy_color)

        # Max Combo
        self._render_stat_line("Max Combo", f"{stats['max_combo']}x", y_start + y_spacing * 3, (241, 196, 15))

        # Hit breakdown
        breakdown_y = y_start + y_spacing * 4.5
        self._render_hit_breakdown(stats, breakdown_y)

    def _render_stat_line(self, label, value, y, color):
        """Render a single stat line"""
        # Label (left aligned)
        label_text = self.label_font.render(f"{label}:", True, (200, 200, 200))
        label_rect = label_text.get_rect(midright=(SCREEN_WIDTH // 2 - 20, y))
        self.screen.blit(label_text, label_rect)

        # Value (right aligned)
        value_text = self.stat_font.render(str(value), True, color)
        value_rect = value_text.get_rect(midleft=(SCREEN_WIDTH // 2 + 20, y))
        self.screen.blit(value_text, value_rect)

    def _render_hit_breakdown(self, stats, y):
        """Render hit type breakdown"""
        breakdown_font = pygame.font.Font(None, 32)

        breakdown_text = (
            f"Perfect: {stats['perfect']}  |  "
            f"Good: {stats['good']}  |  "
            f"OK: {stats['ok']}  |  "
            f"Miss: {stats['miss']}"
        )

        text = breakdown_font.render(breakdown_text, True, (180, 180, 180))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.screen.blit(text, text_rect)

    def _render_instructions(self):
        """Render bottom instructions"""
        y = SCREEN_HEIGHT - 100

        instruction_lines = [
            "Press R to Retry",
            "Press M or ESC for Menu"
        ]

        for i, line in enumerate(instruction_lines):
            text = self.instruction_font.render(line, True, (150, 150, 150))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + i * 35))
            self.screen.blit(text, text_rect)

    def _get_rank_color(self, rank):
        """Get color for rank"""
        colors = {
            'S': (255, 215, 0),      # Gold
            'A': (46, 204, 113),     # Green
            'B': (52, 152, 219),     # Blue
            'C': (241, 196, 15),     # Yellow
            'D': (231, 76, 60)       # Red
        }
        return colors.get(rank, COLOR_WHITE)

    def _get_accuracy_color(self, accuracy):
        """Get color based on accuracy"""
        if accuracy >= 95:
            return (255, 215, 0)     # Gold
        elif accuracy >= 85:
            return (46, 204, 113)    # Green
        elif accuracy >= 70:
            return (52, 152, 219)    # Blue
        elif accuracy >= 50:
            return (241, 196, 15)    # Yellow
        else:
            return (231, 76, 60)     # Red

    def should_retry_game(self):
        """Check if player wants to retry"""
        return self.should_retry

    def should_return_to_menu(self):
        """Check if player wants to return to menu"""
        return self.should_menu

    def reset(self):
        """Reset result screen state"""
        self.should_retry = False
        self.should_menu = False
