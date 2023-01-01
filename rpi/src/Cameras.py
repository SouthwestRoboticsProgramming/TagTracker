#!/usr/bin/env python3

# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

import json
import time
import sys

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
from networktables import NetworkTablesInstance

class USBCamera:
    camera = None

    def __init__(self, config):
        print(f"Starting camera '{config.name}' on {config.path}")

        inst = CameraServer.getInstance()
        self.camera = UsbCamera(config.name, config.path)

        # Start sending video feed back to driver station
        server = inst.startAutomaticCapture(camera=self.camera, return_server=True)

        # Configure the camera
        self.camera.setConfigJson(json.dumps(config.config))
        self.camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        if config.streamConfig is not None:
            server.setConfigJson(json.dumps(config.streamConfig))

# TODO: Switched camera support


