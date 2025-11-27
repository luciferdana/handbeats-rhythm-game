"""
Difficulty Settings & Game Configurations
Multimedia Processing: Speed, Timing, Pattern Complexity
"""

class DifficultySettings:
    """
    Difficulty configurations for Easy, Medium, Hard modes
    Affects: falling speed, spawn rate, timing windows, pattern complexity
    """

    EASY = {
        'name': 'EASY',
        'falling_speed': 3.5,           # Pixels per frame (slower)
        'spawn_interval': 0.6,          # Seconds between spawns
        'pattern_type': 'simple',       # Simple repeating pattern
        'pattern_variation': 0.1,       # 10% random variation
        'perfect_window': 100,          # ±100ms for PERFECT
        'good_window': 180,             # ±180ms for GOOD
        'ok_window': 280,               # ±280ms for OK
        'description': 'Relaxed pace, predictable patterns',
        'color': (46, 204, 113)         # Green
    }

    MEDIUM = {
        'name': 'MEDIUM',
        'falling_speed': 5.5,           # Moderate speed
        'spawn_interval': 0.4,          # Faster spawns
        'pattern_type': 'smart',        # Smart drum patterns
        'pattern_variation': 0.3,       # 30% variation
        'perfect_window': 80,           # ±80ms for PERFECT
        'good_window': 150,             # ±150ms for GOOD
        'ok_window': 230,               # ±230ms for OK
        'description': 'Moderate challenge, musical patterns',
        'color': (52, 152, 219)         # Blue
    }

    HARD = {
        'name': 'HARD',
        'falling_speed': 7.5,           # Fast!
        'spawn_interval': 0.3,          # Very fast spawns
        'pattern_type': 'complex',      # Complex patterns
        'pattern_variation': 0.5,       # 50% variation
        'perfect_window': 60,           # ±60ms for PERFECT (tight!)
        'good_window': 120,             # ±120ms for GOOD
        'ok_window': 180,               # ±180ms for OK
        'description': 'Fast pace, unpredictable patterns',
        'color': (231, 76, 60)          # Red
    }

    @staticmethod
    def get_difficulty(level='MEDIUM'):
        """Get difficulty settings by level name"""
        if level == 'EASY':
            return DifficultySettings.EASY
        elif level == 'MEDIUM':
            return DifficultySettings.MEDIUM
        elif level == 'HARD':
            return DifficultySettings.HARD
        else:
            return DifficultySettings.MEDIUM


class GameSettings:
    """General game settings"""

    # Game duration
    GAME_DURATION = 60  # seconds (will loop 9-second beat ~6-7 times)

    # Audio settings (AUDIO PROCESSING)
    AUDIO_FREQUENCY = 44100
    AUDIO_SIZE = -16
    AUDIO_CHANNELS = 2
    AUDIO_BUFFER = 512

    # Main beat loop (9 seconds)
    BEAT_DURATION = 9.0
    BEAT_BPM = 120  # Approximate BPM

    # Visual effects
    ENABLE_PARTICLES = True
    ENABLE_GLOW = True
    ENABLE_SCREEN_SHAKE = True

    # Hand tracking (IMAGE PROCESSING)
    SHOW_HAND_LANDMARKS = False  # Show MediaPipe skeleton
    SHOW_HAND_BBOX = True        # Show bounding boxes
    HAND_BBOX_COLOR = (0, 255, 0)  # Green
    HAND_BBOX_THICKNESS = 3

    # Camera feed (VIDEO PROCESSING)
    CAMERA_ALPHA = 0.6           # Transparency of camera overlay
    CAMERA_BLUR = False          # Blur background slightly
    CAMERA_BRIGHTNESS = 1.0      # Brightness adjustment

    # Debug mode
    DEBUG_MODE = False           # Show FPS, hitboxes, etc.
    SHOW_FPS = True


class CalibrationSettings:
    """Settings for hand detection calibration"""

    CALIBRATION_TIME = 3.0  # Seconds to verify hands
    MIN_HAND_SIZE = 50      # Minimum hand bounding box size (pixels)
    MAX_HAND_SIZE = 400     # Maximum hand bounding box size

    # Required hand positions for calibration
    REQUIRE_BOTH_HANDS = True
    REQUIRE_LEFT_HAND = True
    REQUIRE_RIGHT_HAND = True
