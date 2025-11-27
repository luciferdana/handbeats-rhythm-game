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
        Simple repeating pattern: K-S-H-S (Kick-Snare-HiHat-Snare)
        Easy to follow, very predictable
        """
        beatmap = []
        pattern = ['kick', 'snare', 'hihat', 'snare']
        pattern_length = len(pattern)

        for i in range(self.total_beats):
            timestamp = i * self.beat_interval
            instrument = pattern[i % pattern_length]

            # Small variation
            if random.random() < self.variation:
                instrument = random.choice(['kick', 'snare', 'hihat'])

            beatmap.append((timestamp, instrument))

        return beatmap

    def _generate_smart_pattern(self) -> List[Tuple[float, str]]:
        """
        Smart drum pattern following typical drum rhythm
        - Kick on downbeats (1, 3)
        - Snare on backbeats (2, 4)
        - Hi-hat as filler and offbeats

        Musical and satisfying!
        """
        beatmap = []

        # 8-beat pattern (2 bars of 4/4 time)
        # K = Kick, S = Snare, H = Hi-Hat
        # Beat:  1   &   2   &   3   &   4   &
        # Note:  K   H   S   H   K   H   S   H
        base_pattern = [
            'kick',   # Beat 1 (downbeat)
            'hihat',  # & (offbeat)
            'snare',  # Beat 2 (backbeat)
            'hihat',  # &
            'kick',   # Beat 3 (downbeat)
            'hihat',  # &
            'snare',  # Beat 4 (backbeat)
            'hihat'   # &
        ]

        pattern_length = len(base_pattern)
        half_beat = self.beat_interval / 2  # For eighth notes

        beat_count = 0
        timestamp = 0

        while timestamp < self.duration:
            instrument = base_pattern[beat_count % pattern_length]

            # Add variation (substitute with different instrument)
            if random.random() < self.variation:
                # Keep the rhythmic structure but vary instruments
                if instrument == 'kick':
                    # Sometimes replace kick with hihat
                    instrument = random.choice(['kick', 'hihat'])
                elif instrument == 'snare':
                    # Sometimes replace snare with kick
                    instrument = random.choice(['snare', 'kick'])
                else:  # hihat
                    # Sometimes replace hihat with kick or snare
                    instrument = random.choice(['hihat', 'kick', 'snare'])

            beatmap.append((timestamp, instrument))

            timestamp += half_beat
            beat_count += 1

        return beatmap

    def _generate_complex_pattern(self) -> List[Tuple[float, str]]:
        """
        Complex pattern with fills, syncopation, and variations
        Challenging but still musical
        """
        beatmap = []

        # More varied pattern with fills
        # 16-beat pattern (4 bars)
        base_pattern = [
            'kick', 'hihat', 'snare', 'hihat',
            'kick', 'kick', 'snare', 'hihat',
            'kick', 'hihat', 'snare', 'hihat',
            'kick', 'snare', 'snare', 'hihat'
        ]

        pattern_length = len(base_pattern)
        half_beat = self.beat_interval / 2

        beat_count = 0
        timestamp = 0

        while timestamp < self.duration:
            instrument = base_pattern[beat_count % pattern_length]

            # Higher variation for complex mode
            if random.random() < self.variation:
                instrument = random.choice(['kick', 'snare', 'hihat'])

            # Occasionally add double notes (faster succession)
            if random.random() < 0.15:  # 15% chance
                beatmap.append((timestamp, instrument))
                timestamp += half_beat / 2  # Half the normal interval
                instrument = random.choice(['kick', 'snare', 'hihat'])

            beatmap.append((timestamp, instrument))

            timestamp += half_beat
            beat_count += 1

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
