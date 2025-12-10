"""
Beatmap Generator - Smart Pattern System
AUDIO PROCESSING: Synchronizes falling objects with music beats
Creates musical drum patterns instead of random chaos
"""

import random
from typing import List, Tuple


class BeatmapGenerator:
    """
    Generates beatmaps with smart drum patterns
    Pattern types: simple, smart, complex
    """

    def __init__(self, duration: float, bpm: float = 120, pattern_type: str = 'smart', variation: float = 0.3):
        """
        Initialize beatmap generator

        Args:
            duration: Total duration in seconds
            bpm: Beats per minute
            pattern_type: 'simple', 'smart', or 'complex'
            variation: Randomization factor (0.0 to 1.0)
        """
        self.duration = duration
        self.bpm = bpm
        self.pattern_type = pattern_type
        self.variation = variation

        # Calculate beat timing
        self.beat_interval = 60.0 / bpm  # Seconds per beat
        self.total_beats = int(duration / self.beat_interval)

    def generate(self) -> List[Tuple[float, str]]:
        """
        Generate complete beatmap

        Returns:
            List of (timestamp, instrument) tuples
        """
        if self.pattern_type == 'simple':
            return self._generate_simple_pattern()
        elif self.pattern_type == 'smart':
            return self._generate_smart_pattern()
        elif self.pattern_type == 'complex':
            return self._generate_complex_pattern()
        else:
            return self._generate_smart_pattern()

    def _generate_simple_pattern(self) -> List[Tuple[float, str]]:
        """
        Simple repeating pattern: K-S-H (Kick-Snare-HiHat)
        Easy to follow, very predictable
        Uses moderate intervals (1.5-1.8 seconds)
        """
        beatmap = []
        pattern = ['kick', 'snare', 'hihat']
        pattern_length = len(pattern)

        # Use 3.5x beat intervals for comfortable spacing (1.75 seconds at 120 BPM)
        note_interval = self.beat_interval * 3.5
        num_notes = int(self.duration / note_interval)

        for i in range(num_notes):
            timestamp = i * note_interval
            instrument = pattern[i % pattern_length]

            # Small variation
            if random.random() < self.variation:
                instrument = random.choice(['kick', 'snare', 'hihat'])

            beatmap.append((timestamp, instrument))

        return beatmap

    def _generate_smart_pattern(self) -> List[Tuple[float, str]]:
        """
        Smart drum pattern following typical drum rhythm
        MEDIUM difficulty - moderate spacing (1.5 seconds)
        """
        beatmap = []

        # Simplified pattern for MEDIUM
        base_pattern = [
            'kick',
            'snare',
            'hihat',
            'kick',
            'snare',
            'hihat'
        ]

        pattern_length = len(base_pattern)
        note_interval = self.beat_interval * 3  # 1.5 seconds at 120 BPM

        num_notes = int(self.duration / note_interval)

        for i in range(num_notes):
            timestamp = i * note_interval
            instrument = base_pattern[i % pattern_length]

            # Add variation
            if random.random() < self.variation:
                instrument = random.choice(['kick', 'snare', 'hihat'])

            beatmap.append((timestamp, instrument))

        return beatmap

    def _generate_complex_pattern(self) -> List[Tuple[float, str]]:
        """
        Complex pattern - HARD difficulty
        Faster spacing (around 1 second)
        """
        beatmap = []

        # Complex pattern for HARD
        base_pattern = [
            'kick', 'snare', 'hihat',
            'kick', 'hihat', 'snare',
            'hihat', 'kick', 'snare'
        ]

        pattern_length = len(base_pattern)
        note_interval = self.beat_interval * 2  # Around 1 second at 120 BPM

        num_notes = int(self.duration / note_interval)

        for i in range(num_notes):
            timestamp = i * note_interval
            instrument = base_pattern[i % pattern_length]

            # Higher variation for complex mode
            if random.random() < self.variation:
                instrument = random.choice(['kick', 'snare', 'hihat'])

            beatmap.append((timestamp, instrument))

        return beatmap

    def get_pattern_for_loop(self, loop_duration: float = 9.0) -> List[Tuple[float, str]]:
        """
        Generate pattern for one loop of the audio
        This will be repeated throughout the game

        Args:
            loop_duration: Duration of one audio loop (default 9 seconds)

        Returns:
            Beatmap for one loop
        """
        # Temporarily set duration to loop duration
        original_duration = self.duration
        self.duration = loop_duration
        self.total_beats = int(loop_duration / self.beat_interval)

        pattern = self.generate()

        # Restore original duration
        self.duration = original_duration

        return pattern


# ===== PRESET BEATMAPS FOR 9-SECOND LOOP =====

def get_preset_beatmap_easy() -> List[Tuple[float, str]]:
    """Preset easy beatmap for 9-second loop"""
    generator = BeatmapGenerator(
        duration=9.0,
        bpm=120,
        pattern_type='simple',
        variation=0.1
    )
    return generator.generate()


def get_preset_beatmap_medium() -> List[Tuple[float, str]]:
    """Preset medium beatmap for 9-second loop"""
    generator = BeatmapGenerator(
        duration=9.0,
        bpm=120,
        pattern_type='smart',
        variation=0.3
    )
    return generator.generate()


def get_preset_beatmap_hard() -> List[Tuple[float, str]]:
    """Preset hard beatmap for 9-second loop"""
    generator = BeatmapGenerator(
        duration=9.0,
        bpm=120,
        pattern_type='complex',
        variation=0.5
    )
    return generator.generate()


# ===== UTILITY FUNCTIONS =====

def loop_beatmap(beatmap: List[Tuple[float, str]], num_loops: int, loop_duration: float) -> List[Tuple[float, str]]:
    """
    Repeat a beatmap pattern for multiple loops

    Args:
        beatmap: Original beatmap (one loop)
        num_loops: Number of times to repeat
        loop_duration: Duration of one loop in seconds

    Returns:
        Extended beatmap with all loops
    """
    extended = []

    for loop_index in range(num_loops):
        offset = loop_index * loop_duration
        for timestamp, instrument in beatmap:
            extended.append((timestamp + offset, instrument))

    return extended


def filter_beatmap_by_time(beatmap: List[Tuple[float, str]], start_time: float, end_time: float) -> List[Tuple[float, str]]:
    """Filter beatmap to only include notes within time range"""
    return [(t, i) for t, i in beatmap if start_time <= t <= end_time]
