from imutils import build_montages
from flask_opencv_streamer.streamer import Streamer
from threading import Thread
import numpy as np
import cv2

# data_dict holds both images and the camera that took them
def get_driver_frame(data_dict):
    # Just get the cameras marked as driver
    drivers = [data['image'] for data in data_dict if data['camera'].is_driver]

    # TODO: No drivers?
    if drivers:
        # Arrange the images into one collage
        collage = create_collage(drivers)
    else:
        # Just give back a blank image
        # TODO: Descriptive image
        collage = np.zeros(shape=[512,512,3], dtype=np.uint8)
    return collage




def create_collage(images):
    # TODO: Magic rescaling
    montages = build_montages(images, (256, 256), (len(images),1))
    return montages[0]

class Stream():
    def __init__(self):
        self.image = None

    def _main_loop(self, port):
        stream = Streamer(port, False)
        stream.start_streaming()

        while True: # Constaly update the image
            if self.image is not None:
                print("Updated!")
                stream.update_frame(self.image)

    def start(self, port):
        # Start the streamer
        thread = Thread(target=self._main_loop, args=(port,))
        thread.start()


    def update(self, data):
        self.image = get_driver_frame(data)