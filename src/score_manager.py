"""
Score Manager - Scoring and Combo System
Tracks score, combo, accuracy, and statistics
"""

from typing import Dict
from config.constants import COMBO_MULTIPLIER


class ScoreManager:
    """
    Manages game score, combo system, and statistics
    """

    def __init__(self):
        """Initialize score manager"""
        self.score = 0
        self.combo = 0
        self.max_combo = 0

        # Statistics
        self.total_hits = 0
        self.perfect_count = 0
        self.good_count = 0
        self.ok_count = 0
        self.miss_count = 0

        # Current combo multiplier
        self.current_multiplier = 1.0

    def add_hit(self, hit_result):
        """
        Process a successful hit

        Args:
            hit_result: HitResult object from collision detection
        """
        if not hit_result.success:
            return

        # Increase combo
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)

        # Update statistics
        self.total_hits += 1

        if hit_result.rating == 'PERFECT':
            self.perfect_count += 1
        elif hit_result.rating == 'GOOD':
            self.good_count += 1
        elif hit_result.rating == 'OK':
            self.ok_count += 1

        # Calculate multiplier based on combo
        self.current_multiplier = self._get_combo_multiplier()

        # Add score with multiplier
        points = int(hit_result.points * self.current_multiplier)
        self.score += points

    def add_miss(self):
        """Process a miss (breaks combo)"""
        self.combo = 0
        self.miss_count += 1
        self.current_multiplier = 1.0

    def _get_combo_multiplier(self) -> float:
        """
        Calculate combo multiplier based on current combo

        Returns:
            Multiplier value (1.0 to 2.5+)
        """
        # Get highest applicable multiplier
        applicable_multiplier = 1.0

        for combo_threshold, multiplier in sorted(COMBO_MULTIPLIER.items()):
            if self.combo >= combo_threshold:
                applicable_multiplier = multiplier

        return applicable_multiplier

    def get_accuracy(self) -> float:
        """
        Calculate overall accuracy percentage

        Returns:
            Accuracy as percentage (0.0 to 100.0)
        """
        total_notes = self.total_hits + self.miss_count

        if total_notes == 0:
            return 0.0

        # Weight by hit quality
        weighted_hits = (
            self.perfect_count * 1.0 +
            self.good_count * 0.7 +
            self.ok_count * 0.4
        )

        accuracy = (weighted_hits / total_notes) * 100
        return min(100.0, accuracy)

    def get_rank(self) -> str:
        """
        Get performance rank based on accuracy

        Returns:
            Rank string: 'S', 'A', 'B', 'C', 'D'
        """
        accuracy = self.get_accuracy()

        if accuracy >= 95:
            return 'S'
        elif accuracy >= 85:
            return 'A'
        elif accuracy >= 70:
            return 'B'
        elif accuracy >= 50:
            return 'C'
        else:
            return 'D'

    def get_stats_dict(self) -> Dict:
        """
        Get all statistics as dictionary

        Returns:
            Dictionary of stats
        """
        return {
            'score': self.score,
            'combo': self.combo,
            'max_combo': self.max_combo,
            'total_hits': self.total_hits,
            'perfect': self.perfect_count,
            'good': self.good_count,
            'ok': self.ok_count,
            'miss': self.miss_count,
            'accuracy': self.get_accuracy(),
            'rank': self.get_rank(),
            'multiplier': self.current_multiplier
        }

    def reset(self):
        """Reset all scores and stats"""
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.total_hits = 0
        self.perfect_count = 0
        self.good_count = 0
        self.ok_count = 0
        self.miss_count = 0
        self.current_multiplier = 1.0

    def __str__(self):
        """String representation"""
        return f"Score: {self.score} | Combo: {self.combo}x | Accuracy: {self.get_accuracy():.1f}%"
