import customtkinter as ctk
from database.db_manager import DBManager

class SignLearnApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("SignLearn - ASL Learning Platform")
        # Start with a sensible default size but adapt to screen resolution
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Use 80% of the available screen space
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.geometry(f"{window_width}x{window_height}")
        # Allow resizing and make content expand with the window
        self.minsize(1200, 700)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize database
        self.db = DBManager()
        
        # Current user
        self.current_user = None
        
        # Container for frames
        self.current_frame = None
        
        # Start with login
        self.switch_frame("login")
    
    def switch_frame(self, frame_name, **kwargs):
        """Switch between different frames"""
        # Destroy current frame
        if self.current_frame:
            self.current_frame.destroy()
        
        # Create new frame based on name
        if frame_name == "login":
            from ui.login_frame import LoginFrame
            self.current_frame = LoginFrame(self, self.db)
        elif frame_name == "dashboard":
            from ui.dashboard_frame import DashboardFrame
            self.current_frame = DashboardFrame(self, self.db, self.current_user)
        elif frame_name == "learning":
            from ui.learning_frame import LearningFrame
            self.current_frame = LearningFrame(self, self.db, self.current_user)
        elif frame_name == "leaderboard":
            from ui.leaderboard_frame import LeaderboardFrame
            self.current_frame = LeaderboardFrame(self, self.db)
        
        self.current_frame.pack(fill="both", expand=True)
    
    def set_user(self, username):
        """Set the current logged-in user"""
        self.current_user = username

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = SignLearnApp()
    app.mainloop()