#!/bin/bash

if ! [ $(id -u) = 0 ]; then
   echo "Please run as root!"
   exit 1
fi

echo "[INFO] Starting setup"

yes | apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6 python3 python3-pip python3-opencv cmake

echo "[INFO] Installed packages"

pip install pip setuptools wheel --upgrade

echo "[INFO] Made sure pip dependencies are up to date"

pip install -r requirements.txt

echo "[INFO] Installed dependencies"

python3 setup_service.py

echo "[INFO] Installed service"

systemctl daemon-reload
systemctl enable apriltag_detector.service
systemctl start apriltag_detector.service

echo "[INFO] Started and enabled service"