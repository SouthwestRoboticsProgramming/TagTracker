#!/bin/bash

if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi

echo "[INFO] Starting setup"

yes | apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 cmake python3 python3-pip

echo "[INFO] Installing dependencies"

pip install opencv-contrib-python
pip install apriltag
pip install pynetworktables

echo "[INFO] Finished setup"
