"""
Game Constants - Colors, Positions, Zones
For Multimedia Processing: Image/Video Overlay Configuration
"""

# ===== SCREEN CONFIGURATION =====
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# ===== CAMERA CONFIGURATION (VIDEO PROCESSING) =====
# HD Resolution for better video quality
CAMERA_WIDTH = 1280   # HD 720p width
CAMERA_HEIGHT = 720   # HD 720p height
CAMERA_FLIP_HORIZONTAL = True

# Alternative resolutions (uncomment if needed):
# Full HD 1080p: CAMERA_WIDTH = 1920, CAMERA_HEIGHT = 1080
# 4K: CAMERA_WIDTH = 3840, CAMERA_HEIGHT = 2160

# ===== COLOR PALETTE =====
# Background
COLOR_BG = (13, 13, 13)  # Dark black
COLOR_BG_OVERLAY = (0, 0, 0, 180)  # Semi-transparent overlay

# Instrument Colors (matching asset images)
COLOR_KICK = (74, 144, 226)      # Blue
COLOR_HIHAT = (255, 215, 0)      # Gold/Yellow
COLOR_SNARE = (255, 107, 53)     # Orange

# UI Colors
COLOR_WHITE = (255, 255, 255)
COLOR_TEXT = (240, 240, 240)
COLOR_SCORE = (100, 255, 100)

# Feedback Colors
COLOR_PERFECT = (46, 204, 113)   # Green
COLOR_GOOD = (52, 152, 219)      # Blue
COLOR_MISS = (231, 76, 60)       # Red
COLOR_COMBO = (241, 196, 15)     # Yellow

# Zone Active/Inactive Colors
COLOR_ZONE_INACTIVE = (255, 255, 255, 50)   # Very transparent
COLOR_ZONE_ACTIVE = (255, 255, 255, 150)    # Bright when active
COLOR_ZONE_HIT = (255, 255, 255, 255)       # Full brightness on hit

# ===== LANE/ZONE POSITIONS (IMAGE PROCESSING - Detection Areas) =====
# These are the target zones where hands must be placed
ZONE_WIDTH = 160
ZONE_HEIGHT = 110
ZONE_Y_SIDE = 400  # Side zones (hands) - comfortable hand position
ZONE_Y_CENTER = 280  # Center zone (chest/dada) - nod down slightly

# Left Zone (KICK) - Collision at left (for inverted coords)
KICK_ZONE = {
    'x': 1010,
    'y': ZONE_Y_SIDE,
    'width': ZONE_WIDTH,
    'height': ZONE_HEIGHT,
    'color': COLOR_KICK,
    'name': 'KICK',
    'instrument': 'kick',
    'hand_preference': 'Left'
}

# Center Zone (HI-HAT) - Center
HIHAT_ZONE = {
    'x': 530,
    'y': ZONE_Y_CENTER,
    'width': ZONE_WIDTH,
    'height': ZONE_HEIGHT,
    'color': COLOR_HIHAT,
    'name': 'HI-HAT',
    'instrument': 'hihat',
    'hand_preference': 'chin'
}

# Right Zone (SNARE) - Collision at right (for inverted coords)
SNARE_ZONE = {
    'x': 50,
    'y': ZONE_Y_SIDE,
    'width': ZONE_WIDTH,
    'height': ZONE_HEIGHT,
    'color': COLOR_SNARE,
    'name': 'SNARE',
    'instrument': 'snare',
    'hand_preference': 'Right'
}

# All zones list
ZONES = [KICK_ZONE, HIHAT_ZONE, SNARE_ZONE]

# ===== FALLING OBJECT CONFIGURATION =====
OBJECT_SIZE = 80  # Size of falling note images
OBJECT_SPAWN_Y = -100  # Spawn above screen

# Target Y positions for each instrument (matching their zones)
OBJECT_TARGET_Y_SIDE = ZONE_Y_SIDE - 20  # For kick and snare
OBJECT_TARGET_Y_CENTER = ZONE_Y_CENTER - 20  # For hihat (higher)

# Falling track positions (centered above each zone)
KICK_TRACK_X = KICK_ZONE['x'] + (ZONE_WIDTH - OBJECT_SIZE) // 2
HIHAT_TRACK_X = HIHAT_ZONE['x'] + (ZONE_WIDTH - OBJECT_SIZE) // 2
SNARE_TRACK_X = SNARE_ZONE['x'] + (ZONE_WIDTH - OBJECT_SIZE) // 2

TRACK_POSITIONS = {
    'kick': KICK_TRACK_X,
    'hihat': HIHAT_TRACK_X,
    'snare': SNARE_TRACK_X
}

# Target Y positions per instrument
TARGET_Y_POSITIONS = {
    'kick': OBJECT_TARGET_Y_SIDE,
    'hihat': OBJECT_TARGET_Y_CENTER,
    'snare': OBJECT_TARGET_Y_SIDE
}


# Hit detection Y range (vertical tolerance)
# Using side target as reference (most common)
HIT_ZONE_TOP = OBJECT_TARGET_Y_SIDE - 50
HIT_ZONE_BOTTOM = OBJECT_TARGET_Y_SIDE + 50

# ===== SCORING SYSTEM =====
SCORE_PERFECT = 100
SCORE_GOOD = 50
SCORE_OK = 25
SCORE_MISS = 0

COMBO_MULTIPLIER = {
    10: 1.2,   # 10 combo = 1.2x
    20: 1.5,   # 20 combo = 1.5x
    30: 2.0,   # 30 combo = 2.0x
    50: 2.5    # 50 combo = 2.5x
}

# ===== UI LAYOUT =====
# Top bar (score, combo, timer)
TOPBAR_HEIGHT = 80
TOPBAR_PADDING = 20

# Game area (falling objects)
GAME_AREA_Y = TOPBAR_HEIGHT
GAME_AREA_HEIGHT = ZONE_Y_SIDE - TOPBAR_HEIGHT

# Camera feed overlay position
CAMERA_OVERLAY_X = 0
CAMERA_OVERLAY_Y = GAME_AREA_Y
CAMERA_OVERLAY_WIDTH = SCREEN_WIDTH
CAMERA_OVERLAY_HEIGHT = SCREEN_HEIGHT - TOPBAR_HEIGHT

# ===== VISUAL EFFECTS =====
GLOW_RADIUS = 20
PARTICLE_COUNT = 10
SHAKE_INTENSITY = 5

# ===== ASSET PATHS =====
ASSET_PATH = "assets"
IMAGE_PATH = f"{ASSET_PATH}/image"
AUDIO_PATH = f"{ASSET_PATH}/audio"

# Image assets
IMAGE_KICK = f"{IMAGE_PATH}/kick.png"
IMAGE_SNARE = f"{IMAGE_PATH}/snare.PNG"
IMAGE_HIHAT = f"{IMAGE_PATH}/hi-hat.PNG"

# Audio assets
AUDIO_MAIN_BEAT = f"{AUDIO_PATH}/main.mp3"
AUDIO_KICK = f"{AUDIO_PATH}/kick.wav"
AUDIO_SNARE = f"{AUDIO_PATH}/snare-drum-341273.mp3"
AUDIO_HIHAT = f"{AUDIO_PATH}/open-hi-hat-431740.mp3"

# ===== MEDIAPIPE HAND DETECTION SETTINGS (IMAGE PROCESSING) =====
HAND_DETECTION_CONFIDENCE = 0.7
HAND_TRACKING_CONFIDENCE = 0.5
MAX_HANDS = 2

# Hand landmark indices for bounding box calculation
HAND_BBOX_PADDING = 20  # Pixels to expand bounding box
