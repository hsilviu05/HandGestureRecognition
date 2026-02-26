import cv2
import numpy as np

class HandDetector:
    def __init__(self, max_hands=2, detection_confidence=0.7, tracking_confidence=0.5):
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        # Try new MediaPipe Tasks API first, then fall back to legacy
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            # Use the new Tasks API
            base_options = python.BaseOptions(
                model_asset_path='assets/models/hand_landmarker.task'
            )
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=max_hands,
                min_hand_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
                running_mode=vision.RunningMode.IMAGE
            )
            self.hand_landmarker = vision.HandLandmarker.create_from_options(options)
            self.use_tasks_api = True
            self.mp_drawing = None
            print("Using MediaPipe Tasks API")
            
        except Exception as e:
            print(f"Tasks API failed: {e}, trying legacy API...")
            try:
                import mediapipe as mp
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=max_hands,
                    min_detection_confidence=detection_confidence,
                    min_tracking_confidence=tracking_confidence
                )
                self.mp_drawing = mp.solutions.drawing_utils
                self.use_tasks_api = False
                print("Using legacy MediaPipe API")
            except Exception as e2:
                raise ImportError(f"MediaPipe is not available: {e2}")
    
    def find_hands(self, frame, draw=True):
        """Detect hands in frame and return landmarks"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        all_hands = []
        
        if self.use_tasks_api:
            import mediapipe as mp
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            results = self.hand_landmarker.detect(mp_image)
            
            if results.hand_landmarks:
                for hand_idx, hand_landmarks in enumerate(results.hand_landmarks):
                    hand_data = {"landmarks": [], "handedness": "Unknown"}
                    
                    if results.handedness and hand_idx < len(results.handedness):
                        hand_data["handedness"] = results.handedness[hand_idx][0].category_name
                    
                    h, w, _ = frame.shape
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        hand_data["landmarks"].append((cx, cy, lm.z))
                    
                    all_hands.append(hand_data)
                    
                    if draw:
                        self._draw_landmarks(frame, hand_landmarks, w, h)
        else:
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    hand_data = {"landmarks": [], "handedness": "Unknown"}
                    
                    if results.multi_handedness:
                        hand_data["handedness"] = results.multi_handedness[hand_idx].classification[0].label
                    
                    h, w, _ = frame.shape
                    for lm in hand_landmarks.landmark:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        hand_data["landmarks"].append((cx, cy, lm.z))
                    
                    all_hands.append(hand_data)
                    
                    if draw and self.mp_drawing:
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
        
        return all_hands, frame
    
    def _draw_landmarks(self, frame, landmarks, w, h):
        """Draw hand landmarks on frame for Tasks API"""
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        
        for connection in connections:
            cv2.line(frame, points[connection[0]], points[connection[1]], (0, 255, 0), 2)
        
        for point in points:
            cv2.circle(frame, point, 5, (255, 0, 0), -1)
    
    def release(self):
        """Release resources"""
        if self.use_tasks_api:
            self.hand_landmarker.close()
        else:
            self.hands.close()