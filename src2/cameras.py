import cv2
import numpy as np
import json

class Camera:
    name = ""

    def __init__(self, name):
        self.name = name

    # Get an image from the camera
    def read(self):
        return np.zeros(shape=(1080, 1920, 3), dtype=np.uint8)

    def release(self): pass

class USBCamera(Camera):
    capture = None

    def __init__(self, name, port=0):
        self.capture = cv2.VideoCapture(port)
        self.name = name

        print(f"Starting camera '{self.name}' on port {port}")

    def read(self):
        ret, frame = self.capture.read()
        if not ret:
            print(f"{self.name} was unable to capture an image")
            frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

            # Overlay failed message
            cv2.putText(frame, "No input", (80, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (20, 20, 20))

        return frame

    def release(self):
        self.capture.release()

class CameraServerCamera(Camera):

    stream = None
    image_base = None

    def __init__(self, config_dict, stream_feed=False):
        from cscore import CameraServer, VideoSource, UsbCamera
        
        # Extract name
        self.name = config_dict['name']

        # Extract path to video stream
        path = config_dict['path']

        # Stream properties (can be None, will fall back to default)
        stream_properties = config_dict.get('stream')

        print(f"Starting camera '{self.name}' on {path}")

        cs = CameraServer.getInstance()
        camera = UsbCamera(self.name, path)

        # Configure camera
        camera.setConfigJson(json.dumps(config_dict))
        camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        if stream_feed:
            # Start sending video back to driver station
            server = cs.startAutomaticCapture(camera=camera)

            if (config_dict.get('streamConfig') is not None):
                server.startConfigJson(json.dumps(stream_properties))

        self.stream = cs.getVideo(camera=camera)

        # It runs much quicker if an image is preallocated
        width = config_dict['width']
        height = config_dict['height']

        # FIXME: Possibly breaks with B+W camera
        self.image_base = np.zeros(shape=(height, width, 3), dtype=np.uint8)

    def read(self):
        img_time, img = self.stream.grabFrame(self.image_base)

        if img_time == 0:  # Something has gone wrong
            return self.image_base
            
        return img
