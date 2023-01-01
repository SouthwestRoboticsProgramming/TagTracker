import json
import sys
import time

import cv2
import numpy as np

# Used to send values back to RoboRIO
from networktables import NetworkTablesInstance

# Mostly used for sending video back to driver station
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer

DEFAULT_CONFIG_PATH = '/boot/frc.json'

class USBCamera:
    stream = None
    image_base = None

    def __init__(self, config):

        # Extract json into values

        # Extract name
        name = config.get('name')
        if name is None:
            raise KeyError("No name defined for camera")
        
        # Extract path to video stream
        path = config.get('path')
        if path is None:
            raise KeyError("No camera stream path defined")

        # Stream properties
        stream_properties = config.get('stream') # Intentionally allowed to be None, default is defined


        print(f"Starting camera '{name}' on {path}")

        inst = CameraServer.getInstance()
        camera = UsbCamera(name, path)

        # Start sending video feed back to driver station
        server = inst.startAutomaticCapture(camera=camera)

        # Configure the camera
        camera.setConfigJson(json.dumps(config))
        camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        if config.get('streamConfig') is not None:
            server.setConfigJson(json.dumps(stream_properties))

        self.stream = inst.getVideo(camera=camera)

        width = config.get('width')
        height = config.get('height')
        if width is None or height is None:
            raise KeyError("Width or height not defined")
        
        self.image_base = np.zeros(shape=(height, width, 3), dtype=np.uint8)

    def get_image(self):
        frame_time, frame = self.stream.grabFrame(self.image_base)
        return frame_time, frame

# TODO: Switched camera support



def extract_config(path):
    team = 0
    is_server = False
    camera_configs = []
    switched_configs = []

    # Extract into json
    try:
        with open(path, 'rt', encoding='utf-8') as file:
            config = json.load(file)
    except OSError as e:
        raise FileNotFoundError(f"Couldn't find {path}") from e

    # Check that the json is formatted correctly
    if not isinstance(config, dict):
        raise TypeError("json not formatted correctly")

    # Extract team number
    team = config['team']
    if team is None:
        raise KeyError('No team number defined')
    
    # Check if it should be client or server (optional config)
    if 'ntmode' in config:
        mode = config['ntmode'].lower()
        if mode == 'client':
            is_server = False
        elif mode == 'server':
            is_server = True
        else:
            raise NameError(f"Couldn't understand ntmode {mode} in config file")
    
    # Extract USB cameras
    camera_configs = config.get('cameras')
    if camera_configs is None:
        raise KeyError("No cameras defined!")

    # Extract switched cameras
    if 'switched cameras' in config:
        switched_configs = config['switched cameras']

    return team, is_server, camera_configs, switched_configs
    

def main():
    # Default config path is "/boot/frc.json" for WPILibPI
    configPath = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_CONFIG_PATH

    team, is_server, camera_configs, switched_configs = extract_config(configPath)

    # Start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    if is_server:
        print("Starting NetworkTables server")
        ntinst.startServer()
    else:
        print(f"Connecting to NetworkTables for team {team}")
        print(type(team))
        ntinst.startClientTeam(team)
        ntinst.startDSClient()

    # Create a table to publish values to
    table = ntinst.getTable('tagtracker')

    # Configure cameras
    cameras = []
    for config in camera_configs:
        cameras.append(USBCamera(config))

    output_stream = CameraServer.getInstance().putVideo('Processed', 320, 240)

    # Loop until power is cut
    print("Starting main process")
    while True:
        # Test by doing operations on camera 1
        frame_time, frame = cameras[0].get_image()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        output_stream.putFrame(gray)



if __name__ == '__main__':
    main()

