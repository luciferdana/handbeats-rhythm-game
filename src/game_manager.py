"""
Game Manager - Main Game State Controller
MULTIMEDIA INTEGRATION: Orchestrates Image, Audio, and Video Processing
Manages game flow, state transitions, and component coordination
"""

import pygame
import cv2
import sys
from enum import Enum

from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAMERA_WIDTH, CAMERA_HEIGHT
from config.settings import GameSettings, DifficultySettings
from config.beatmap import BeatmapGenerator, loop_beatmap

from src.audio_manager import AudioManager
from src.hand_tracker import HandTracker
from src.lane import LaneManager
from src.falling_object import FallingObjectManager
from src.collision import CollisionDetector
from src.score_manager import ScoreManager

from ui.menu_screen import MenuScreen
from ui.game_screen import GameScreen
from ui.result_screen import ResultScreen


class GameState(Enum):
    """Game state enumeration"""
    MENU = 1
    COUNTDOWN = 2
    PLAYING = 3
    RESULT = 4
    QUIT = 5


class GameManager:
    """
    Main game controller
    Coordinates all multimedia components: image, audio, video processing
    """

    def __init__(self):
        """Initialize game manager and all subsystems"""
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()

        # Create display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hand Beats - Rhythm Game")

        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = FPS

        # Game state
        self.state = GameState.MENU
        self.running = True

        # Difficulty settings
        self.current_difficulty = None

        # MULTIMEDIA COMPONENTS

        # AUDIO PROCESSING
        self.audio_manager = AudioManager()
        self.audio_manager.load_main_beat()

        # IMAGE/VIDEO PROCESSING
        self.hand_tracker = HandTracker()
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        if not self.camera.isOpened():
            print("❌ Error: Cannot open camera")
            sys.exit(1)

        # Game components
        self.lane_manager = None
        self.falling_objects = None
        self.collision_detector = None
        self.score_manager = None

        # UI Screens
        self.menu_screen = MenuScreen(self.screen)
        self.game_screen = GameScreen(self.screen)
        self.result_screen = ResultScreen(self.screen)

        # Game timing
        self.game_time = 0
        self.countdown_time = 3.0
        self.total_game_duration = GameSettings.GAME_DURATION

        # Beatmap
        self.beatmap = None

        print("✓ Game Manager initialized")
        print("✓ All multimedia subsystems ready")

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds

            # Handle events
            events = pygame.event.get()
            self.handle_events(events)

            # Update current state
            self.update(dt)

            # Render current state
            self.render()

            # Update display
            pygame.display.flip()

        # Cleanup
        self.cleanup()

    def handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        # State-specific event handling
        if self.state == GameState.MENU:
            self.menu_screen.handle_events(events)

        elif self.state == GameState.RESULT:
            self.result_screen.handle_events(events)

        # Global controls
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.state == GameState.PLAYING:
                    # Pause or return to menu
                    self.return_to_menu()

    def update(self, dt: float):
        """Update current game state"""
        if self.state == GameState.MENU:
            self.menu_screen.update(dt)

            # Check if should start game
            if self.menu_screen.should_start_game():
                self.start_game()

        elif self.state == GameState.COUNTDOWN:
            self.countdown_time -= dt

            if self.countdown_time <= 0:
                # Start actual game
                self.state = GameState.PLAYING
                self.game_time = 0

                # Start music
                self.audio_manager.play_main_beat()

        elif self.state == GameState.PLAYING:
            self.update_gameplay(dt)

        elif self.state == GameState.RESULT:
            # Check if should retry or return to menu
            if self.result_screen.should_retry_game():
                self.start_game()
            elif self.result_screen.should_return_to_menu():
                self.return_to_menu()

    def update_gameplay(self, dt: float):
        """
        Update gameplay
        MULTIMEDIA PROCESSING: Integrate image, audio, video
        """
        self.game_time += dt

        # Check if game over
        if self.game_time >= self.total_game_duration:
            self.end_game()
            return

        # VIDEO PROCESSING: Capture and process camera frame
        ret, frame = self.camera.read()
        if not ret:
            return

        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)

        # IMAGE PROCESSING: Detect hands using MediaPipe
        results = self.hand_tracker.process_frame(frame)

        # Get hand bounding boxes in screen coordinates
        hand_bboxes = self.hand_tracker.get_hand_positions_scaled(
            results,
            CAMERA_WIDTH, CAMERA_HEIGHT,
            SCREEN_WIDTH, SCREEN_HEIGHT - 80  # Accounting for top bar
        )

        # Store frame for rendering
        self.current_frame = frame
        self.current_hand_bboxes = hand_bboxes

        # Update lanes based on hand positions
        active_lanes = self.lane_manager.check_hand_collisions(hand_bboxes)

        # Update lane visual state
        self.lane_manager.update(dt)

        # Update falling objects
        self.falling_objects.update(dt, self.game_time)

        # COLLISION DETECTION: Check for hits
        objects_in_zone = self.falling_objects.get_objects_in_hit_zone()
        hit_results = self.collision_detector.check_multiple_objects(objects_in_zone, active_lanes)

        # Process hit results
        for hit_result in hit_results:
            # Update score
            self.score_manager.add_hit(hit_result)

            # Visual feedback
            feedback_text, feedback_color = self.collision_detector.get_timing_feedback(0)
            self.game_screen.show_feedback(hit_result.rating, feedback_color)

            # AUDIO PROCESSING: Play hit sound and instrument
            self.audio_manager.play_hit_sound(hit_result.rating.lower())
            self.audio_manager.play_instrument(hit_result.instrument)

            # Visual feedback on lane
            lane = self.lane_manager.get_lane_by_instrument(hit_result.instrument)
            if lane:
                lane.trigger_hit()

        # Check for missed objects
        for obj in self.falling_objects.get_active_objects():
            if obj.is_missed and not obj.is_dead:
                self.score_manager.add_miss()

        # Update game screen
        self.game_screen.update(dt)

    def render(self):
        """Render current state"""
        if self.state == GameState.MENU:
            self.menu_screen.render()

        elif self.state == GameState.COUNTDOWN:
            # Show countdown
            count = int(self.countdown_time) + 1
            self.game_screen.render_countdown(count)

        elif self.state == GameState.PLAYING:
            self.render_gameplay()

        elif self.state == GameState.RESULT:
            self.result_screen.render(self.score_manager, self.current_difficulty['name'])

    def render_gameplay(self):
        """Render gameplay screen"""
        # Render camera feed and UI
        self.game_screen.render(
            self.current_frame,
            self.score_manager,
            self.game_time,
            self.total_game_duration,
            self.current_hand_bboxes
        )

        # Render lanes
        self.lane_manager.render(self.screen)

        # Render falling objects
        self.falling_objects.render(self.screen)

    def start_game(self):
        """Initialize and start new game"""
        print("\n🎮 Starting new game...")

        # Get difficulty settings
        self.current_difficulty = self.menu_screen.get_selected_difficulty()
        print(f"✓ Difficulty: {self.current_difficulty['name']}")

        # Generate beatmap
        print("✓ Generating beatmap...")
        generator = BeatmapGenerator(
            duration=GameSettings.BEAT_DURATION,  # 9 seconds
            bpm=GameSettings.BEAT_BPM,
            pattern_type=self.current_difficulty['pattern_type'],
            variation=self.current_difficulty['pattern_variation']
        )

        # Generate one loop and repeat it
        one_loop = generator.generate()
        num_loops = int(self.total_game_duration / GameSettings.BEAT_DURATION) + 1
        self.beatmap = loop_beatmap(one_loop, num_loops, GameSettings.BEAT_DURATION)
        print(f"✓ Beatmap created: {len(self.beatmap)} notes")

        # Initialize game components
        self.lane_manager = LaneManager()
        self.falling_objects = FallingObjectManager(
            self.beatmap,
            self.current_difficulty['falling_speed']
        )
        self.collision_detector = CollisionDetector(
            perfect_window=self.current_difficulty['perfect_window'],
            good_window=self.current_difficulty['good_window'],
            ok_window=self.current_difficulty['ok_window']
        )
        self.score_manager = ScoreManager()

        # Reset state
        self.game_time = 0
        self.countdown_time = 3.0
        self.current_frame = None
        self.current_hand_bboxes = {}

        # Reset UI screens
        self.menu_screen.reset()
        self.result_screen.reset()

        # Enter countdown state
        self.state = GameState.COUNTDOWN

        print("✓ Game started!\n")

    def end_game(self):
        """End current game"""
        print("\n🏁 Game Over!")

        # Stop music
        self.audio_manager.stop_main_beat()

        # Print final stats
        stats = self.score_manager.get_stats_dict()
        print(f"Final Score: {stats['score']}")
        print(f"Accuracy: {stats['accuracy']:.1f}%")
        print(f"Rank: {stats['rank']}")
        print(f"Max Combo: {stats['max_combo']}x")

        # Transition to result screen
        self.state = GameState.RESULT

    def return_to_menu(self):
        """Return to main menu"""
        print("↩ Returning to menu...")

        # Stop music
        self.audio_manager.stop_main_beat()

        # Reset state
        self.state = GameState.MENU
        self.menu_screen.reset()

    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")

        # Release camera
        self.camera.release()

        # Cleanup audio
        self.audio_manager.cleanup()

        # Cleanup hand tracker
        self.hand_tracker.cleanup()

        # Quit pygame
        pygame.quit()
        cv2.destroyAllWindows()

        print("✓ Cleanup complete")
        sys.exit(0)
