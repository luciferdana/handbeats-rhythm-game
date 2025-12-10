"""
Collision Detection & Hit Timing System
Determines when hands successfully hit falling objects
Calculates hit accuracy (PERFECT, GOOD, OK, MISS)
"""

from typing import Optional, Tuple


class HitResult:
    """Result of a hit attempt"""

    def __init__(self, success: bool, rating: str, points: int, instrument: str):
        """
        Initialize hit result

        Args:
            success: True if hit was successful
            rating: 'PERFECT', 'GOOD', 'OK', or 'MISS'
            points: Points earned
            instrument: Instrument that was hit
        """
        self.success = success
        self.rating = rating
        self.points = points
        self.instrument = instrument


class CollisionDetector:
    """
    Handles collision detection and hit timing
    Determines accuracy based on timing
    """

    def __init__(self, perfect_window: int,
                 good_window: int,
                 ok_window: int):
        """
        Initialize collision detector

        Args:
            perfect_window: Distance in pixels for PERFECT hit
            good_window: Distance in pixels for GOOD hit
            ok_window: Distance in pixels for OK hit
        """
        self.perfect_window = perfect_window
        self.good_window = good_window
        self.ok_window = ok_window

        # Score values for each rating
        self.score_values = {
            'PERFECT': 100,
            'GOOD': 50,
            'OK': 25,
            'MISS': 0
        }

    def check_hit(self, falling_object, hand_in_lane: bool) -> Optional[HitResult]:
        """
        Check if a falling object was hit

        Args:
            falling_object: FallingObject instance
            hand_in_lane: True if hand is in the correct lane

        Returns:
            HitResult if a hit occurred, None otherwise
        """
        if not hand_in_lane:
            return None

        if falling_object.is_hit or falling_object.is_missed:
            return None

        # Get distance from perfect hit point
        distance = abs(falling_object.get_distance_from_target())

        # Determine hit rating based on distance
        rating = self._calculate_rating(distance)

        if rating == 'MISS':
            return None  # Not close enough

        # Calculate points
        points = self.score_values[rating]

        # Mark object as hit
        falling_object.mark_hit()

        return HitResult(
            success=True,
            rating=rating,
            points=points,
            instrument=falling_object.instrument
        )

    def _calculate_rating(self, distance: float) -> str:
        """
        Calculate hit rating based on distance from target

        Args:
            distance: Distance in pixels from perfect hit point

        Returns:
            Rating string: 'PERFECT', 'GOOD', 'OK', or 'MISS'
        """
        if distance <= self.perfect_window:
            return 'PERFECT'
        elif distance <= self.good_window:
            return 'GOOD'
        elif distance <= self.ok_window:
            return 'OK'
        else:
            return 'MISS'

    def check_multiple_objects(self, objects: list, active_lanes: dict) -> list:
        """
        Check collisions for multiple objects and lanes

        Args:
            objects: List of FallingObject instances in hit zone
            active_lanes: Dict of {instrument: hand_label} for active lanes

        Returns:
            List of HitResult objects
        """
        hit_results = []

        for obj in objects:
            # Check if hand is in the correct lane for this object
            hand_in_lane = obj.instrument in active_lanes

            # Check for hit
            result = self.check_hit(obj, hand_in_lane)

            if result:
                hit_results.append(result)

        return hit_results

    def get_timing_feedback(self, distance: float) -> Tuple[str, tuple]:
        """
        Get visual feedback for timing

        Args:
            distance: Distance from perfect hit point

        Returns:
            Tuple of (message, color)
        """
        rating = self._calculate_rating(distance)

        feedback_map = {
            'PERFECT': ('PERFECT!', (46, 204, 113)),   # Green
            'GOOD': ('GOOD!', (52, 152, 219)),          # Blue
            'OK': ('OK', (241, 196, 15)),               # Yellow
            'MISS': ('MISS', (231, 76, 60))             # Red
        }

        return feedback_map.get(rating, ('', (255, 255, 255)))
