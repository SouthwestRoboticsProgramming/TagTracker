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

        self.capture = cv2.VideoCapture(camera_port)
        self.camera_params = params
        

    def getImage(self, return_list=None, return_index=None):
        ret, frame = self.capture.read()
        if not return_list:
            return frame

        return_list[return_index] = (ret, frame)


class CameraArray: # Multithread frame captures
    def __init__(self, logger, camera_list):
        # Put together a list of cameras
        self.cameras = camera_list

        if not self.cameras:
            logger.error("No cameras defined! Quitting")
            raise Exception("No cameras defined in camera array!")


    def getImages(self):
        threads = []
        images = []

        for camera in enumerate(self.cameras):
            # Add a space for the image
            images.append(None)

            # Start a thread
            threads.append(Thread(target=camera[1].getImage, args=(images, camera[0],)))
            threads[camera[0]].start()

        # Join threads to get back to one thread
        for thread in threads:
            thread.join()

        # Filter out failed image captures and log them
        for image in enumerate(images):
            index = image[0]
            value = image[1]
            if not value[0]: # If ret was false
                images.pop(index)
                logger.error("{} failed to capture an image".format(self.camera[index].name))
            else: # Otherwise, remove the ret and leave just the image
                images[index] = images[index][1] # Remove ret

        return images

    def getParams(self):
        params = []

        for camera in self.cameras:
            # Convert dictionary to tuple
            camera_params_tuple = tuple(camera.camera_params.values())
            params.append(camera_params_tuple)

        return params