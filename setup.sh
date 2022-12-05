#!/bin/bash

echo "[INFO] Starting setup"

if [ "$EUID" -ne 0 ] then
    yes | sudo apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 cmake python3 python3-pip
else
    yes | apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 cmake python3 python3-pip
fi 

echo "[INFO] Installing dependencies"

pip install opencv-contrib-python
pip install apriltag
pip install pynetworktables

echo "[INFO] Finished setup"
