import customtkinter as ctk
import cv2
from PIL import Image
import time
import os
from engine.hand_detector import HandDetector
from engine.gesture_logic import GestureRecognizer

class LearningFrame(ctk.CTkFrame):
    def __init__(self, parent, db, username):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.username = username
        
        # Initialize detection
        self.detector = HandDetector(max_hands=2, detection_confidence=0.7)
        self.recognizer = GestureRecognizer()
        
        # Learning state
        self.current_letter_index = 0
        self.letters = ['A', 'B', 'D', 'E', 'I', 'L', 'V']
        self.score = 0
        
        print(f"Learning sequence: {self.letters}")  # Debug output

        # Load reference images
        self.letter_images = {}
        self.load_letter_images()
        
        # Stability tracking
        self.gesture_start_time = None
        self.last_detected_gesture = None
        self.stability_threshold = 1.5  # seconds
        self.letter_completed = False  # Flag to prevent multiple completions
        
        # Video
        self.cap = None
        self.video_running = False
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0, minsize=350)  # Fixed sidebar width
        self.grid_columnconfigure(1, weight=1)  # Video area expands
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI
        self.create_sidebar()
        self.create_main_area()
        
        # Start video
        self.start_video()
    
    def load_letter_images(self):
        """Load reference images for ASL letters"""
        # Get absolute path to assets directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        images_path = os.path.join(project_root, "assets", "images")
        
        for letter in self.letters:
            image_file = os.path.join(images_path, f"{letter}.png")
            if os.path.exists(image_file):
                try:
                    img = Image.open(image_file)
                    self.letter_images[letter] = ctk.CTkImage(
                        light_image=img,
                        dark_image=img,
                        size=(200, 320)
                    )
                except Exception as e:
                    print(f"Error loading image for letter {letter}: {e}")
                    self.letter_images[letter] = None
            else:
                print(f"Warning: Image not found for letter {letter}: {image_file}")
                self.letter_images[letter] = None
    
    def create_sidebar(self):
        """Create left sidebar with controls"""
        # Fixed sidebar frame (not scrollable to avoid cutoff issues)
        sidebar = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color=("gray90", "gray17"))
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Use a scrollable inner frame so all controls remain accessible on smaller screens
        inner_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            inner_frame,
            text="🤟 ASL Learning",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Current letter card
        letter_card = ctk.CTkFrame(inner_frame, fg_color=("gray85", "gray25"), corner_radius=15)
        letter_card.pack(fill="x", pady=(0, 15))
        
        self.letter_label = ctk.CTkLabel(
            letter_card,
            text=self.letters[self.current_letter_index],
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color=("#1e40af", "#60a5fa")
        )
        self.letter_label.pack(pady=(15, 5))
        
        ctk.CTkLabel(
            letter_card,
            text="Current Letter",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))
        
        # Reference image card
        ref_card = ctk.CTkFrame(inner_frame, fg_color=("gray85", "gray25"), corner_radius=15)
        ref_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            ref_card,
            text="📷 Reference",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        current_letter = self.letters[self.current_letter_index]
        self.reference_image_label = ctk.CTkLabel(
            ref_card,
            text="" if self.letter_images.get(current_letter) else "No image",
            image=self.letter_images.get(current_letter)
        )
        self.reference_image_label.pack(pady=(0, 15))
        
        # Progress card
        progress_card = ctk.CTkFrame(inner_frame, fg_color=("gray85", "gray25"), corner_radius=15)
        progress_card.pack(fill="x", pady=(0, 15))
        
        progress_header = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_header.pack(fill="x", padx=15, pady=(15, 8))
        
        ctk.CTkLabel(
            progress_header,
            text="📊 Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        self.progress_label = ctk.CTkLabel(
            progress_header,
            text=f"{self.current_letter_index + 1}/{len(self.letters)}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1e40af", "#60a5fa")
        )
        self.progress_label.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(progress_card, height=12)
        self.progress_bar.pack(padx=15, pady=(0, 15), fill="x")
        self.progress_bar.set((self.current_letter_index + 1) / len(self.letters))
        
        # Score card
        score_card = ctk.CTkFrame(inner_frame, fg_color=("#3b82f6", "#2563eb"), corner_radius=15)
        score_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            score_card,
            text="⭐ Score",
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=(15, 0))
        
        self.score_label = ctk.CTkLabel(
            score_card,
            text=str(self.score),
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        self.score_label.pack(pady=(0, 15))
        
        # Stability card
        stability_card = ctk.CTkFrame(inner_frame, fg_color=("gray85", "gray25"), corner_radius=15)
        stability_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            stability_card,
            text="⏱️ Hold Steady",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 10))
        
        self.stability_bar = ctk.CTkProgressBar(
            stability_card, 
            height=14,
            progress_color=("#10b981", "#059669")
        )
        self.stability_bar.pack(padx=15, fill="x")
        self.stability_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            stability_card,
            text="Show the sign...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=(10, 15))
        
        # Spacer to push button to bottom
        spacer = ctk.CTkFrame(inner_frame, fg_color="transparent", height=20)
        spacer.pack(fill="both", expand=True)
        
        # Back button
        back_btn = ctk.CTkButton(
            inner_frame,
            text="← Back to Dashboard",
            command=self.go_back,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray40"),
            hover_color=("gray80", "gray30"),
            height=45,
            font=ctk.CTkFont(size=14)
        )
        back_btn.pack(fill="x", pady=(0, 10))
    
    def create_main_area(self):
        """Create main video area"""
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("gray85", "gray20"))
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Video label - centered
        self.video_label = ctk.CTkLabel(
            main_frame, 
            text="Starting camera...",
            font=ctk.CTkFont(size=18)
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def start_video(self):
        """Start video capture"""
        self.cap = cv2.VideoCapture(0)
        self.video_running = True
        self.update_video()
    
    def update_video(self):
        """Update video frame"""
        if not self.video_running:
            return
        
        ret, frame = self.cap.read()
        if ret:
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect hands
            hands, frame = self.detector.find_hands(frame)
            
            # Recognize gesture
            detected_gesture = None
            if hands:
                detected_gesture = self.recognizer.recognize(hands[0])
            
            # Update stability
            self.update_stability(detected_gesture)
            
            # Add text overlay
            current_letter = self.letters[self.current_letter_index]
            
            # Background for text visibility
            cv2.rectangle(frame, (10, 10), (280, 80), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, 10), (280, 80), (0, 255, 0), 2)
            cv2.putText(frame, f"Show: {current_letter}", (20, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            
            if detected_gesture:
                color = (0, 255, 0) if detected_gesture == current_letter else (0, 0, 255)
                cv2.rectangle(frame, (10, 90), (350, 140), (0, 0, 0), -1)
                cv2.putText(frame, f"Detected: {detected_gesture}", (20, 130),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)
            
            # Convert to CTkImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Dynamically scale video to fit available space while preserving aspect ratio
            h, w = frame.shape[:2]
            # Try to use the actual size of the video label / parent frame
            available_width = self.video_label.winfo_width()
            available_height = self.video_label.winfo_height()

            # Fallbacks during initial frames before layout is fully calculated
            if available_width <= 1 or available_height <= 1:
                # Account for sidebar (≈350px) and padding
                root_width = self.parent.winfo_width() or 1600
                root_height = self.parent.winfo_height() or 900
                available_width = max(root_width - 400, 800)
                available_height = max(root_height - 120, 600)

            # Leave a little padding inside the main frame
            max_width = max(available_width - 40, 400)
            max_height = max(available_height - 40, 300)

            scale = min(max_width / w, max_height / h)
            display_width = int(w * scale)
            display_height = int(h * scale)
            
            img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(display_width, display_height))
            
            self.video_label.configure(image=photo, text="")
            self.video_label._current_image = photo
        
        # Schedule next update
        self.after(15, self.update_video)
    
    def update_stability(self, detected_gesture):
        """Update stability bar and check if gesture is held"""
        # Don't process if letter is already completed
        if self.letter_completed:
            return
        
        current_letter = self.letters[self.current_letter_index]
        
        if detected_gesture == current_letter:
            if self.last_detected_gesture == detected_gesture and self.gesture_start_time:
                elapsed = time.time() - self.gesture_start_time
                progress = min(elapsed / self.stability_threshold, 1.0)
                self.stability_bar.set(progress)
                
                if progress >= 1.0 and not self.letter_completed:
                    self.on_gesture_complete()
            else:
                self.gesture_start_time = time.time()
                self.last_detected_gesture = detected_gesture
                self.stability_bar.set(0)
                self.status_label.configure(text="Hold it steady!", text_color="#eab308")
        else:
            self.gesture_start_time = None
            self.last_detected_gesture = None
            self.stability_bar.set(0)
            
            if detected_gesture:
                self.status_label.configure(text=f"Wrong: {detected_gesture}", text_color="#ef4444")
            else:
                self.status_label.configure(text="Show the sign...", text_color="gray")
    
    def on_gesture_complete(self):
        """Called when gesture is successfully held"""
        # Prevent multiple calls
        if self.letter_completed:
            return
        
        self.letter_completed = True
        self.score += 10
        self.score_label.configure(text=str(self.score))
        self.status_label.configure(text="✓ Correct!", text_color="#10b981")
        
        self.db.update_score(self.username, self.score)
        
        # Move to next letter after delay
        self.after(1500, self.next_letter)  # Increased delay to 1.5s so user can see the success message
    
    def next_letter(self):
        """Move to next letter"""
        self.current_letter_index += 1
        
        if self.current_letter_index >= len(self.letters):
            self.on_course_complete()
        else:
            next_letter = self.letters[self.current_letter_index]
            self.letter_label.configure(text=next_letter)
            self.progress_bar.set((self.current_letter_index + 1) / len(self.letters))
            self.progress_label.configure(text=f"{self.current_letter_index + 1}/{len(self.letters)}")
            
            if self.letter_images.get(next_letter):
                self.reference_image_label.configure(image=self.letter_images[next_letter], text="")
            else:
                self.reference_image_label.configure(image=None, text="No image")
        
        # Reset tracking state for next letter
        self.gesture_start_time = None
        self.last_detected_gesture = None
        self.letter_completed = False  # Reset completion flag
        self.stability_bar.set(0)
        self.status_label.configure(text="Show the sign...", text_color="gray")
    
    def on_course_complete(self):
        """Called when all letters are completed"""
        self.video_running = False
        if self.cap:
            self.cap.release()
        
        # Clear video and show completion
        self.video_label.configure(image=None, text="")
        
        completion_frame = ctk.CTkFrame(self.video_label.master, fg_color=("gray80", "gray25"), corner_radius=20)
        completion_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            completion_frame,
            text="🎉",
            font=ctk.CTkFont(size=72)
        ).pack(pady=(50, 20), padx=100)
        
        ctk.CTkLabel(
            completion_frame,
            text="Course Complete!",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            completion_frame,
            text=f"Final Score: {self.score} pts",
            font=ctk.CTkFont(size=22),
            text_color=("#1e40af", "#60a5fa")
        ).pack(pady=10)
        
        ctk.CTkButton(
            completion_frame,
            text="Back to Dashboard",
            command=self.go_back,
            width=220,
            height=50,
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8"),
            corner_radius=12,
            font=ctk.CTkFont(size=16)
        ).pack(pady=(25, 50))
    
    def go_back(self):
        """Return to dashboard"""
        self.video_running = False
        if self.cap:
            self.cap.release()
        self.detector.release()
        self.parent.switch_frame("dashboard")