#!/usr/bin/sh
DISPLAY=:0
export DISPLAY
echo "$(date) Hello, world." >> /home/mike/foo.txt
#/usr/bin/notify-send "Usb Device detected" "Starting SDCard move program for GoPro" | at now
/usr/bin/python /home/mike/eclipse-workspace/GoPro_SDCard_Move/Detect_SDCard.py  | at now