import customtkinter as ctk
from typing import Callable, Optional, Tuple

class CustomButton(ctk.CTkButton):
    """Enhanced button with consistent styling"""
    
    def __init__(
        self,
        parent,
        text: str,
        command: Callable,
        variant: str = "primary",  # primary, secondary, danger, success
        **kwargs
    ):
        # Color schemes
        colors = {
            "primary": ("#3b82f6", "#2563eb"),
            "secondary": ("#6b7280", "#4b5563"),
            "danger": ("#dc2626", "#b91c1c"),
            "success": ("#10b981", "#059669"),
            "outline": ("transparent", "#3b82f6")
        }
        
        fg_color, hover_color = colors.get(variant, colors["primary"])
        
        # Default styling
        defaults = {
            "corner_radius": 8,
            "height": 45,
            "font": ctk.CTkFont(size=14, weight="bold"),
            "fg_color": fg_color,
            "hover_color": hover_color
        }
        
        # Add border for outline variant
        if variant == "outline":
            defaults["border_width"] = 2
            defaults["border_color"] = "#3b82f6"
        
        # Merge with custom kwargs
        defaults.update(kwargs)
        
        super().__init__(parent, text=text, command=command, **defaults)


class Card(ctk.CTkFrame):
    """Card container with shadow effect"""
    
    def __init__(
        self,
        parent,
        title: Optional[str] = None,
        **kwargs
    ):
        defaults = {
            "corner_radius": 12,
            "border_width": 1,
            "border_color": "#3b3b3b"
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        if title:
            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            self.title_label.pack(pady=(20, 10), padx=20, anchor="w")


class StatCard(ctk.CTkFrame):
    """Card for displaying statistics"""
    
    def __init__(
        self,
        parent,
        label: str,
        value: str,
        icon: str = "",
        color: str = "#3b82f6",
        **kwargs
    ):
        defaults = {
            "corner_radius": 12,
            "border_width": 2,
            "border_color": color,
            "fg_color": "transparent"
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        # Icon
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=ctk.CTkFont(size=32)
            )
            icon_label.pack(pady=(20, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=5)
        
        # Label
        label_label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        label_label.pack(pady=(5, 20))


class ProgressCard(ctk.CTkFrame):
    """Card with progress bar"""
    
    def __init__(
        self,
        parent,
        title: str,
        current: int,
        total: int,
        **kwargs
    ):
        defaults = {
            "corner_radius": 12,
            "fg_color": "#2b2b2b"
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Progress text
        progress_text = ctk.CTkLabel(
            self,
            text=f"{current} / {total}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        progress_text.pack(pady=5, padx=20, anchor="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=(5, 20), padx=20, fill="x")
        self.progress_bar.set(current / total if total > 0 else 0)
    
    def update_progress(self, current: int, total: int):
        """Update progress bar value"""
        self.progress_bar.set(current / total if total > 0 else 0)


class IconButton(ctk.CTkButton):
    """Button with icon and text"""
    
    def __init__(
        self,
        parent,
        text: str,
        icon: str,
        command: Callable,
        **kwargs
    ):
        full_text = f"{icon}  {text}"
        
        defaults = {
            "corner_radius": 10,
            "height": 50,
            "font": ctk.CTkFont(size=14),
            "anchor": "w",
            "fg_color": "#2b2b2b",
            "hover_color": "#3b3b3b"
        }
        defaults.update(kwargs)
        
        super().__init__(parent, text=full_text, command=command, **defaults)


class InfoBox(ctk.CTkFrame):
    """Information box with icon"""
    
    def __init__(
        self,
        parent,
        message: str,
        box_type: str = "info",  # info, success, warning, error
        **kwargs
    ):
        # Color schemes
        colors = {
            "info": ("#3b82f6", "#1e40af"),
            "success": ("#10b981", "#065f46"),
            "warning": ("#f59e0b", "#92400e"),
            "error": ("#dc2626", "#7f1d1d")
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠️",
            "error": "✕"
        }
        
        color, bg_color = colors.get(box_type, colors["info"])
        icon = icons.get(box_type, icons["info"])
        
        defaults = {
            "corner_radius": 8,
            "border_width": 2,
            "border_color": color,
            "fg_color": bg_color
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(pady=15, padx=15, fill="both", expand=True)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=ctk.CTkFont(size=20),
            width=30
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=400,
            justify="left"
        )
        message_label.pack(side="left", fill="both", expand=True)


class CustomEntry(ctk.CTkEntry):
    """Enhanced entry field with label"""
    
    def __init__(
        self,
        parent,
        label: str,
        placeholder: str = "",
        show: str = "",
        **kwargs
    ):
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Label
        label_widget = ctk.CTkLabel(
            self.container,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.pack(fill="x", pady=(0, 5))
        
        # Entry defaults
        defaults = {
            "height": 40,
            "corner_radius": 8,
            "placeholder_text": placeholder,
            "show": show
        }
        defaults.update(kwargs)
        
        super().__init__(self.container, **defaults)
        self.pack(fill="x")
    
    def pack(self, **kwargs):
        """Override pack to pack the container"""
        self.container.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        """Override grid to grid the container"""
        self.container.grid(**kwargs)
        return self


class BadgeLabel(ctk.CTkLabel):
    """Badge/pill shaped label"""
    
    def __init__(
        self,
        parent,
        text: str,
        color: str = "#3b82f6",
        **kwargs
    ):
        defaults = {
            "corner_radius": 12,
            "fg_color": color,
            "font": ctk.CTkFont(size=11, weight="bold"),
            "padx": 12,
            "pady": 4,
            "text_color": "white"
        }
        defaults.update(kwargs)
        
        super().__init__(parent, text=text, **defaults)


class ToggleSwitch(ctk.CTkSwitch):
    """Toggle switch with label"""
    
    def __init__(
        self,
        parent,
        label: str,
        command: Optional[Callable] = None,
        **kwargs
    ):
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Label
        label_widget = ctk.CTkLabel(
            self.container,
            text=label,
            font=ctk.CTkFont(size=14)
        )
        label_widget.pack(side="left", padx=(0, 20))
        
        # Switch
        defaults = {
            "command": command
        }
        defaults.update(kwargs)
        
        super().__init__(self.container, text="", **defaults)
        self.pack(side="right")
    
    def pack(self, **kwargs):
        """Override pack to pack the container"""
        self.container.pack(**kwargs)
        return self
    
    def grid(self, **kwargs):
        """Override grid to grid the container"""
        self.container.grid(**kwargs)
        return self


class Table(ctk.CTkFrame):
    """Simple table widget"""
    
    def __init__(
        self,
        parent,
        headers: list,
        data: list,
        **kwargs
    ):
        defaults = {
            "corner_radius": 10
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        # Configure columns
        for i in range(len(headers)):
            self.grid_columnconfigure(i, weight=1)
        
        # Header row
        header_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        header_frame.grid(row=0, column=0, columnspan=len(headers), sticky="ew", padx=2, pady=2)
        
        for i, header in enumerate(headers):
            header_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold")
            ).grid(row=0, column=i, padx=15, pady=12)
        
        # Data rows
        for row_idx, row_data in enumerate(data, start=1):
            row_color = "#1f1f1f" if row_idx % 2 == 0 else "#2b2b2b"
            row_frame = ctk.CTkFrame(self, fg_color=row_color)
            row_frame.grid(row=row_idx, column=0, columnspan=len(headers), sticky="ew", padx=2, pady=1)
            
            for col_idx, cell_data in enumerate(row_data):
                row_frame.grid_columnconfigure(col_idx, weight=1)
                ctk.CTkLabel(
                    row_frame,
                    text=str(cell_data),
                    font=ctk.CTkFont(size=12)
                ).grid(row=0, column=col_idx, padx=15, pady=10)


class LoadingSpinner(ctk.CTkLabel):
    """Animated loading spinner"""
    
    def __init__(self, parent, **kwargs):
        defaults = {
            "text": "⟳",
            "font": ctk.CTkFont(size=32)
        }
        defaults.update(kwargs)
        
        super().__init__(parent, **defaults)
        
        self.is_spinning = False
        self.rotation = 0
    
    def start(self):
        """Start spinning animation"""
        self.is_spinning = True
        self._animate()
    
    def stop(self):
        """Stop spinning animation"""
        self.is_spinning = False
    
    def _animate(self):
        """Animation loop"""
        if not self.is_spinning:
            return
        
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.configure(text=spinners[self.rotation % len(spinners)])
        self.rotation += 1
        
        self.after(100, self._animate)


class Modal(ctk.CTkToplevel):
    """Modal dialog window"""
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        buttons: list = None,  # List of (text, command) tuples
        **kwargs
    ):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x250")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
