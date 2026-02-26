import customtkinter as ctk
from tkinter import messagebox

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        container.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            container,
            text="SignLearn",
            font=ctk.CTkFont(size=40, weight="bold")
        )
        title.grid(row=0, column=0, pady=(40, 10))
        
        subtitle = ctk.CTkLabel(
            container,
            text="Learn American Sign Language",
            font=ctk.CTkFont(size=16)
        )
        subtitle.grid(row=1, column=0, pady=(0, 40))
        
        # Username
        self.username_entry = ctk.CTkEntry(
            container,
            placeholder_text="Username",
            width=300,
            height=40
        )
        self.username_entry.grid(row=2, column=0, pady=10)
        
        # Password
        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Password",
            show="*",
            width=300,
            height=40
        )
        self.password_entry.grid(row=3, column=0, pady=10)
        
        # Login button
        login_btn = ctk.CTkButton(
            container,
            text="Login",
            command=self.login,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        login_btn.grid(row=4, column=0, pady=20)
        
        # Register button
        register_btn = ctk.CTkButton(
            container,
            text="Create Account",
            command=self.register,
            width=300,
            height=40,
            fg_color="transparent",
            border_width=2
        )
        register_btn.grid(row=5, column=0, pady=10)
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.login())
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if self.db.authenticate_user(username, password):
            self.parent.set_user(username)
            self.parent.switch_frame("dashboard")
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        if self.db.register_user(username, password):
            messagebox.showinfo("Success", "Account created! Please login.")
            self.password_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Username already exists")