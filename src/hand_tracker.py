"""
Hand Tracker - IMAGE PROCESSING Module
Uses MediaPipe for real-time hand detection and tracking
Processes video frames to extract hand positions and bounding boxes
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
from config.constants import (
    HAND_DETECTION_CONFIDENCE,
    HAND_TRACKING_CONFIDENCE,
    MAX_HANDS,
    HAND_BBOX_PADDING,
    CAMERA_WIDTH,
    CAMERA_HEIGHT
)
from config.settings import GameSettings


class HandTracker:
    """
    Hand detection and tracking using MediaPipe
    IMAGE PROCESSING: Real-time hand landmark detection from video frames
    """

    def __init__(self):
        """Initialize MediaPipe Hands"""
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize hands detector
        # IMAGE PROCESSING: Configure detection parameters
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=HAND_TRACKING_CONFIDENCE
        )

        # Drawing styles
        self.landmark_style = self.mp_draw.DrawingSpec(
            color=(0, 255, 0), thickness=2, circle_radius=2
        )
        self.connection_style = self.mp_draw.DrawingSpec(
            color=(255, 255, 255), thickness=2
        )

    def process_frame(self, frame: np.ndarray) -> Optional[object]:
        """
        Process video frame to detect hands
        IMAGE PROCESSING: Convert BGR to RGB and run MediaPipe detection

        Args:
            frame: BGR image from camera

        Returns:
            MediaPipe results object
        """
        # Convert BGR to RGB (required by MediaPipe)
        # IMAGE PROCESSING: Color space conversion
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame through MediaPipe
        # IMAGE PROCESSING: Hand landmark detection
        results = self.hands.process(rgb_frame)

        return results

    def get_hand_bboxes(self, results, frame_width: int, frame_height: int) -> Dict[str, Dict]:
        """
        Extract bounding boxes for detected hands
        IMAGE PROCESSING: Calculate bounding boxes from landmarks

        Args:
            results: MediaPipe detection results
            frame_width: Width of video frame
            frame_height: Height of video frame

        Returns:
            Dictionary with 'Left' and 'Right' hand bounding boxes
        """
        hand_bboxes = {}

        if not results.multi_hand_landmarks:
            return hand_bboxes

        # Process each detected hand
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # Get hand label (Left or Right)
            hand_label = results.multi_handedness[idx].classification[0].label

            # Extract all landmark coordinates
            # IMAGE PROCESSING: Convert normalized coordinates to pixel coordinates
            x_coords = []
            y_coords = []

            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                x_coords.append(x)
                y_coords.append(y)

            # Calculate bounding box
            # IMAGE PROCESSING: Find min/max coordinates
            min_x = max(0, min(x_coords) - HAND_BBOX_PADDING)
            max_x = min(frame_width, max(x_coords) + HAND_BBOX_PADDING)
            min_y = max(0, min(y_coords) - HAND_BBOX_PADDING)
            max_y = min(frame_height, max(y_coords) + HAND_BBOX_PADDING)

            # Store bounding box info
            hand_bboxes[hand_label] = {
                'x': min_x,
                'y': min_y,
                'width': max_x - min_x,
                'height': max_y - min_y,
                'center_x': (min_x + max_x) // 2,
                'center_y': (min_y + max_y) // 2,
                'landmarks': hand_landmarks
            }

        return hand_bboxes

    def get_hand_positions_scaled(self, results, frame_width: int, frame_height: int,
                                  screen_width: int, screen_height: int) -> Dict[str, Dict]:
        """
        Get hand positions scaled to game screen coordinates
        IMAGE PROCESSING: Coordinate transformation from camera to screen space

        Args:
            results: MediaPipe results
            frame_width: Camera frame width
            frame_height: Camera frame height
            screen_width: Game screen width
            screen_height: Game screen height

        Returns:
            Hand bounding boxes in screen coordinates
        """
        # Get bboxes in camera coordinates
        camera_bboxes = self.get_hand_bboxes(results, frame_width, frame_height)

        # Scale to screen coordinates
        # IMAGE PROCESSING: Coordinate scaling
        screen_bboxes = {}

        for hand_label, bbox in camera_bboxes.items():
            # Scale factors
            scale_x = screen_width / frame_width
            scale_y = screen_height / frame_height

            screen_bboxes[hand_label] = {
                'x': int(bbox['x'] * scale_x),
                'y': int(bbox['y'] * scale_y),
                'width': int(bbox['width'] * scale_x),
                'height': int(bbox['height'] * scale_y),
                'center_x': int(bbox['center_x'] * scale_x),
                'center_y': int(bbox['center_y'] * scale_y),
                'landmarks': bbox['landmarks']
            }

        return screen_bboxes

    def draw_landmarks(self, frame: np.ndarray, results) -> np.ndarray:
        """
        Draw hand landmarks on frame
        IMAGE PROCESSING: Visual overlay on video frame

        Args:
            frame: Video frame
            results: MediaPipe results

        Returns:
            Frame with landmarks drawn
        """
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks and connections
                # IMAGE PROCESSING: Overlay graphics on video
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.landmark_style,
                    self.connection_style
                )

        return frame

    def draw_bounding_boxes(self, frame: np.ndarray, hand_bboxes: Dict[str, Dict],
                           color=(0, 255, 0), thickness=3) -> np.ndarray:
        """
        Draw bounding boxes around hands
        IMAGE PROCESSING: Visual feedback overlay

        Args:
            frame: Video frame
            hand_bboxes: Dictionary of hand bounding boxes
            color: Box color (BGR)
            thickness: Line thickness

        Returns:
            Frame with bounding boxes drawn
        """
        for hand_label, bbox in hand_bboxes.items():
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']

            # Draw rectangle
            # IMAGE PROCESSING: Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

            # Draw label
            label_text = f"{hand_label}"
            cv2.putText(
                frame,
                label_text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

            # Draw center point
            center_x, center_y = bbox['center_x'], bbox['center_y']
            cv2.circle(frame, (center_x, center_y), 5, color, -1)

        return frame

    def check_hand_in_zone(self, hand_bbox: Dict, zone: Dict) -> bool:
        """
        Check if hand bounding box overlaps with a zone
        IMAGE PROCESSING: Collision detection between hand and target zone

        Args:
            hand_bbox: Hand bounding box dict
            zone: Zone dict with x, y, width, height

        Returns:
            True if hand overlaps zone
        """
        # Hand bounding box
        hx1 = hand_bbox['x']
        hy1 = hand_bbox['y']
        hx2 = hx1 + hand_bbox['width']
        hy2 = hy1 + hand_bbox['height']

        # Zone bounding box
        zx1 = zone['x']
        zy1 = zone['y']
        zx2 = zx1 + zone['width']
        zy2 = zy1 + zone['height']

        # Check overlap
        # IMAGE PROCESSING: Rectangle intersection
        overlap = (hx1 < zx2 and hx2 > zx1 and hy1 < zy2 and hy2 > zy1)

        return overlap

    def cleanup(self):
        """Release MediaPipe resources"""
        self.hands.close()
        print("✓ Hand tracker cleaned up")


# ===== UTILITY FUNCTIONS =====

def normalize_coordinates(x: int, y: int, width: int, height: int) -> Tuple[float, float]:
    """
    Normalize pixel coordinates to 0.0-1.0 range
    IMAGE PROCESSING: Coordinate normalization
    """
    norm_x = x / width
    norm_y = y / height
    return norm_x, norm_y


def denormalize_coordinates(norm_x: float, norm_y: float, width: int, height: int) -> Tuple[int, int]:
    """
    Convert normalized coordinates back to pixels
    IMAGE PROCESSING: Coordinate denormalization
    """
    x = int(norm_x * width)
    y = int(norm_y * height)
    return x, y
