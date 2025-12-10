"""
HandBeats - Gesture Rhythm Game
===================================

MULTIMEDIA PROCESSING PROJECT
- IMAGE PROCESSING: MediaPipe hand detection and tracking
- VIDEO PROCESSING: Real-time camera feed with overlay graphics
- AUDIO PROCESSING: Seamless music looping and synchronized sound effects

Team Members:
- Ferdana Al-Hakim
- Yesa Viola
- Nydia Renli Sinaga

Course: Sistem/Teknologi Multimedia - IF25-40305
"""

import sys
from src.game_manager import GameManager


def main():
    """
    Main entry point for HandBeats Rhythm Game

    MULTIMEDIA COMPONENTS:
    1. IMAGE PROCESSING - Hand gesture recognition using MediaPipe
    2. AUDIO PROCESSING - Music loop and instrument sound effects
    3. VIDEO PROCESSING - Camera capture with real-time overlay
    """

    print("=" * 60)
    print("  HANDBEATS - GESTURE RHYTHM GAME")
    print("=" * 60)
    print("\nMULTIMEDIA PROCESSING COMPONENTS:")
    print("  [OK] IMAGE: MediaPipe hand detection & tracking")
    print("  [OK] AUDIO: Seamless music loop + sound effects")
    print("  [OK] VIDEO: Real-time camera overlay rendering")
    print("\nTeam: Ferdana")
    print("Course: Sistem/Teknologi Multimedia\n")
    print("=" * 60)
    print("\nInitializing game...\n")

    try:
        # Create and run game
        game = GameManager()
        game.run()

    except KeyboardInterrupt:
        print("\n\n[WARNING] Game interrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
