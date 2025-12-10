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
    WARMUP = 2
    COUNTDOWN = 3
    PLAYING = 4
    RESULT = 5
    QUIT = 6


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
        self.camera = None

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

        # Warmup tracking
        self.warmup_objects = None
        self.warmup_completed = False

        print("Game Manager initialized")
        print("All multimedia subsystems ready")

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

        elif self.state == GameState.WARMUP:
            # Update warmup objects
            self.game_time += dt
            for obj in self.warmup_objects:
                obj.update(dt, self.game_time)

            # Check if all warmup objects have passed target zone
            all_passed = all(obj.y > obj.target_y + 100 or obj.is_dead for obj in self.warmup_objects)
            if all_passed and not self.warmup_completed:
                self.warmup_completed = True
                self.state = GameState.COUNTDOWN
                self.game_time = 0
                self.countdown_time = 3.0
                print("Warmup completed! Starting countdown...")

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

        # IMAGE PROCESSING: Detect hands and face using MediaPipe
        frame, hand_results, face_results = self.hand_tracker.process_frame(frame)

        # Get fingertip positions for COLLISION (inverted X)
        fingertip_positions = self.hand_tracker.get_fingertip_positions(
            hand_results,
            SCREEN_WIDTH, SCREEN_HEIGHT
        )

        # Get fingertip positions for VISUAL (not inverted, matches video)
        fingertip_visuals = self.hand_tracker.get_fingertip_visuals(
            hand_results,
            SCREEN_WIDTH, SCREEN_HEIGHT
        )

        # Get chin position for COLLISION (inverted X)
        chin_position = self.hand_tracker.get_chin_position(
            face_results,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

        # Get chin position for VISUAL (not inverted)
        chin_visual = self.hand_tracker.get_chin_visual(
            face_results,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

        # Calculate velocities for gesture detection
        fingertip_velocities = self.hand_tracker.calculate_velocity(
            fingertip_positions,
            self.hand_tracker.prev_fingertip_positions
        )
        chin_velocity = self.hand_tracker.calculate_chin_velocity(
            chin_position,
            self.hand_tracker.prev_chin_position
        ) if chin_position else 0.0

        # Update velocity tracking for next frame
        self.hand_tracker.update_velocity_tracking(fingertip_positions, chin_position)

        # Store frame and detection data for rendering
        self.current_frame = frame
        self.current_fingertips = fingertip_positions
        self.current_fingertips_visual = fingertip_visuals
        self.current_chin = chin_position
        self.current_chin_visual = chin_visual

        # Update lanes with velocity check
        active_lanes = self.lane_manager.check_collisions_with_velocity(
            fingertip_positions,
            chin_position,
            fingertip_velocities,
            chin_velocity,
            self.hand_tracker.velocity_threshold
        )

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

        elif self.state == GameState.WARMUP:
            # Render warmup phase
            self.game_screen.render(
                camera_frame=self.current_frame,
                score_manager=self.score_manager,
                game_time=self.game_time,
                total_time=10.0,
                fingertip_positions=self.current_fingertips_visual,
                chin_position=self.current_chin_visual
            )
            # Render lanes
            self.lane_manager.render(self.screen)
            # Render warmup objects
            for obj in self.warmup_objects:
                obj.render(self.screen)
            # Show "WARM UP" text
            font = pygame.font.Font(None, 72)
            text = font.render("WARM UP", True, (255, 255, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(text, text_rect)

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
            self.current_fingertips_visual,  # Visual coords (not inverted)
            self.current_chin_visual  # Visual coords (not inverted)
        )

        # Render lanes
        self.lane_manager.render(self.screen)

        # Render falling objects
        self.falling_objects.render(self.screen)

    def start_game(self):
        """Initialize and start new game"""
        print("\nStarting new game...")

        # Get difficulty settings
        self.current_difficulty = self.menu_screen.get_selected_difficulty()
        print(f"Difficulty: {self.current_difficulty['name']}")

        # Initialize camera
        if not self.camera:
            print("Initializing camera...")
            self.camera = cv2.VideoCapture(0)
            # === PERBAIKAN: Memaksa resolusi 16:9 ===
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            # =======================================
            if not self.camera.isOpened():
                print("Error: Cannot open camera")
                self.running = False
                return
            
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Camera initialized: {int(actual_width)}x{int(actual_height)}")

        # Generate beatmap
        print("Generating beatmap...")
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
        print(f"Beatmap created: {len(self.beatmap)} notes")

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
        self.current_fingertips = {}
        self.current_fingertips_visual = {}
        self.current_chin = None
        self.current_chin_visual = None

        # Reset UI screens
        self.menu_screen.reset()
        self.result_screen.reset()

        # Create warmup objects (3 objects: kick, hihat, snare)
        from src.falling_object import FallingObject
        self.warmup_objects = []
        warmup_sequence = [
            (0.5, 'kick'),
            (1.5, 'hihat'),
            (2.5, 'snare')
        ]
        for spawn_time, instrument in warmup_sequence:
            obj = FallingObject(instrument, spawn_time + 3.0, self.current_difficulty['falling_speed'])
            self.warmup_objects.append(obj)

        self.warmup_completed = False

        # Enter warmup state
        self.state = GameState.WARMUP

        print("Game started with warmup!\n")

    def end_game(self):
        """End current game"""
        print("\nGame Over!")

        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
            print("Camera released")

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
        print("[INFO] Returning to menu...")

        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
            print("Camera released")

        # Stop music
        self.audio_manager.stop_main_beat()

        # Reset state
        self.state = GameState.MENU
        self.menu_screen.reset()

    def cleanup(self):
        """Cleanup resources"""
        print("\n[CLEANUP] Cleaning up...")

        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None

        # Cleanup audio
        self.audio_manager.cleanup()

        # Cleanup hand tracker
        self.hand_tracker.cleanup()

        # Quit pygame
        pygame.quit()
        cv2.destroyAllWindows()

        print("Cleanup complete")
        sys.exit(0)