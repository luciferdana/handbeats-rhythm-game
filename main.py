import cv2
import mediapipe as mp
import numpy as np
import pygame
import sys
from datetime import datetime

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results

    def draw_landmarks(self, frame, results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
        return frame

class RhythmGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.width = 1280
        self.height = 720
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Hand Beats - Rhythm Game")

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True

        self.hand_tracker = HandTracker()
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Error: Cannot open camera")
            sys.exit(1)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def process_camera(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)
        results = self.hand_tracker.process_frame(frame)
        frame = self.hand_tracker.draw_landmarks(frame, results)

        return frame, results

    def render_camera_feed(self, frame):
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(
                np.rot90(frame_rgb)
            )
            self.screen.blit(frame_surface, (0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))

        frame, results = self.process_camera()
        self.render_camera_feed(frame)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)

        self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        pygame.quit()
        sys.exit(0)

def main():
    game = RhythmGame()
    game.run()

if __name__ == "__main__":
    main()
