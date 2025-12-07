# HandBeats: Gesture Rhythm Game
Tugas Besar Sistem / Teknologi Multimedia - IF25-40305

## Deskripsi Project
HandBeats adalah game interaktif berbasis kamera yang menampilkan bounding box instrumen musik seperti "Kick", "Snare", dan "Hi-Hat" di layar. Pemain harus mengetuk area tersebut menggunakan gesture tangan tepat waktu mengikuti irama musik. Sistem mendeteksi pergerakan tangan dengan MediaPipe Hands, dan jika posisi serta timing sesuai, maka akan muncul suara beat, efek visual, serta peningkatan skor.

## Anggota Kelompok
- Ferdana Al-Hakim 

## Komponen Multimedia

### 1. IMAGE PROCESSING
- **MediaPipe Hands**: Deteksi dan tracking tangan real-time
- **Bounding Box Detection**: Kalkulasi posisi tangan dalam koordinat layar
- **Collision Detection**: Deteksi overlap antara tangan dan target zone
- **Hand Landmark Visualization**: Overlay skeleton tangan pada video

### 2. VIDEO PROCESSING
- **Real-time Camera Capture**: OpenCV untuk capture video dari webcam
- **Frame Processing**: Konversi BGR to RGB, flipping, resizing
- **Video Overlay**: Composite video feed dengan game graphics
- **Visual Effects**: Glow effects, particle effects, screen shake

### 3. AUDIO PROCESSING
- **Seamless Music Looping**: Loop musik utama 9 detik tanpa jeda
- **Sound Effects**: Instrument sounds (kick, snare, hi-hat)
- **Audio Synchronization**: Sinkronisasi falling objects dengan beat
- **Layered Audio**: Polyphonic playback untuk multiple sounds

## Fitur Game

### Difficulty Levels
- **EASY**: Slower falling speed, simple patterns, forgiving timing
- **MEDIUM**: Moderate speed, smart drum patterns, balanced timing
- **HARD**: Fast speed, complex patterns, tight timing windows

### Scoring System
- **PERFECT**: ±60-100ms timing window (100 points)
- **GOOD**: ±100-180ms timing window (50 points)
- **OK**: ±180-280ms timing window (25 points)
- **MISS**: Outside timing window (0 points)
- **Combo Multiplier**: 10x = 1.2x, 20x = 1.5x, 30x = 2.0x, 50x = 2.5x

### Pattern System
- **Simple Pattern**: K-S-H-S repeating (Easy)
- **Smart Pattern**: Drum-like rhythm dengan variasi (Medium)
- **Complex Pattern**: Advanced drum fills dan syncopation (Hard)

## Struktur Project

```
handbeats-rhythm-game/
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md
│
├── config/                  # Game configuration
│   ├── constants.py         # Colors, zones, paths
│   ├── settings.py          # Difficulty settings
│   └── beatmap.py           # Pattern generator
│
├── src/                     # Core game logic
│   ├── game_manager.py      # Main orchestrator
│   ├── audio_manager.py     # Audio processing
│   ├── hand_tracker.py      # Image processing
│   ├── lane.py              # Target zones
│   ├── falling_object.py    # Rhythm notes
│   ├── collision.py         # Hit detection
│   └── score_manager.py     # Scoring system
│
├── ui/                      # User interface
│   ├── menu_screen.py       # Main menu
│   ├── game_screen.py       # Game UI with video overlay
│   └── result_screen.py     # Result stats
│
└── assets/                  # Media files
    ├── audio/
    │   ├── main.mp3         # Main beat (9s loop)
    │   ├── kick.wav
    │   ├── snare-drum-341273.mp3
    │   └── open-hi-hat-431740.mp3
    └── image/
        ├── kick.png
        ├── snare.PNG
        └── hi-hat.PNG
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure camera is connected and working

3. Run the game:
```bash
python main.py
```

## Controls

### Menu
- **UP/DOWN Arrow**: Select difficulty
- **ENTER/SPACE**: Start game

### In-Game
- **Hands**: Position hands over target zones to hit notes
- **ESC**: Return to menu

### Result Screen
- **R**: Retry with same difficulty
- **M/ESC**: Return to main menu

## Technical Details

### Image Processing
- MediaPipe Hands detection with 0.7 confidence threshold
- Bounding box calculation from 21 hand landmarks
- Real-time coordinate transformation (camera → screen space)
- Collision detection using rectangle intersection

### Video Processing
- 1280x720 HD camera capture (720p)
- High-quality LANCZOS4 interpolation for scaling
- BGR→RGB color space conversion
- MJPG compression for better quality
- Surface rotation and alpha blending
- Real-time overlay rendering at 60 FPS

### Audio Processing
- 44.1kHz audio sampling rate
- Infinite loop with pygame.mixer.music.play(-1)
- Multi-channel sound effects playback
- Beat-synchronized object spawning

## Performance

- **Target FPS**: 60 FPS
- **Hand Detection**: ~30ms per frame
- **Total Latency**: <50ms (detection + rendering)
- **Audio Latency**: <10ms

## Referensi
https://vt.tiktok.com/ZSydyTok3/
