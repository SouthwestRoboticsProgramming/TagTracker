from threading import Thread
import cv2
import json
from main import logger

class Camera:
    def __init__(self, camera_options):
        # Extract indevidual values
        camera_port = camera_options['port']
        self.name = camera_options['name']

        # Extract params JSON
        try:
            location = 'camera_params/{}.json'.format(camera_options['type'])
            params_json = open(location, 'r')
            params = json.load(params_json)
            logger.info("Camera parameters JSON loaded for {}".format(self.name))
        except:
            logger.exception("Could not open camera parameters JSON, qutting")
            raise Exception("Could not open cameara params JSON '{}' for {}, is the path relative to /camera_params?".format(camera_options['type'], self.name))
        params_json.close()

        # Convert params to tuple
        self.camera_params = tuple(params.values())


        self.capture = cv2.VideoCapture(camera_port)
        

    def read(self, return_list=None, return_index=None):
        read_value = self.capture.read()

        if not return_list: # If used outside of multithreaded camera system
            return read_value

        return_list[return_index] = read_value


class CameraArray: # Multithread frame captures
    def __init__(self, logger, camera_list):
        # Put together a list of cameras
        self.camera_list = camera_list

        if not self.camera_list:
            logger.error("No cameras defined! Quitting")
            raise Exception("No cameras defined in camera array!")


    def read_cameras(self): # Returns map of images to camera that they came from
        threads = [] # Threads to run
        images = [] # Collected images

        for i, camera in enumerate(self.camera_list):
            # Add a space for the image
            images.append([None, camera]) # Attach camera info to image that will be collected

            # Start a thread
            threads.append(Thread(target=camera.read, args=(images[i], 0,)))
            threads[i].start()

        # Join threads to get back to one thread
        for thread in threads:
            thread.join()

        # Filter out failed image captures and log them
        for i, read_image in enumerate(images):

            image, camera = read_image

            del(read_image) # For debugging purposes

            ret, frame = image # Extract image into ret and the frame

            if not ret: # If the image couldn't be captured
                images.pop(i)
                logger.error("{} failed to capture an image".format(camera.name))
            else: # Otherwise, remove the ret and leave just the image
                images[i][0] = frame # Remove ret but leave camera info

        return images

    def getParams(self):
        params = []

        for camera in self.camera_list:
            # Convert dictionary to tuple
            camera_params_tuple = tuple(camera.camera_params.values())
            params.append(camera_params_tuple)

        return params