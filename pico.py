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
        """ Convert photo to sketch, place it on diploma frame, and print it """
        if hasattr(self, 'photo_path'):
            import cv2
            from PIL import Image, ImageEnhance
            import subprocess
            import os
            
            # Show printing notification
            printing_notification = tk.Toplevel(self.root)
            printing_notification.title("Processing")
            printing_notification.configure(bg=self.bg_color)
            
            # Force fullscreen
            printing_notification.attributes('-fullscreen', True)
            printing_notification.overrideredirect(True)
            printing_notification.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
            printing_notification.focus_set()
            
            # Create centered content frame
            notification_frame = tk.Frame(printing_notification, bg=self.bg_color)
            notification_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # Status message
            icon_size = max(24, min(42, int(self.screen_height / 16)))
            title_size = max(14, min(18, int(self.screen_height / 35)))
            
            processing_label = tk.Label(
                notification_frame,
                text="🖨️",
                font=("Helvetica", icon_size),
                fg=self.primary_color,
                bg=self.bg_color
            )
            processing_label.pack(pady=(0, 15))
            
            status_label = tk.Label(
                notification_frame,
                text="Creating your diploma...",
                font=("Helvetica", title_size, "bold"),
                fg=self.primary_color,
                bg=self.bg_color
            )
            status_label.pack(pady=10)
            
            self.root.update()
            
            try:
                # Load the original image
                original_img = cv2.imread(self.photo_path)

                # Create sketch effect
                # Step 1: Convert to grayscale
                gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

                # Step 2: Invert the grayscale image
                inverted_img = 255 - gray_img

                # Step 3: Apply Gaussian blur to the inverted image
                blurred_img = cv2.GaussianBlur(inverted_img, (21, 21), 0)

                # Step 4: Invert the blurred image
                inverted_blurred = 255 - blurred_img

                # Step 5: Create sketch by dividing grayscale by inverted blurred image
                sketch = cv2.divide(gray_img, inverted_blurred, scale=256.0)

                # For better contrast in the sketch
                sketch = cv2.normalize(sketch, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
                
                # Convert sketch to PIL Image
                sketch_pil = Image.fromarray(sketch)
                
                # Load the diploma frame template
                diploma_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlays", "diploma.png")
                
                # Check if diploma frame exists
                if not os.path.exists(diploma_path):
                    # Create the overlays directory if it doesn't exist
                    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlays"), exist_ok=True)
                    status_label.config(text=f"Error: Diploma frame not found at {diploma_path}")
                    raise FileNotFoundError(f"Diploma frame not found at {diploma_path}")
                    
                # Load the diploma frame
                diploma_frame = Image.open(diploma_path).convert('RGBA')
                
                # Define the coordinates where the sketch should be placed within the diploma
                # Format: (left, top, right, bottom) - the area where the sketch should be placed
                # These coordinates will need adjustment based on your specific diploma frame
                frame_w, frame_h = diploma_frame.size
                
                # Calculate a reasonable area for the photo - adjust these ratios as needed
                # This assumes the diploma has a designated space in the center area
                left_margin_ratio = 0.60  # 15% from left edge
                right_margin_ratio = 0.10  # 15% from right edge
                top_margin_ratio = 0.10    # 25% from top edge  
                bottom_margin_ratio = 0.40  # 25% from bottom edge
                
                photo_area = (
                    int(frame_w * left_margin_ratio),
                    int(frame_h * top_margin_ratio),
                    int(frame_w * (1 - right_margin_ratio)),
                    int(frame_h * (1 - bottom_margin_ratio))
                )
                
                # Calculate dimensions for the photo to fit in the designated area
                photo_width = photo_area[2] - photo_area[0]
                photo_height = photo_area[3] - photo_area[1]
                
                # Resize the sketch to fit in the designated area while maintaining aspect ratio
                sketch_w, sketch_h = sketch_pil.size
                ratio = min(photo_width / sketch_w, photo_height / sketch_h)
                new_size = (int(sketch_w * ratio), int(sketch_h * ratio))
                resized_sketch = sketch_pil.resize(new_size, Image.LANCZOS)
                
                # Convert grayscale sketch to RGBA for proper transparency handling
                resized_sketch_rgba = resized_sketch.convert('RGBA')
                
                # Create a copy of the diploma frame to work with
                result_image = diploma_frame.copy()
                
                # Calculate the centered position within the photo area
                paste_x = photo_area[0] + (photo_width - new_size[0]) // 2
                paste_y = photo_area[1] + (photo_height - new_size[1]) // 2
                
                # Paste the sketch onto the diploma frame
                # Use the sketch as its own mask for proper blending
                result_image.paste(resized_sketch_rgba, (paste_x, paste_y), resized_sketch_rgba)
                
                # Save the combined image (sketch on diploma)
                framed_path = os.path.splitext(self.photo_path)[0] + "_diploma.jpg"
                
                # Convert to RGB before saving as JPG
                result_image_rgb = result_image.convert('RGB')
                result_image_rgb.save(framed_path, quality=95)
                
                # Print the image directly (no A4 resizing)
                status_label.config(text="Sending to printer...")
                self.root.update()
                
                # Use lpr command with appropriate options for printing
                subprocess.run([
                    'lpr',
                    '-o', 'media=A4',
                    '-o', 'fit-to-page',  # Fit to page to ensure proper sizing
                    '-o', 'orientation-requested=4',  # Landscape orientation
                    framed_path
                ])
                
                # Update notification to show success
                processing_label.config(text="✅")
                status_label.config(text="Successfully sent to printer!")
                
                # Add a button to dismiss the notification
                dismiss_btn = tk.Button(
                    notification_frame,
                    text="OK",
                    command=printing_notification.destroy,
                    font=("Helvetica", title_size),
                    bg=self.accent_color,
                    fg="white",
                    padx=20,
                    pady=10,
                    cursor="hand2"
                )
                dismiss_btn.pack(pady=20)
                
            except Exception as e:
                status_label.config(text=f"Error: {str(e)}")
                
                # Add a button to dismiss the error
                dismiss_btn = tk.Button(
                    notification_frame,
                    text="OK",
                    command=printing_notification.destroy,
                    font=("Helvetica", title_size),
                    bg="#F44336",
                    fg="white",
                    padx=20,
                    pady=10,
                    cursor="hand2"
                )
                dismiss_btn.pack(pady=20)

    def retake_photo(self, preview_window):
        """ Retake the photo by closing the preview window and starting over """
        preview_window.destroy()  # Close the preview window
        self.start_countdown()  # Start the countdown again to retake the photo


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoApp(root)
    root.mainloop()