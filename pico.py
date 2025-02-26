import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os
import time


class PhotoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POLI Internation Fest")

        # Camera setup
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Force Video4Linux2

        # UI Elements
        self.canvas = tk.Label(root)
        self.canvas.pack()

        self.countdown_label = tk.Label(root, text="", font=("Arial", 40), fg="red")
        self.countdown_label.pack()

        self.btn_capture = tk.Button(root, text="Capture Photo", command=self.start_countdown)
        self.btn_capture.pack()

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
        """ Continuously update video preview """
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            self.canvas.config(image=frame)
            self.canvas.image = frame
        self.root.after(10, self.update_video_stream)

    def start_countdown(self, count=5):
        """ Show countdown before capturing photo """
        if count > 0:
            self.countdown_label.config(text=str(count))  # Update countdown label
            self.root.after(1000, self.start_countdown, count - 1)  # Wait 1 second
        else:
            self.countdown_label.config(text="")  # Clear countdown
            self.capture_photo()

    def capture_photo(self):
        """ Capture a photo from the camera and apply overlay """
        ret, frame = self.cap.read()
        if ret:
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
        photo_path = os.path.expanduser(f"~/Pictures/photo_{int(time.time())}.png")  # Unique filename
        img.save(photo_path)
        print(f"Photo saved to {photo_path}")
        self.photo_path = photo_path  # Save the path for later use (e.g., printing)

    def show_preview_window(self, img):
        """ Show a new window with the preview image and print option """
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Photo")

        # Display the photo in the new window
        img_resized = img.resize((300, 300))  # Resize for preview display
        img_tk = ImageTk.PhotoImage(img_resized)

        label = tk.Label(preview_window, image=img_tk)
        label.image = img_tk  # Keep a reference to the image
        label.pack()

        # Print button
        btn_print = tk.Button(preview_window, text="Print Photo", command=lambda: self.print_photo(preview_window))
        btn_print.pack()

        # Retake button
        btn_retake = tk.Button(preview_window, text="Retake Photo", command=lambda: self.retake_photo(preview_window))
        btn_retake.pack()

    def print_photo(self, preview_window):
        """ Print the saved photo using Linux `lp` command """
        if hasattr(self, 'photo_path'):
            print(f"Simulating print for: {self.photo_path}")
            # Uncomment the line below for actual printing if a printer is available
            # os.system(f"lp {self.photo_path}")  # Print using system command

            #To print a file to a specific printer (without setting it as the default), you can use the -d option with the lp command to specify the printer:
            #lp -d printer_name /path/to/photo.png

            preview_window.destroy()  # Close preview window after printing

    def retake_photo(self, preview_window):
        """ Retake the photo by closing the preview window and starting over """
        preview_window.destroy()  # Close the preview window
        self.start_countdown()  # Start the countdown again to retake the photo


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoApp(root)
    root.mainloop()
