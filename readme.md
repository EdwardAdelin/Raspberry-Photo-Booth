# Be sure you install the following
# (depending on the status of your device you might need
# to install all dependencies or install none if they are already on your device)
1
pip install opencv-python numpy pillow tk
2
sudo apt update
sudo apt install python3-opencv
3
sudo apt install python3-tk
4
sudo apt install python3-pillow
sudo apt-get install python3-pil.imagetk

# Paste the overlay you want to use to "Pictures" directory (the overlay of FILS is located in "overlays" folder, copy it to "Pictures" directory from Linux device)
# some values are hardcoded in this app because it was made to run on a slow PI3 wich wouldve crashed if more menius or options would`ve been used. Keep this in mind when changing code values.

# CHECK ALL THE PRINTERS AND BE SURE TO WRITE IN CODE THE PROPPER PRINTER YOU WILL PRINT ON
type in termminal:
lpstat -p -d
This command will return you the name of printers and the default printer. 
lpstat -a
This will show you printers. You can write in code the printers name that you want to use.
After hitting print button, the printer will print your picture that you last took.




