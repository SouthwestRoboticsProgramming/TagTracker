from threading import Thread
import cv2
import numpy as np
import json
from main import logger
import time
import subprocess

class CameraServerCamera:
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

class Camera:
    def __init__(self, camera_options):
        # Extract individual values
        camera_port = camera_options.get('port')
        if camera_port is None:
            camera_port = get_camera_by_serial(camera_options['serial'])
        self.name = camera_options['name']
        self.robot_position = camera_options['robot_pose']
        self.is_driver = camera_options.get('driver') is not None

        # Extract params JSON
        try:
            location = f"camera_params/{camera_options['type']}.json"
            params_json = open(location, 'r')
            params = json.load(params_json)
            logger.info(f"Camera params JSON loaded for {self.name}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.exception("Could not open camera parameters JSON, qutting")
            raise FileNotFoundError("Could not open cameara params JSON '{}' for {}, \
                is the path relative to /camera_params?".format(camera_options['type'], self.name)) from e

        params_json.close()

        # Convert params to tuple
        self.camera_params = (params['fx'], params['fy'], params['cx'], params['cy'])
        self.distortion = params['dist']
        self.matrix = np.array([
            self.camera_params[0], 0, self.camera_params[2],
            0, self.camera_params[1], self.camera_params[3],
            0, 0, 1
        ]).reshape(3, 3)


        self.capture = cv2.VideoCapture(camera_port)

    # def read(self, return_list=None, return_index=None):
    #     read_value = self.capture.read()

    #     if not return_list:  # If used outside of multithreaded camera system
    #         return read_value

    #     return_list[return_index] = read_value

    # Takes a queue, when reading the queue, you are reading the most up-to-date image
    def start_reader(self, images_list, list_index):
        while True:
            ret, frame = self.capture.read() # Read the camera

            if not ret:
                images_list[list_index] = ((ret, frame), self)
                continue

            height, width = frame.shape[:2]
            dist_coeffs = np.array(self.distortion)
            new_mtx, roi = cv2.getOptimalNewCameraMatrix(self.matrix, dist_coeffs, (width, height), 1, (width, height))

            undistorted = cv2.undistort(frame, new_mtx, dist_coeffs, None, self.matrix)
            crop_x, crop_y, crop_w, crop_h = roi
            undistorted = undistorted[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]

            images_list[list_index] = ((ret, frame), self)

    def release(self):
        self.capture.release()


class CameraArray:  # Multithread frame captures
    def __init__(self, logger, camera_list):
        # Put together a list of cameras
        self.camera_list = camera_list

        if not self.camera_list:
            logger.error("No cameras defined! Quitting")
            raise ValueError("No cameras defined in camera array!")

        self.image_list = []
        self.threads = []

        # Create threads for each camera
        for i, camera in enumerate(self.camera_list):
            self.image_list.append(None) # Add something for the thread to edit
            self.threads.append(Thread(target=camera.start_reader, args=(self.image_list, i,)))
            self.threads[i].start()

    def read_cameras(self):  # Returns map of images to camera that they came from
        final_images = []

        # Filter out failed image captures and log them
        for read_image in self.image_list:

            if not read_image:
                continue

            image, camera = read_image

            ret, frame = image  # Extract image into ret and the frame

            if not ret:  # If the image couldn't be captured
                logger.error(f"{camera.name} failed to capture an image")
            else:  # Otherwise, remove the ret and leave just the image
                final_images.append({
                    'image': frame,  # Remove  ret
                    'camera': camera
                })
        return final_images

    def getParams(self):
        params = []

        for camera in self.camera_list:
            # Convert dictionary to tuple
            camera_params_tuple = tuple(camera.camera_params.values())
            params.append(camera_params_tuple)

        return params

    def release_cameras(self):
        for camera in self.camera_list:
            camera.release()


# Works by running the command "udevadm info --name/dev/video0"
def get_cam_serial(cam_id):
    FILTER = "ID_SERIAL_SHORT="

    p = subprocess.Popen('udevadm info --name=/dev/video{} | grep {} | cut -d "=" -f 2'.format(cam_id, FILTER),
                         stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p.status = p.wait()
    response = output.decode('utf-8')
    return response.replace('\n', '')

def get_camera_by_serial(serial):
    for cam_id in range(0, 10):
        s = get_cam_serial(cam_id)
        if s == serial:
            return cam_id
