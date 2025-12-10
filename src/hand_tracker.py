"""
Hand Tracker - IMAGE PROCESSING Module
Uses MediaPipe for real-time hand and face detection and tracking
Processes video frames to extract hand and chin positions
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Optional
from config.constants import (
    HAND_DETECTION_CONFIDENCE,
    HAND_TRACKING_CONFIDENCE,
    MAX_HANDS,
    TOPBAR_HEIGHT
)
from config.settings import GameSettings


class HandTracker:
    """
    Hand and face detection and tracking using MediaPipe
    IMAGE PROCESSING: Real-time landmark detection from video frames
    """

    def __init__(self):
        """Initialize MediaPipe Hands and Face Mesh"""
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize hands detector - OPTIMIZED for low latency
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Initialize face mesh - OPTIMIZED for low latency
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Drawing styles
        self.landmark_style = self.mp_draw.DrawingSpec(
            color=(0, 255, 0), thickness=2, circle_radius=2
        )
        self.connection_style = self.mp_draw.DrawingSpec(
            color=(255, 255, 255), thickness=2
        )

        # Velocity tracking for gesture detection
        self.prev_fingertip_positions = {}
        self.prev_chin_position = None
        self.velocity_threshold = 15.0  # Minimum speed (pixels per frame) for valid hit

    def process_frame(self, frame: np.ndarray) -> tuple:
        """
        Process video frame to detect hands and face.
        Flips the frame horizontally for intuitive mirror-like control.

        Args:
            frame: BGR image from camera

        Returns:
            Tuple of (flipped_frame, hand_results, face_results)
        """
        # === PERBAIKAN A: FLIP VISUAL (MIRROR) ===
        frame = cv2.flip(frame, 1)
        # ========================================
        
        # Convert BGR to RGB (required by MediaPipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame through MediaPipe for hands and face
        hand_results = self.hands.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)

        return frame, hand_results, face_results

    def get_fingertip_positions(self, results, screen_width: int, screen_height: int) -> Dict[str, Dict]:
        """
        Get index fingertip positions for COLLISION detection (inverted X).

        Args:
            results: MediaPipe hand results
            screen_width: Game screen width
            screen_height: Game screen height

        Returns:
            Dictionary with fingertip positions (X inverted for collision)
        """
        fingertip_zones = {}

        if not results.multi_hand_landmarks:
            return fingertip_zones

        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[idx].classification[0].label
            index_tip = hand_landmarks.landmark[8]

            # Invert X for collision detection (matches zone positions)
            tip_x_collision = int((1 - index_tip.x) * screen_width)

            # Y offset by top bar
            tip_y = int(index_tip.y * (screen_height - TOPBAR_HEIGHT) + TOPBAR_HEIGHT)

            zone_size = 40
            fingertip_zones[hand_label] = {
                'x': tip_x_collision - zone_size // 2,
                'y': tip_y - zone_size // 2,
                'width': zone_size,
                'height': zone_size,
                'center_x': tip_x_collision,
                'center_y': tip_y
            }
        return fingertip_zones

    def get_fingertip_visuals(self, results, screen_width: int, screen_height: int) -> Dict[str, Dict]:
        """
        Get fingertip positions for VISUAL display (NOT inverted, matches flipped video).

        Args:
            results: MediaPipe hand results
            screen_width: Game screen width
            screen_height: Game screen height

        Returns:
            Dictionary with fingertip visual positions (no X inversion)
        """
        fingertip_visuals = {}

        if not results.multi_hand_landmarks:
            return fingertip_visuals

        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            hand_label = results.multi_handedness[idx].classification[0].label
            index_tip = hand_landmarks.landmark[8]

            # NO X inversion - use raw coordinates (matches flipped video)
            tip_x_visual = int(index_tip.x * screen_width)
            tip_y = int(index_tip.y * (screen_height - TOPBAR_HEIGHT) + TOPBAR_HEIGHT)

            fingertip_visuals[hand_label] = {
                'center_x': tip_x_visual,
                'center_y': tip_y
            }
        return fingertip_visuals

    def get_chin_position(self, face_results, screen_width: int, screen_height: int) -> Optional[Dict]:
        """
        Get chin position for COLLISION detection (inverted X).

        Args:
            face_results: MediaPipe FaceMesh results
            screen_width: Game screen width
            screen_height: Game screen height

        Returns:
            Dictionary with chin position (X inverted for collision), or None
        """
        if not face_results.multi_face_landmarks:
            return None

        face_landmarks = face_results.multi_face_landmarks[0]
        chin_landmark = face_landmarks.landmark[152]

        # Invert X for collision detection
        chin_x_collision = int((1 - chin_landmark.x) * screen_width)
        chin_y = int(chin_landmark.y * (screen_height - TOPBAR_HEIGHT) + TOPBAR_HEIGHT)

        zone_size = 40
        return {
            'x': chin_x_collision - zone_size // 2,
            'y': chin_y - zone_size // 2,
            'width': zone_size,
            'height': zone_size,
            'center_x': chin_x_collision,
            'center_y': chin_y
        }

    def get_chin_visual(self, face_results, screen_width: int, screen_height: int) -> Optional[Dict]:
        """
        Get chin position for VISUAL display (NOT inverted, matches flipped video).

        Args:
            face_results: MediaPipe FaceMesh results
            screen_width: Game screen width
            screen_height: Game screen height

        Returns:
            Dictionary with chin visual position (no X inversion), or None
        """
        if not face_results.multi_face_landmarks:
            return None

        face_landmarks = face_results.multi_face_landmarks[0]
        chin_landmark = face_landmarks.landmark[152]

        # NO X inversion - matches flipped video
        chin_x_visual = int(chin_landmark.x * screen_width)
        chin_y = int(chin_landmark.y * (screen_height - TOPBAR_HEIGHT) + TOPBAR_HEIGHT)

        return {
            'center_x': chin_x_visual,
            'center_y': chin_y
        }

    def calculate_velocity(self, current_positions: Dict, previous_positions: Dict) -> Dict[str, float]:
        """
        Calculate velocity (speed) of hand movement for gesture detection.

        Args:
            current_positions: Current frame positions
            previous_positions: Previous frame positions

        Returns:
            Dictionary with hand labels and their velocities
        """
        velocities = {}

        for hand_label in current_positions:
            if hand_label in previous_positions:
                curr = current_positions[hand_label]
                prev = previous_positions[hand_label]

                # Calculate Euclidean distance
                dx = curr['center_x'] - prev['center_x']
                dy = curr['center_y'] - prev['center_y']
                velocity = (dx**2 + dy**2) ** 0.5

                velocities[hand_label] = velocity
            else:
                # First detection, assume zero velocity
                velocities[hand_label] = 0.0

        return velocities

    def calculate_chin_velocity(self, current_position: Dict, previous_position: Optional[Dict]) -> float:
        """
        Calculate velocity of chin movement for gesture detection.

        Args:
            current_position: Current chin position
            previous_position: Previous chin position

        Returns:
            Velocity (speed) of chin movement
        """
        if previous_position is None:
            return 0.0

        dx = current_position['center_x'] - previous_position['center_x']
        dy = current_position['center_y'] - previous_position['center_y']
        velocity = (dx**2 + dy**2) ** 0.5

        return velocity

    def update_velocity_tracking(self, fingertip_positions: Dict, chin_position: Optional[Dict]):
        """
        Update velocity tracking with current positions.

        Args:
            fingertip_positions: Current fingertip positions
            chin_position: Current chin position
        """
        self.prev_fingertip_positions = fingertip_positions.copy() if fingertip_positions else {}
        self.prev_chin_position = chin_position.copy() if chin_position else None

    def draw_landmarks(self, frame: np.ndarray, hand_results, face_results) -> np.ndarray:
        """
        Draw hand landmarks on the frame.

        Args:
            frame: Video frame (already flipped)
            hand_results: MediaPipe hand results
            face_results: MediaPipe face results

        Returns:
            Frame with landmarks drawn
        """
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.landmark_style, self.connection_style
                )
        return frame

    def cleanup(self):
        """Release MediaPipe resources"""
        self.hands.close()
        self.face_mesh.close()
        print("Hand and face tracker cleaned up")