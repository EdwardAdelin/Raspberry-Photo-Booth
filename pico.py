import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os
import time
from tkinter import font as tkFont


class PhotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POLI International Fest")
        self.root.attributes('-fullscreen', True)  # Fullscreen mode
        
        # Define color scheme
        self.primary_color = "#1A237E"  # Deep blue
        self.accent_color = "#FF4081"   # Pink accent
        self.bg_color = "#F5F5F5"       # Light gray background
        self.text_color = "#212121"     # Dark text
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Create custom fonts
        self.title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=24)
        self.countdown_font = tkFont.Font(family="Helvetica", size=80, weight="bold")
        
        # Camera setup
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Force Video4Linux2
        
        # Header with title
        self.header = tk.Frame(root, bg=self.primary_color, height=100)
        self.header.pack(fill=tk.X, padx=0, pady=0)
        
        self.title_label = tk.Label(
            self.header, 
            text="POLI International Fest", 
            font=self.title_font, 
            fg="white", 
            bg=self.primary_color
        )
        self.title_label.pack(pady=20)
        
        # Main content frame - use more space
        self.content_frame = tk.Frame(root, bg=self.bg_color)
        self.content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)  # Reduced padding
        
        # Video frame with stylish border - larger relative size
        self.video_frame = tk.Frame(
            self.content_frame, 
            bg=self.primary_color,
            highlightbackground=self.accent_color,
            highlightthickness=5,
            padx=5,  # Reduced inner padding
            pady=5   # Reduced inner padding
        )
        self.video_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)  # Reduced outer padding
        
        # Canvas for video display
        self.canvas = tk.Label(self.video_frame, bg="black")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Countdown label with animation effect
        self.countdown_label = tk.Label(
            root, 
            text="", 
            font=self.countdown_font, 
            fg=self.accent_color,
            bg=self.bg_color
        )
        self.countdown_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Button frame with more space
        self.btn_frame = tk.Frame(root, bg=self.bg_color)
        self.btn_frame.pack(pady=30, padx=20, side=tk.BOTTOM, fill=tk.X)
        
        # Styled capture button - SUPER SIZED for touch screens
        self.btn_capture = tk.Button(
            self.btn_frame, 
            text="📸 Take Photo", 
            font=tkFont.Font(family="Helvetica", size=42, weight="bold"),  # Much larger font
            command=self.start_countdown, 
            bg=self.accent_color,
            fg="white",
            activebackground=self.primary_color,
            activeforeground="white",
            relief=tk.RAISED,
            borderwidth=4,  # Thicker border
            padx=60,  # Much more horizontal padding
            pady=30,  # Much more vertical padding
            cursor="hand2"
        )
        # Center the button with more vertical space
        self.btn_capture.pack(pady=30, expand=True, ipadx=20, ipady=10)  # Added internal padding
        

        self.overlay = self.load_overlay()  # Load overlay image
        self.update_video_stream()

    def load_overlay(self):
        """ Load the overlay image and resize it to be smaller """
        overlay_path = os.path.expanduser("~/Pictures/overlay.png")
        if os.path.exists(overlay_path):
            overlay = Image.open(overlay_path).convert("RGBA")
            overlay = overlay.resize((150, 150), Image.LANCZOS)
            return overlay
        else:
            print("Overlay not found! Captured images will not have an overlay.")
            return None

    def update_video_stream(self):
        """ Continuously update video preview with proper sizing """
        ret, frame = self.cap.read()
        if ret:
            # Flip the frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get the current size of the video frame container
            container_width = self.video_frame.winfo_width()
            container_height = self.video_frame.winfo_height()
            
            # If container size is valid (not during initialization)
            if container_width > 10 and container_height > 10:
                # Get original frame dimensions
                frame_height, frame_width = frame.shape[:2]
                
                # Calculate scaling to fit container while maintaining aspect ratio
                scale_width = container_width / frame_width
                scale_height = container_height / frame_height
                scale = min(scale_width, scale_height) * 0.95  # Use 95% of available space
                
                # Calculate new dimensions
                new_width = int(frame_width * scale)
                new_height = int(frame_height * scale)
                
                # Resize the frame
                frame_resized = cv2.resize(frame, (new_width, new_height))
                
                # Convert to PIL Image for display
                img = Image.fromarray(frame_resized)
                photo_img = ImageTk.PhotoImage(img)
                
                # Update the image in the label
                self.canvas.config(image=photo_img)
                self.canvas.image = photo_img  # Keep reference
            else:
                # During initialization just show the frame
                img = Image.fromarray(frame)
                photo_img = ImageTk.PhotoImage(img)
                self.canvas.config(image=photo_img)
                self.canvas.image = photo_img
                
        # Schedule next update
        self.root.after(10, self.update_video_stream)

    def start_countdown(self, count=5):
        """ Show countdown before capturing photo with animation """
        self.btn_capture.config(state=tk.DISABLED)  # Disable button during countdown
        
        if count > 0:
            # Make countdown label visible and update text
            self.countdown_label.config(text=str(count))
            
            # Animate the countdown (grow and shrink)
            self.animate_countdown(count)
            
            self.root.after(1000, self.start_countdown, count - 1)
        else:
            self.countdown_label.config(text="SMILE! 😊")
            self.root.after(500, self.clear_countdown)
            self.capture_photo()
    
    def animate_countdown(self, count):
        """Animate the countdown label with a pulsing effect"""
        # Initial size
        size = 80
        
        def grow():
            nonlocal size
            if size < 120:
                size += 5
                self.countdown_font.configure(size=size)
                self.countdown_label.config(font=self.countdown_font)
                self.root.after(50, grow)
            else:
                shrink()
                
        def shrink():
            nonlocal size
            if size > 80:
                size -= 5
                self.countdown_font.configure(size=size)
                self.countdown_label.config(font=self.countdown_font)
                self.root.after(50, shrink)
                
        grow()
    
    def clear_countdown(self):
        """Clear the countdown text and re-enable the button"""
        self.countdown_label.config(text="")
        self.btn_capture.config(state=tk.NORMAL)

    def capture_photo(self):
        """ Capture a photo from the camera and apply overlay """
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Mirror effect
            self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(self.photo).convert("RGBA")  # Convert to RGBA for overlay support

            # Apply overlay if available
            if self.overlay:
                img = self.apply_overlay(img, self.overlay)

            # Save photo automatically
            self.save_photo(img)

            # Open the preview window
            self.show_preview_window(img)

    def apply_overlay(self, img, overlay):
        """ Apply overlay image in the lower-left corner """
        img_w, img_h = img.size
        overlay_w, overlay_h = overlay.size

        position = (10, img_h - overlay_h - 10)  # 10px padding from bottom-left
        combined = Image.new("RGBA", img.size, (0, 0, 0, 0))
        combined.paste(img, (0, 0))
        combined.paste(overlay, position, overlay)  # Paste overlay with transparency
        return combined

    def save_photo(self, img):
        """ Save the captured photo with overlay to the Pictures folder """
        photo_name = f"photo_{int(time.time())}.png"
        photo_path = os.path.expanduser(f"~/Pictures/{photo_name}")  # Unique filename
        
        img.save(photo_path)
        print(f"Photo saved to {photo_path}")
        self.photo_path = photo_path  # Save the path for later use (e.g., printing)

    def show_preview_window(self, img):
        """ Show a new window with the preview image and print option """
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Photo")
        preview_window.configure(bg=self.bg_color)
        
        # Make preview window fullscreen for better visibility
        preview_window.attributes('-fullscreen', True)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Create header in preview window
        preview_header = tk.Frame(preview_window, bg=self.primary_color, height=80)
        preview_header.pack(fill=tk.X, padx=0, pady=0)
        
        preview_title = tk.Label(
            preview_header, 
            text="Your Photo", 
            font=("Helvetica", 32, "bold"),
            fg="white", 
            bg=self.primary_color
        )
        preview_title.pack(pady=15, side=tk.LEFT, padx=(20, 0))
        
        # Add exit button to header
        btn_exit = tk.Button(
            preview_header, 
            text="Return to Main", 
            command=preview_window.destroy,  # This will only close the preview window
            font=("Helvetica", 16),
            bg="#F44336",  # Red
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=2
        )
        btn_exit.pack(side=tk.RIGHT, padx=20, pady=15)

        # Content frame - limit maximum height to ensure buttons remain visible
        preview_content = tk.Frame(preview_window, bg=self.bg_color)
        preview_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Display the photo with a nice border - LARGER
        photo_frame = tk.Frame(
            preview_content, 
            bg="white",
            highlightbackground=self.accent_color,
            highlightthickness=5,  # Thicker border
            padx=15,
            pady=15
        )
        photo_frame.pack(expand=True, pady=20)

        # Calculate proper size while maintaining aspect ratio - INCREASED SIZE
        img_w, img_h = img.size
        # Increase max_size for a bigger photo (70% of screen height)
        max_size = int(screen_height * 0.7)  
        ratio = min(max_size/img_w, max_size/img_h)
        new_size = (int(img_w * ratio), int(img_h * ratio))
        
        img_resized = img.resize(new_size)
        img_tk = ImageTk.PhotoImage(img_resized)

        label = tk.Label(photo_frame, image=img_tk, bg="white")
        label.image = img_tk  # Keep a reference to the image
        label.pack(pady=10, padx=10)

        # Button frame - pack with fixed position at bottom to ensure visibility
        # Increased height for larger buttons
        button_frame = tk.Frame(preview_window, bg=self.bg_color, height=200)
        button_frame.pack(side=tk.BOTTOM, pady=15, fill=tk.X)

        # Action label to make it clearer
        action_label = tk.Label(
            button_frame,
            text="What would you like to do?",
            font=("Helvetica", 25),  # Larger font
            fg=self.text_color,
            bg=self.bg_color
        )
        action_label.pack(pady=(0, 15))

        # Button container for better layout
        btn_container = tk.Frame(button_frame, bg=self.bg_color)
        btn_container.pack(fill=tk.X)

        # Print button - SUPER SIZED for touch screens to match Take Photo button
        btn_print = tk.Button(
            btn_container, 
            text="🖨️ Print Photo", 
            font=("Helvetica", 42, "bold"),  # Increased to match Take Photo button
            command=lambda: self.print_photo(preview_window),
            bg="#4CAF50",  # Green
            fg="white",
            activebackground="#388E3C",  # Darker green on hover
            activeforeground="white",
            padx=60,  # Increased to match Take Photo button
            pady=30,  # Increased to match Take Photo button
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=4  # Thicker border to match Take Photo button
        )
        btn_print.pack(side=tk.LEFT, padx=(80, 40), pady=30, expand=True, ipadx=20, ipady=10)  # Added internal padding

        # Retake button - SUPER SIZED for touch screens to match Take Photo button
        btn_retake = tk.Button(
            btn_container, 
            text="🔄 Retake Photo", 
            font=("Helvetica", 42, "bold"),  # Increased to match Take Photo button
            command=lambda: self.retake_photo(preview_window),
            bg="#FF9800",  # Orange
            fg="white",
            activebackground="#F57C00",  # Darker orange on hover
            activeforeground="white",
            padx=60,  # Increased to match Take Photo button
            pady=30,  # Increased to match Take Photo button
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=4  # Thicker border to match Take Photo button
        )
        btn_retake.pack(side=tk.RIGHT, padx=(40, 80), pady=30, expand=True, ipadx=20, ipady=10)  # Added internal padding

    def print_photo(self, preview_window):
        """ Print the saved photo using Linux `lp` command """
        if hasattr(self, 'photo_path'):
            import subprocess
            #replace with printer name on your system
            printer_name = "HP_LaserJet_MFP_M140w_8C2E18_USB"
            photo_path = self.photo_path
            
            # Show printing notification with improved styling
            print_notification = tk.Toplevel(preview_window)
            print_notification.title("Printing")
            print_notification.geometry("400x200")
            print_notification.configure(bg=self.bg_color)
            print_notification.resizable(False, False)
            
            # Centered content frame
            notification_frame = tk.Frame(print_notification, bg=self.bg_color)
            notification_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # Printer icon
            printer_label = tk.Label(
                notification_frame,
                text="🖨️",
                font=("Helvetica", 36),
                fg=self.primary_color,
                bg=self.bg_color
            )
            printer_label.pack(pady=(0, 10))
            
            # Status message
            status_label = tk.Label(
                notification_frame,
                text="Printing your photo...",
                font=("Helvetica", 16, "bold"),
                fg=self.primary_color,
                bg=self.bg_color
            )
            status_label.pack(pady=(0, 5))
            
            # Progress message
            progress = tk.Label(
                notification_frame,
                text="Please wait while your photo is printing",
                font=("Helvetica", 12),
                fg=self.text_color,
                bg=self.bg_color
            )
            progress.pack(pady=5)
            
            self.root.update()
            
            # Print the photo
            subprocess.run(["lp", "-d", printer_name, photo_path])
            
            # Update message after print command is sent
            progress.config(text="Print job sent successfully!")
            
            # Close notification and preview
            self.root.after(2000, print_notification.destroy)
            self.root.after(2500, preview_window.destroy)

    def retake_photo(self, preview_window):
        """ Retake the photo by closing the preview window and starting over """
        preview_window.destroy()  # Close the preview window
        self.start_countdown()  # Start the countdown again to retake the photo


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoApp(root)
    root.mainloop()