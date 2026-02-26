import customtkinter as ctk

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, db, username):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.username = username
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top bar with user info
        self.create_top_bar()
        
        # Main content area
        self.create_main_content()
    
    def create_top_bar(self):
        """Create top navigation bar"""
        top_bar = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=("gray90", "gray17"))
        top_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        top_bar.grid_columnconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            top_bar,
            text="🤟 SignLearn Dashboard",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        # User info logout and exit
        user_info = self.db.get_user_info(self.username)
        score = user_info[1] if user_info else 0
        
        user_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        user_frame.grid(row=0, column=2, padx=30, pady=20, sticky="e")
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.username}  |  ⭐ {score} pts",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        user_label.grid(row=0, column=0, padx=(0, 20))
        
        logout_btn = ctk.CTkButton(
            user_frame,
            text="Logout",
            command=self.logout,
            width=100,
            height=35,
            fg_color="#6b7280",
            hover_color="#4b5563",
            corner_radius=8
        )
        logout_btn.grid(row=0, column=1)

        exit_btn = ctk.CTkButton(
            user_frame,
            text="Exit",
            command=self.parent.destroy,
            width=100,
            height=35,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=8
        )
        exit_btn.grid(row=0, column=2, padx=(20, 0))

    
    def create_main_content(self):
        """Create main dashboard content"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure(0, weight=2)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Learning card
        learning_card = self.create_card(
            main_frame,
            "📚",
            "Start Learning",
            "Practice ASL alphabet signs\nwith real-time camera feedback",
            self.open_learning,
            "#3b82f6"
        )
        learning_card.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Leaderboard card
        leaderboard_card = self.create_card(
            main_frame,
            "🏆",
            "Leaderboard",
            "See top learners and\ncompare your progress",
            self.open_leaderboard,
            "#10b981"
        )
        leaderboard_card.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Stats card
        stats_card = self.create_stats_card(main_frame)
        stats_card.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew")
    
    def create_card(self, parent, icon, title, description, command, color):
        """Create a dashboard card button"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=20,
            fg_color=color,
            cursor="hand2"
        )
        
        # Make the entire card clickable
        card.bind("<Button-1>", lambda e: command())
        
        # Card content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)
        content_frame.bind("<Button-1>", lambda e: command())
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=ctk.CTkFont(size=48),
            text_color="white"
        )
        icon_label.pack(pady=(20, 10))
        icon_label.bind("<Button-1>", lambda e: command())
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(0, 10))
        title_label.bind("<Button-1>", lambda e: command())
        
        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            text_color="#e0e0e0",
            justify="center"
        )
        desc_label.pack(pady=(0, 20))
        desc_label.bind("<Button-1>", lambda e: command())
        
        # Hover effects
        def on_enter(e):
            card.configure(fg_color=self.darken_color(color))
        
        def on_leave(e):
            card.configure(fg_color=color)
        
        for widget in [card, content_frame, icon_label, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        return card
    
    def create_stats_card(self, parent):
        """Create statistics card"""
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color=("gray85", "gray20"))
        
        title = ctk.CTkLabel(
            card,
            text="📊 Your Statistics",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(25, 15))
        
        # Get user info
        user_info = self.db.get_user_info(self.username)
        score = user_info[1] if user_info else 0
        
        # Get leaderboard position
        leaderboard = self.db.get_leaderboard(100)
        position = next((i + 1 for i, (user, _) in enumerate(leaderboard) if user == self.username), "N/A")
        
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(pady=20, padx=60, fill="x")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Best Score
        self.create_stat_item(stats_frame, "Best Score", str(score), 0, "🎯")
        
        # Rank
        self.create_stat_item(stats_frame, "Global Rank", f"#{position}", 1, "🌍")
        
        # Letters Learned
        letters_learned = min(score // 10, 6)
        self.create_stat_item(stats_frame, "Letters Learned", f"{letters_learned}/6", 2, "✅")
        
        return card
    
    def create_stat_item(self, parent, label, value, column, icon=""):
        """Create a single stat item"""
        frame = ctk.CTkFrame(parent, fg_color=("gray80", "gray25"), corner_radius=15)
        frame.grid(row=0, column=column, padx=15, pady=10, sticky="nsew")
        
        inner_frame = ctk.CTkFrame(frame, fg_color="transparent")
        inner_frame.pack(expand=True, pady=20, padx=20)
        
        if icon:
            icon_label = ctk.CTkLabel(
                inner_frame,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack()
        
        value_label = ctk.CTkLabel(
            inner_frame,
            text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("#1e40af", "#60a5fa")
        )
        value_label.pack(pady=(5, 0))
        
        label_label = ctk.CTkLabel(
            inner_frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        label_label.pack()
    
    def darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * 0.85), int(g * 0.85), int(b * 0.85)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def open_learning(self):
        """Open learning module"""
        self.parent.switch_frame("learning")
    
    def open_leaderboard(self):
        """Open leaderboard"""
        self.parent.switch_frame("leaderboard")
    
    def logout(self):
        """Logout user"""
        self.parent.set_user(None)
        self.parent.switch_frame("login")