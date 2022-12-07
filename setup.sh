#!/bin/bash

if [ `id -u` -ne 0 ] ; then echo "Please run as root" ; exit 1 ; fi

echo "[INFO] Starting setup"

yes | apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 libopencv-dev cmake python3 python3-pip python3-opencv

echo "[INFO] Installing dependencies"

pip install apriltag pynetworktables

echo "[INFO] Finished setup"
