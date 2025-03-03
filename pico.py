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
        self.root.title("Photo Booth")
        self.root.attributes('-fullscreen', True)  # Fullscreen mode
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Define color scheme
        self.primary_color = "#1A237E"  # Deep blue
        self.accent_color = "#FF4081"   # Pink accent
        self.bg_color = "#F5F5F5"       # Light gray background
        self.text_color = "#212121"     # Dark text
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Create custom fonts - SCALED BASED ON SCREEN SIZE
        self.title_font = tkFont.Font(family="Helvetica", 
                                     size=max(14, min(36, int(self.screen_height / 20))), 
                                     weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", 
                                      size=max(16, min(42, int(self.screen_height / 16))), 
                                      weight="bold")
        self.countdown_font = tkFont.Font(family="Helvetica", 
                                         size=max(40, min(80, int(self.screen_height / 8))), 
                                         weight="bold")
        
        # Camera setup
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Force Video4Linux2
        # use terminal command if you want list of available cameras and select wanted port
        
        # Header with title - REDUCED HEIGHT FOR SMALL SCREENS
        header_height = min(100, max(60, int(self.screen_height * 0.1)))
        self.header = tk.Frame(root, bg=self.primary_color, height=header_height)
        self.header.pack(fill=tk.X, padx=0, pady=0)
        
        self.title_label = tk.Label(
            self.header, 
            text="Photo Booth", 
            font=self.title_font, 
            fg="white", 
            bg=self.primary_color
        )
        self.title_label.pack(pady=max(5, min(20, int(self.screen_height * 0.02))))
        
        # Main content frame - REDUCED PADDING FOR SMALL SCREENS
        self.content_frame = tk.Frame(root, bg=self.bg_color)
        self.content_frame.pack(expand=True, fill=tk.BOTH, 
                               padx=max(5, min(20, int(self.screen_width * 0.02))), 
                               pady=max(5, min(20, int(self.screen_height * 0.02))))
        
        # Video frame with stylish border
        self.video_frame = tk.Frame(
            self.content_frame, 
            bg=self.primary_color,
            highlightbackground=self.accent_color,
            highlightthickness=3,
            padx=3,  # Minimal padding for small screens
            pady=3   # Minimal padding for small screens
        )
        self.video_frame.pack(expand=True, fill=tk.BOTH, 
                             padx=max(5, min(30, int(self.screen_width * 0.03))), 
                             pady=max(5, min(20, int(self.screen_height * 0.02))))
        
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
        
        # Button frame - REDUCED PADDING FOR SMALL SCREENS
        self.btn_frame = tk.Frame(root, bg=self.bg_color)
        self.btn_frame.pack(
            pady=max(10, min(30, int(self.screen_height * 0.04))), 
            padx=max(10, min(20, int(self.screen_width * 0.02))), 
            side=tk.BOTTOM, 
            fill=tk.X
        )
        
        # Calculate button size based on screen dimensions
        btn_font_size = max(18, min(42, int(self.screen_height / 16)))
        btn_padx = max(20, min(60, int(self.screen_width * 0.06)))
        btn_pady = max(10, min(30, int(self.screen_height * 0.04)))
        
        # Styled capture button - SCALED FOR SCREEN SIZE
        self.btn_capture = tk.Button(
            self.btn_frame, 
            text="📸 Take Photo", 
            font=tkFont.Font(family="Helvetica", size=btn_font_size, weight="bold"),
            command=self.start_countdown, 
            bg=self.accent_color,
            fg="white",
            activebackground=self.primary_color,
            activeforeground="white",
            relief=tk.RAISED,
            borderwidth=3,
            padx=btn_padx,
            pady=btn_pady,
            cursor="hand2"
        )
        # Center the button with scaled padding
        self.btn_capture.pack(
            pady=max(10, min(30, int(self.screen_height * 0.03))), 
            expand=True, 
            ipadx=max(5, min(20, int(self.screen_width * 0.02))), 
            ipady=max(3, min(10, int(self.screen_height * 0.015)))
        )

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
        
        # Force fullscreen using multiple approaches
        preview_window.attributes('-fullscreen', True)
        preview_window.overrideredirect(True)  # Remove window decorations completely
        preview_window.geometry(f"{self.screen_width}x{self.screen_height}+0+0")  # Set exact screen size
        preview_window.focus_set()  # Give window focus
        
        # Create header in preview window - SCALED HEIGHT
        header_height = min(80, max(40, int(self.screen_height * 0.08)))
        preview_header = tk.Frame(preview_window, bg=self.primary_color, height=header_height)
        preview_header.pack(fill=tk.X, padx=0, pady=0)
        
        # SCALED FONT SIZE
        title_size = max(16, min(32, int(self.screen_height / 20)))
        preview_title = tk.Label(
            preview_header, 
            text="Your Photo", 
            font=("Helvetica", title_size, "bold"),
            fg="white", 
            bg=self.primary_color
        )
        preview_title.pack(pady=max(5, min(15, int(self.screen_height * 0.02))), 
                          side=tk.LEFT, 
                          padx=(max(10, min(20, int(self.screen_width * 0.02))), 0))
        
        # Add exit button to header - SCALED SIZE
        exit_btn_font = max(10, min(16, int(self.screen_height / 40)))
        btn_exit = tk.Button(
            preview_header, 
            text="Return to Main", 
            command=preview_window.destroy,
            font=("Helvetica", exit_btn_font),
            bg="#F44336",  # Red
            fg="white",
            padx=max(5, min(15, int(self.screen_width * 0.015))),
            pady=max(3, min(8, int(self.screen_height * 0.012))),
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=2
        )
        btn_exit.pack(side=tk.RIGHT, 
                     padx=max(10, min(20, int(self.screen_width * 0.02))), 
                     pady=max(5, min(15, int(self.screen_height * 0.02))))
        
        # Content frame - SCALED PADDING
        preview_content = tk.Frame(preview_window, bg=self.bg_color)
        preview_content.pack(expand=True, fill=tk.BOTH, 
                            padx=max(5, min(20, int(self.screen_width * 0.02))), 
                            pady=max(5, min(10, int(self.screen_height * 0.015))))
        
        # Display the photo with a nice border - SCALED BORDER AND PADDING
        photo_frame = tk.Frame(
            preview_content, 
            bg="white",
            highlightbackground=self.accent_color,
            highlightthickness=3,
            padx=max(5, min(15, int(self.screen_width * 0.015))),
            pady=max(5, min(15, int(self.screen_height * 0.02)))
        )
        photo_frame.pack(expand=True, pady=max(5, min(20, int(self.screen_height * 0.03))))
        
        # Calculate proper size while maintaining aspect ratio - SCALED MAX SIZE
        img_w, img_h = img.size
        # Set max size to 50% of screen height for small screens (was 70%)
        max_size = int(self.screen_height * 0.5)
        ratio = min(max_size/img_w, max_size/img_h)
        new_size = (int(img_w * ratio), int(img_h * ratio))
        
        img_resized = img.resize(new_size)
        img_tk = ImageTk.PhotoImage(img_resized)
        
        label = tk.Label(photo_frame, image=img_tk, bg="white")
        label.image = img_tk  # Keep a reference to the image
        label.pack(pady=5, padx=5)
        
        # Button frame - REDUCED HEIGHT FOR SMALL SCREENS
        button_frame = tk.Frame(preview_window, bg=self.bg_color, 
                              height=max(100, min(200, int(self.screen_height * 0.25))))
        button_frame.pack(side=tk.BOTTOM, 
                         pady=max(5, min(15, int(self.screen_height * 0.02))), 
                         fill=tk.X)
        
        # SCALED FONT SIZE
        label_size = max(14, min(25, int(self.screen_height / 27)))
        # Action label to make it clearer
        action_label = tk.Label(
            button_frame,
            text="What would you like to do?",
            font=("Helvetica", label_size),
            fg=self.text_color,
            bg=self.bg_color
        )
        action_label.pack(pady=(0, max(5, min(15, int(self.screen_height * 0.02)))))
        
        # Button container for better layout
        btn_container = tk.Frame(button_frame, bg=self.bg_color)
        btn_container.pack(fill=tk.X)
        
        # CALCULATE BUTTON SIZES BASED ON SCREEN SIZE
        btn_font_size = max(16, min(42, int(self.screen_height / 17)))
        btn_padx = max(15, min(60, int(self.screen_width * 0.06)))
        btn_pady = max(10, min(30, int(self.screen_height * 0.04)))
        btn_side_padding = (max(20, min(80, int(self.screen_width * 0.08))), 
                           max(10, min(40, int(self.screen_width * 0.04))))
        
        # Print button - SCALED FOR SMALL SCREENS
        btn_print = tk.Button(
            btn_container, 
            text="🖨️ Print", 
            font=("Helvetica", btn_font_size, "bold"),
            command=lambda: self.print_photo(preview_window),
            bg="#4CAF50",
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            padx=btn_padx,
            pady=btn_pady,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=3
        )
        btn_print.pack(side=tk.LEFT, 
                      padx=btn_side_padding, 
                      pady=max(10, min(30, int(self.screen_height * 0.04))), 
                      expand=True,
                      ipadx=max(5, min(20, int(self.screen_width * 0.02))), 
                      ipady=max(3, min(10, int(self.screen_height * 0.015))))
        
        # Retake button - SCALED FOR SMALL SCREENS
        btn_retake = tk.Button(
            btn_container, 
            text="🔄 Retake", 
            font=("Helvetica", btn_font_size, "bold"),
            command=lambda: self.retake_photo(preview_window),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            activeforeground="white",
            padx=btn_padx,
            pady=btn_pady,
            cursor="hand2",
            relief=tk.RAISED,
            borderwidth=3
        )
        btn_retake.pack(side=tk.RIGHT, 
                       padx=btn_side_padding, 
                       pady=max(10, min(30, int(self.screen_height * 0.04))), 
                       expand=True,
                       ipadx=max(5, min(20, int(self.screen_width * 0.02))), 
                       ipady=max(3, min(10, int(self.screen_height * 0.015))))

    def print_photo(self, preview_window):
        """ Print the saved photo using Linux `lp` command with proper sizing for A4 paper """
        if hasattr(self, 'photo_path'):
            import subprocess
            from PIL import Image
            
            # Get printer name - replace with your actual printer name
            printer_name = "HP_LaserJet_MFP_M140w_8C2E18"
            original_photo_path = self.photo_path
            
            # Show printing notification with improved styling and guaranteed fullscreen
            print_notification = tk.Toplevel(self.root)
            print_notification.title("Printing")
            print_notification.configure(bg=self.bg_color)
            
            # Force fullscreen using multiple approaches
            print_notification.attributes('-fullscreen', True)
            print_notification.overrideredirect(True)  # Remove window decorations
            print_notification.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
            print_notification.focus_set()
            
            # Scale font sizes based on screen dimensions for better readability on small screens
            icon_size = max(24, min(42, int(self.screen_height / 16)))
            title_size = max(14, min(18, int(self.screen_height / 35)))
            text_size = max(10, min(14, int(self.screen_height / 48)))
            
            # Centered content frame
            notification_frame = tk.Frame(print_notification, bg=self.bg_color)
            notification_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # Printer icon
            printer_label = tk.Label(
                notification_frame,
                text="🖨️",
                font=("Helvetica", icon_size),
                fg=self.primary_color,
                bg=self.bg_color
            )
            printer_label.pack(pady=(0, 15))
            
            # Status message with adaptive font size
            status_label = tk.Label(
                notification_frame,
                text="Preparing your photo for printing...",
                font=("Helvetica", title_size, "bold"),
                fg=self.primary_color,
                bg=self.bg_color,
                wraplength=int(self.screen_width * 0.7)  # Allow text wrapping for small screens
            )
            status_label.pack(pady=(0, 10))
            
            # Progress message with adaptive font size
            progress = tk.Label(
                notification_frame,
                text="Please wait...",
                font=("Helvetica", text_size),
                fg=self.text_color,
                bg=self.bg_color,
                wraplength=int(self.screen_width * 0.7)  # Allow text wrapping
            )
            progress.pack(pady=10)
            
            self.root.update()
            
            # Create a print-ready version of the image optimized for A4 paper
            try:
                # A4 paper dimensions in pixels at 300 DPI
                a4_width_px = int(8.27 * 300)  # A4 width: 8.27 inches
                a4_height_px = int(11.69 * 300)  # A4 height: 11.69 inches
                
                # Open the original image
                original_img = Image.open(original_photo_path)
                
                # Create a new A4-sized white image
                a4_img = Image.new('RGB', (a4_width_px, a4_height_px), (255, 255, 255))
                
                # Resize the photo to fit nicely on A4 while maintaining aspect ratio
                # Use 80% of A4 width for the image
                target_width = int(a4_width_px * 0.8)
                aspect_ratio = original_img.height / original_img.width
                target_height = int(target_width * aspect_ratio)
                
                # Ensure height doesn't exceed 80% of A4 height
                if target_height > (a4_height_px * 0.8):
                    target_height = int(a4_height_px * 0.8)
                    target_width = int(target_height / aspect_ratio)
                
                resized_img = original_img.resize((target_width, target_height), Image.LANCZOS)
                
                # Calculate position to center the image on the A4 page
                x_offset = (a4_width_px - target_width) // 2
                y_offset = (a4_height_px - target_height) // 2
                
                # Paste the resized image onto the A4 canvas
                a4_img.paste(resized_img, (x_offset, y_offset))
                
                # Save the print-ready image
                print_ready_path = os.path.splitext(original_photo_path)[0] + "_print.jpg"
                a4_img.save(print_ready_path, quality=95, dpi=(300, 300))
                progress.config(text="Photo prepared for printing!")
                self.root.update()
                
                # Print the formatted image
                status_label.config(text="Sending to printer...")
                progress.config(text="Please wait while your photo is printing")
                self.root.update()
                
                # Print command with specific options for photo printing
                subprocess.run([
                    "lp", 
                    "-d", printer_name,
                    "-o", "fit-to-page=true",
                    "-o", "media=a4",
                    "-o", "print-quality=high",
                    print_ready_path
                ])
                
                # Update message after print command is sent
                status_label.config(text="Print job sent successfully!")
                progress.config(text="You can collect your photo from the printer.")
                
            except Exception as e:
                status_label.config(text="Printing Error")
                progress.config(text=f"Error: {str(e)}")
                
            # Close notification and preview after delay
            self.root.after(3000, print_notification.destroy)
            self.root.after(3500, preview_window.destroy)

    def retake_photo(self, preview_window):
        """ Retake the photo by closing the preview window and starting over """
        preview_window.destroy()  # Close the preview window
        self.start_countdown()  # Start the countdown again to retake the photo


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoApp(root)
    root.mainloop()