import customtkinter as ctk

class LeaderboardFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_header()
        self.create_leaderboard()
    
    def create_header(self):
        """Create header with title and back button"""
        header = ctk.CTkFrame(self, height=100, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        header.grid_columnconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            header,
            text="🏆 Leaderboard",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")
        
        # Back button
        back_btn = ctk.CTkButton(
            header,
            text="← Back",
            command=self.go_back,
            width=120,
            height=40,
            fg_color="transparent",
            border_width=2
        )
        back_btn.grid(row=0, column=2, sticky="e")
    
    def create_leaderboard(self):
        """Create leaderboard table"""
        # Container
        container = ctk.CTkFrame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 40))
        container.grid_columnconfigure(0, weight=1)
        
        # Table header
        header_frame = ctk.CTkFrame(container, fg_color="#2b2b2b", corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="Rank",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80
        ).grid(row=0, column=0, padx=20, pady=15)
        
        ctk.CTkLabel(
            header_frame,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        ).grid(row=0, column=1, padx=20, pady=15, sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Score",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100
        ).grid(row=0, column=2, padx=20, pady=15)
        
        # Scrollable frame for entries (fill remaining vertical space)
        scrollable = ctk.CTkScrollableFrame(container)
        scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scrollable.grid_columnconfigure(0, weight=1)
        
        # Get leaderboard data
        leaderboard = self.db.get_leaderboard(20)
        
        # Create rows
        for rank, (username, score) in enumerate(leaderboard, 1):
            self.create_leaderboard_row(scrollable, rank, username, score)
        
        if not leaderboard:
            no_data = ctk.CTkLabel(
                scrollable,
                text="No players yet. Be the first!",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_data.grid(row=0, column=0, pady=50)
    
    def create_leaderboard_row(self, parent, rank, username, score):
        """Create a single leaderboard row"""
        # Determine color based on rank
        if rank == 1:
            medal = "🥇"
            fg_color = "#fbbf24"
        elif rank == 2:
            medal = "🥈"
            fg_color = "#94a3b8"
        elif rank == 3:
            medal = "🥉"
            fg_color = "#cd7f32"
        else:
            medal = ""
            fg_color = "#3b3b3b" if rank % 2 == 0 else "#2b2b2b"
        
        row_frame = ctk.CTkFrame(parent, fg_color=fg_color, corner_radius=8)
        row_frame.grid(row=rank-1, column=0, sticky="ew", pady=5)
        row_frame.grid_columnconfigure(1, weight=1)
        
        # Rank
        rank_text = f"{medal} #{rank}" if medal else f"#{rank}"
        ctk.CTkLabel(
            row_frame,
            text=rank_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80
        ).grid(row=0, column=0, padx=20, pady=12)
        
        # Username
        ctk.CTkLabel(
            row_frame,
            text=username,
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).grid(row=0, column=1, padx=20, pady=12, sticky="w")
        
        # Score
        ctk.CTkLabel(
            row_frame,
            text=str(score),
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100
        ).grid(row=0, column=2, padx=20, pady=12)
    
    def go_back(self):
        """Return to dashboard"""
        self.parent.switch_frame("dashboard")