"""
Audio Manager - AUDIO PROCESSING Module
Handles: Main beat looping, instrument sound effects, audio synchronization
"""

import pygame
import os
from config.constants import AUDIO_PATH, AUDIO_MAIN_BEAT, AUDIO_KICK, AUDIO_SNARE, AUDIO_HIHAT
from config.settings import GameSettings


class AudioManager:
    """
    Manages all audio in the game
    - Main beat seamless looping
    - Instrument sound effects (kick, snare, hi-hat)
    - Hit/Miss feedback sounds
    """

    def __init__(self):
        """Initialize pygame mixer and load all sounds"""
        # Initialize audio with high quality settings
        pygame.mixer.init(
            frequency=GameSettings.AUDIO_FREQUENCY,
            size=GameSettings.AUDIO_SIZE,
            channels=GameSettings.AUDIO_CHANNELS,
            buffer=GameSettings.AUDIO_BUFFER
        )

        # Sound effects dictionary
        self.sounds = {}

        # Load all audio assets
        self._load_sounds()

        # Music state
        self.music_playing = False
        self.music_paused = False

    def _load_sounds(self):
        """
        Load all sound files
        AUDIO PROCESSING: Load and prepare audio files for playback
        """
        try:
            # Load instrument sounds as pygame.mixer.Sound objects
            # These can be played simultaneously (polyphonic)

            if os.path.exists(AUDIO_KICK):
                self.sounds['kick'] = pygame.mixer.Sound(AUDIO_KICK)
                self.sounds['kick'].set_volume(0.8)
                print(f"✓ Loaded: {AUDIO_KICK}")

            if os.path.exists(AUDIO_SNARE):
                self.sounds['snare'] = pygame.mixer.Sound(AUDIO_SNARE)
                self.sounds['snare'].set_volume(0.7)
                print(f"✓ Loaded: {AUDIO_SNARE}")

            if os.path.exists(AUDIO_HIHAT):
                self.sounds['hihat'] = pygame.mixer.Sound(AUDIO_HIHAT)
                self.sounds['hihat'].set_volume(0.6)
                print(f"✓ Loaded: {AUDIO_HIHAT}")

            # Feedback sounds (can be synthesized or simple beeps)
            # For now, we'll reuse instruments for feedback
            self.sounds['hit'] = self.sounds.get('hihat')  # Can replace with dedicated sound
            self.sounds['miss'] = None  # Can add a "thud" or error sound

            print("✓ All audio files loaded successfully")

        except Exception as e:
            print(f"⚠ Error loading sounds: {e}")

    def load_main_beat(self):
        """
        Load main background beat (9-second loop)
        AUDIO PROCESSING: Prepare main music track for seamless looping
        """
        try:
            if os.path.exists(AUDIO_MAIN_BEAT):
                pygame.mixer.music.load(AUDIO_MAIN_BEAT)
                pygame.mixer.music.set_volume(0.5)  # Background music at 50%
                print(f"✓ Main beat loaded: {AUDIO_MAIN_BEAT}")
                return True
            else:
                print(f"⚠ Main beat not found: {AUDIO_MAIN_BEAT}")
                return False
        except Exception as e:
            print(f"⚠ Error loading main beat: {e}")
            return False

    def play_main_beat(self, loops=-1):
        """
        Play main beat with seamless looping
        AUDIO PROCESSING: Continuous loop without gaps

        Args:
            loops: -1 for infinite loop, or number of loops
        """
        if not self.music_playing:
            pygame.mixer.music.play(loops)
            self.music_playing = True
            print("♪ Main beat started (looping)")

    def stop_main_beat(self):
        """Stop the main beat music"""
        pygame.mixer.music.stop()
        self.music_playing = False
        self.music_paused = False
        print("■ Main beat stopped")

    def pause_main_beat(self):
        """Pause the main beat"""
        if self.music_playing and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True

    def resume_main_beat(self):
        """Resume the main beat"""
        if self.music_playing and self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False

    def play_instrument(self, instrument: str):
        """
        Play instrument sound effect
        AUDIO PROCESSING: Layered audio playback

        Args:
            instrument: 'kick', 'snare', or 'hihat'
        """
        if instrument in self.sounds and self.sounds[instrument]:
            self.sounds[instrument].play()

    def play_hit_sound(self, hit_type: str = 'good'):
        """
        Play feedback sound for successful hit
        AUDIO PROCESSING: Audio feedback for user interaction

        Args:
            hit_type: 'perfect', 'good', or 'ok'
        """
        if 'hit' in self.sounds and self.sounds['hit']:
            # Can vary pitch/volume based on hit quality
            volume = {
                'perfect': 1.0,
                'good': 0.8,
                'ok': 0.6
            }.get(hit_type, 0.8)

            sound = self.sounds['hit']
            sound.set_volume(volume)
            sound.play()

    def play_miss_sound(self):
        """
        Play feedback sound for miss
        AUDIO PROCESSING: Negative feedback audio
        """
        if 'miss' in self.sounds and self.sounds['miss']:
            self.sounds['miss'].play()

    def set_music_volume(self, volume: float):
        """
        Set main beat volume

        Args:
            volume: 0.0 to 1.0
        """
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    def set_sfx_volume(self, volume: float):
        """
        Set sound effects volume

        Args:
            volume: 0.0 to 1.0
        """
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(max(0.0, min(1.0, volume)))

    def get_music_position(self):
        """
        Get current position in music (milliseconds)
        AUDIO PROCESSING: Audio-visual synchronization

        Returns:
            Current music position in ms
        """
        if self.music_playing:
            return pygame.mixer.music.get_pos()
        return 0

    def cleanup(self):
        """Stop all audio and cleanup"""
        self.stop_main_beat()
        pygame.mixer.quit()
        print("✓ Audio manager cleaned up")


# ===== AUDIO UTILITY FUNCTIONS =====

def seconds_to_ms(seconds: float) -> int:
    """Convert seconds to milliseconds"""
    return int(seconds * 1000)


def ms_to_seconds(milliseconds: int) -> float:
    """Convert milliseconds to seconds"""
    return milliseconds / 1000.0
