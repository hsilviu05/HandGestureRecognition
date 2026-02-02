import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import random
import time
from database import Database
import os


# --- CONFIGURARE ASPECT ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SignLearnApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SignLearn - Licență Informatică 2026")
        self.geometry("1200x800")
        self.db = Database()
        self.current_user = None

        # --- LOGICA DE JOC ---
        self.alphabet = ["L", "V", "A", "I"]
        self.target_letter = random.choice(self.alphabet)
        self.score = 0
        self.is_waiting = False # Pentru pauza dintre litere

        # --- INITIALIZARE MEDIAPIPE ---
        base_options = python.BaseOptions(model_asset_path='assets/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        self.detector = vision.HandLandmarker.create_from_options(options)

        # --- UI SETUP ---
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        
        self.cap = None
        self.show_login_page()

    def show_login_page(self):
        for widget in self.container.winfo_children(): widget.destroy()
        
        login_frame = ctk.CTkFrame(self.container, width=400, height=500)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(login_frame, text="SignLearn", font=("Helvetica", 32, "bold")).pack(pady=(40, 10))
        ctk.CTkLabel(login_frame, text="Sistem Educațional pentru Limbajul Semnelor", font=("Helvetica", 14)).pack(pady=10)
        
        self.user_entry = ctk.CTkEntry(login_frame, placeholder_text="Utilizator", width=250)
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(login_frame, placeholder_text="Parolă", show="*", width=250)
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(login_frame, text="Logare", command=self.handle_login).pack(pady=10)
        ctk.CTkButton(login_frame, text="Creează Cont", fg_color="transparent", border_width=2, command=self.handle_register).pack(pady=5)

    def handle_login(self):
        user = self.user_entry.get()
        pw = self.pass_entry.get()
        result = self.db.login_user(user, pw)
        if result:
            self.current_user = user
            self.show_main_page()
        else:
            print("Eroare: Utilizator sau parolă incorectă")

    def handle_register(self):
        user = self.user_entry.get()
        pw = self.pass_entry.get()
        if self.db.register_user(user, pw):
            print("Cont creat cu succes!")
        else:
            print("Eroare: Utilizatorul există deja")

    def show_main_page(self):
        for widget in self.container.winfo_children(): widget.destroy()

        # SIDEBAR
        sidebar = ctk.CTkFrame(self.container, width=200, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(sidebar, text="MENIU", font=("Helvetica", 18, "bold")).pack(pady=20)
        ctk.CTkButton(sidebar, text="Curs Interactiv", fg_color="gray30").pack(pady=10, padx=10)
        ctk.CTkButton(sidebar, text="Progresul Meu").pack(pady=10, padx=10)
        ctk.CTkButton(sidebar, text="Ieșire", command=self.on_closing, fg_color="#922b21").pack(side="bottom", pady=20, padx=10)

        # PANOU INFO (SUS)
        self.info_frame = ctk.CTkFrame(self.container, height=120)
        self.info_frame.pack(side="top", fill="x", padx=20, pady=(20, 10))

        self.task_label = ctk.CTkLabel(self.info_frame, 
                                       text=f"ARATĂ LITERA: {self.target_letter}", 
                                       font=("Helvetica", 28, "bold"))
        self.task_label.pack(pady=10)

        self.score_label = ctk.CTkLabel(self.info_frame, text=f"Scor curent: {self.score}", font=("Helvetica", 16))
        self.score_label.pack()

        # ZONA VIDEO
        self.video_label = ctk.CTkLabel(self.container, text="", corner_radius=15)
        self.video_label.pack(side="top", fill="both", expand=True, padx=20, pady=10)

        self.start_camera()

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def get_hand_gesture(self, hand_landmarks):
        """Logica geometrică pentru recunoașterea degetelor"""
        tip_ids = [4, 8, 12, 16, 20]
        fingers = []

        # Deget Mare (Thumb)
        if hand_landmarks[tip_ids[0]].x < hand_landmarks[tip_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # Celelalte 4 degete (Index, Middle, Ring, Pinky)
        for i in range(1, 5):
            if hand_landmarks[tip_ids[i]].y < hand_landmarks[tip_ids[i] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        # Mapare combinații la litere
        if fingers == [1, 1, 0, 0, 0]: return "L"
        if fingers == [0, 1, 1, 0, 0]: return "V"
        if fingers == [0, 0, 0, 0, 0]: return "A"
        if fingers == [0, 0, 0, 0, 1]: return "I"
        return None

    def update_frame(self):
        success, frame = self.cap.read()
        if not success: return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Procesare MediaPipe
        result = self.detector.detect(mp_image)

        if result.hand_landmarks and not self.is_waiting:
            current_hand = result.hand_landmarks[0]
            detected_gesture = self.get_hand_gesture(current_hand)

            # Verificare succes
            if detected_gesture == self.target_letter:
                self.handle_success()

            # Desenare schelet mână pe frame-ul OpenCV
            h, w, _ = frame.shape
            for lm in current_hand:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # Conversie frame pentru CustomTkinter
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(720, 540))
        
        self.video_label.configure(image=img_tk)
        self.video_label.image = img_tk

        self.after(10, self.update_frame)

    def handle_success(self):
        self.is_waiting = True
        self.score += 10
        self.score_label.configure(text=f"Scor curent: {self.score}")
        self.task_label.configure(text="CORECT! REZULTAT VALIDAT", text_color="#27ae60")
        
        # Pauză de 2 secunde înainte de următoarea literă
        self.after(2000, self.reset_task)

    def reset_task(self):
        self.target_letter = random.choice(self.alphabet)
        self.task_label.configure(text=f"ARATĂ LITERA: {self.target_letter}", text_color="white")
        self.is_waiting = False

    def on_closing(self):
        if self.cap:
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = SignLearnApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()