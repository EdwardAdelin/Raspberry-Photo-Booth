# Installation Guide

Before running the application, ensure you have the necessary dependencies installed.  
Depending on your device's configuration, you may need to install all, some, or none of them.

### Step 1: Install Python dependencies
```sh
pip install opencv-python numpy pillow tk
```

### Step 2: Update and install OpenCV for Python
```sh
sudo apt update
sudo apt install python3-opencv
```

### Step 3: Install Tkinter (for GUI support)
```sh
sudo apt install python3-tk
```

### Step 4: Install PIL (Python Imaging Library)  
```sh
sudo apt install python3-pillow
sudo apt-get install python3-pil.imagetk
```

---

# Overlay Setup

Place your overlay image in the `Pictures` directory.  
If you want to use the FILS overlay, copy it from the `overlays` folder to the `Pictures` directory on your Linux device.

**Note:**  
Some values in the code are hardcoded due to performance limitations on a Raspberry Pi 3.  
The app was designed to run efficiently on a slow device, so avoid making changes that add heavy menus or options.

---

# Printer Setup

To ensure the correct printer is selected, check all available printers by running:  
```sh
lpstat -p -d
```
This command will list all printers and show the default printer.  

To see available printers:  
```sh
lpstat -a
```
After identifying your desired printer, update the code accordingly.  
Once you press the **Print** button in the app, the last captured photo will be printed using the specified printer.


