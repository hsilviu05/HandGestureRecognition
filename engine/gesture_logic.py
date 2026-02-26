class GestureRecognizer:
    def __init__(self):
        self.gesture_names = {
            'A': self._is_A_shape,
            'B': self._is_B_shape,
            ##'C': self._is_C_shape,
            'D': self._is_D_shape,
            'E': self._is_E_shape,
            'I': self._is_I_shape,
            'L': self._is_L_shape,
            'V': self._is_V_shape
        }
    
    def recognize(self, landmarks):
        """
        Check all gestures and return the matched one.
        
        Args:
            landmarks: Either
                - list of 21 landmark dicts (with 'x' and 'y' in [0, 1])
                - or a hand dict from HandDetector with key 'landmarks'
                  containing 21 (x, y, z) tuples in pixel space.
            
        Returns:
            str or None: Gesture name if detected, None otherwise
        """
        # Accept hand dict from HandDetector
        if isinstance(landmarks, dict) and "landmarks" in landmarks:
            raw_points = landmarks["landmarks"]
        else:
            raw_points = landmarks

        if not raw_points or len(raw_points) != 21:
            return None

        # Convert to normalized coordinate dicts: [{'x': ..., 'y': ...}, ...]
        if isinstance(raw_points[0], tuple) or isinstance(raw_points[0], list):
            xs = [p[0] for p in raw_points]
            ys = [p[1] for p in raw_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max(max_x - min_x, 1)
            height = max(max_y - min_y, 1)
            norm_landmarks = [
                {
                    "x": (x - min_x) / width,
                    "y": (y - min_y) / height
                }
                for x, y, *_ in raw_points
            ]
        else:
            # Already in dict format
            norm_landmarks = raw_points
        
        for gesture_name, check_function in self.gesture_names.items():
            if check_function(norm_landmarks):
                return gesture_name
        
        return None
    
    def _is_finger_extended(self, landmarks, finger_tip_id, finger_pip_id):
        """Check if a finger is extended"""
        tip_y = landmarks[finger_tip_id]['y']
        pip_y = landmarks[finger_pip_id]['y']
        # Require the tip to be clearly above the PIP joint to avoid noise
        return (pip_y - tip_y) > 0.05  # Tip is above PIP (extended)
    
    def _is_A_shape(self, landmarks):
        """Closed fist with thumb across"""
        # All fingers closed (tips below PIPs)
        fingers_closed = all([
            not self._is_finger_extended(landmarks, 8, 6),   # Index
            not self._is_finger_extended(landmarks, 12, 10), # Middle
            not self._is_finger_extended(landmarks, 16, 14), # Ring
            not self._is_finger_extended(landmarks, 20, 18)  # Pinky
        ])
        
        # Thumb is tucked (simplified check)
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        thumb_close = abs(thumb_tip['x'] - index_mcp['x']) < 0.1
        
        return fingers_closed and thumb_close
    def _is_B_shape(self, landmarks):
        """All fingers extended and together, thumb across palm"""
        fingers_extended = all([
            self._is_finger_extended(landmarks, 8, 6),   # Index
            self._is_finger_extended(landmarks, 12, 10), # Middle
            self._is_finger_extended(landmarks, 16, 14), # Ring
            self._is_finger_extended(landmarks, 20, 18)  # Pinky
        ])
        
        # Thumb is across palm 
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        thumb_across = thumb_tip['x'] < index_mcp['x']
        
        return fingers_extended and thumb_across
    
    def _is_C_shape(self, landmarks):
        """Fingers curved to form a C shape"""
        # Check if fingertips are above PIPs but not fully extended
        index_curved = (landmarks[8]['y'] < landmarks[6]['y']) and \
                       (landmarks[8]['y'] > (landmarks[6]['y'] + 0.1))
        middle_curved = (landmarks[12]['y'] < landmarks[10]['y']) and \
                        (landmarks[12]['y'] > (landmarks[10]['y'] + 0.1))
        ring_curved = (landmarks[16]['y'] < landmarks[14]['y']) and \
                      (landmarks[16]['y'] > (landmarks[14]['y'] + 0.1))
        pinky_curved = (landmarks[20]['y'] < landmarks[18]['y']) and \
                       (landmarks[20]['y'] > (landmarks[18]['y'] + 0.1))
        thumb_curved = (landmarks[4]['x'] > landmarks[3]['x']) and \
                          (landmarks[4]['x'] < (landmarks[3]['x'] + 0.1))
        
        return index_curved and middle_curved and ring_curved and pinky_curved and thumb_curved
    
    def _is_D_shape(self, landmarks):
        """Index finger extended, others closed"""
        index_extended = self._is_finger_extended(landmarks, 8, 6)
        others_closed = all([
            not self._is_finger_extended(landmarks, 12, 10), # Middle
            not self._is_finger_extended(landmarks, 16, 14), # Ring
            not self._is_finger_extended(landmarks, 20, 18)  # Pinky
        ])
        return index_extended and others_closed
    def _is_E_shape(self, landmarks):
        """All fingers closed with thumb across"""
        fingers_closed = all([
            not self._is_finger_extended(landmarks, 8, 6),   # Index
            not self._is_finger_extended(landmarks, 12, 10), # Middle
            not self._is_finger_extended(landmarks, 16, 14), # Ring
            not self._is_finger_extended(landmarks, 20, 18)  # Pinky
        ])
        
        # Thumb is across fingers
        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        thumb_across = thumb_tip['x'] < index_mcp['x']
        
        return fingers_closed and thumb_across
    def _is_I_shape(self, landmarks):
        """Only pinky extended"""
        pinky_extended = self._is_finger_extended(landmarks, 20, 18)
        others_closed = all([
            not self._is_finger_extended(landmarks, 8, 6),   # Index
            not self._is_finger_extended(landmarks, 12, 10), # Middle
            not self._is_finger_extended(landmarks, 16, 14)  # Ring
        ])
        return pinky_extended and others_closed
    
    def _is_L_shape(self, landmarks):
        """Thumb and index extended, forming L"""
        # Thumb extended mostly sideways relative to its previous joint
        thumb_dx = landmarks[4]['x'] - landmarks[3]['x']
        thumb_extended = abs(thumb_dx) > 0.12
        index_extended = self._is_finger_extended(landmarks, 8, 6)
        others_closed = all([
            not self._is_finger_extended(landmarks, 12, 10), # Middle
            not self._is_finger_extended(landmarks, 16, 14), # Ring
            not self._is_finger_extended(landmarks, 20, 18)  # Pinky
        ])
        return thumb_extended and index_extended and others_closed
    
    def _is_V_shape(self, landmarks):
        """Index and middle extended (peace sign)"""
        index_extended = self._is_finger_extended(landmarks, 8, 6)
        middle_extended = self._is_finger_extended(landmarks, 12, 10)
        others_closed = all([
            not self._is_finger_extended(landmarks, 16, 14), # Ring
            not self._is_finger_extended(landmarks, 20, 18)  # Pinky
        ])
        return index_extended and middle_extended and others_closed