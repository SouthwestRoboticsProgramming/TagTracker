from threading import Thread
import cv2
import numpy as np
import json
from main import logger


class Camera:
    def __init__(self, camera_options):
        # Extract indevidual values
        camera_port = camera_options['port']
        self.name = camera_options['name']
        self.robot_position = camera_options['robot_pose']

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

        self.is_driver = params['dist'] is not None

        self.capture = cv2.VideoCapture(camera_port)

    def read(self, return_list=None, return_index=None):
        read_value = self.capture.read()

        if not return_list:  # If used outside of multithreaded camera system
            return read_value

        return_list[return_index] = read_value

    def release(self):
        self.capture.release()


class CameraArray:  # Multithread frame captures
    def __init__(self, logger, camera_list):
        # Put together a list of cameras
        self.camera_list = camera_list

        if not self.camera_list:
            logger.error("No cameras defined! Quitting")
            raise Exception("No cameras defined in camera array!")

    def read_cameras(self):  # Returns map of images to camera that they came from
        threads = []  # Threads to run
        images = []   # Collected images

        for i, camera in enumerate(self.camera_list):
            # Add a space for the image
            images.append([None, camera])  # Attach camera info to image that will be collected

            # Start a thread
            threads.append(Thread(target=camera.read, args=(images[i], 0,)))
            threads[i].start()

        # Join threads to get back to one thread
        for thread in threads:
            thread.join()

        # Filter out failed image captures and log them
        for i, read_image in enumerate(images):

            image, camera = read_image

            ret, frame = image  # Extract image into ret and the frame

            if not ret:  # If the image couldn't be captured
                images.pop(i)
                logger.error("{} failed to capture an image".format(camera.name))
            else:  # Otherwise, remove the ret and leave just the image
                height, width = frame.shape[:2]
                dist_coeffs = np.array(camera.distortion)
                new_mtx, roi = cv2.getOptimalNewCameraMatrix(camera.matrix, dist_coeffs, (width, height), 1, (width, height))

                undistorted = cv2.undistort(frame, camera.matrix, dist_coeffs, None, camera.matrix)
                crop_x, crop_y, crop_w, crop_h = roi
                undistorted = undistorted[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]

                images[i] = {
                    'image': undistorted,  # Remove  ret
                    'camera': camera
                }
        return images

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
