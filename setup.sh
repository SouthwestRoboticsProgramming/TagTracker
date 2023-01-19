#!/bin/bash

echo "[INFO] Starting setup"

yes | sudo apt-get install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6

echo "[INFO] Finished installing Anaconda for python environment"

yes n | conda create -n apriltags python=3.8

echo "[INFO] Created environment for python"

conda init bash
conda activate apriltags

pip install opencv-contrib-python
pip install apriltag
pip install pynetworktables

echo "[INFO] Installed dependencies"

python3 setup_service.py

echo "[INFO] Installed service"

systemctl daemon-reload
systemctl enable apriltag_detector.service
systemctl start apriltag_detector.service

echo "[INFO] Started and enabled service"