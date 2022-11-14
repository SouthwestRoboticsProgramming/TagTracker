from imutils import build_montages
import numpy as np
import cv2

# WIP Feature, not currently used.

# data_dict holds both images and the camera that took them
def get_driver_frame(data_dict):
    # Just get the cameras marked as driver
    drivers = [data['image'] for data in data_dict if data['camera'].is_driver]

    # TODO: No drivers?
    if drivers:
        # Arrange the images into one collage
        collage = create_collage(drivers)
        collage = cv2.resize(collage, (50,50))
    else:
        # Just give back a blank image
        # TODO: Descriptive image
        collage = np.zeros(shape=[512,512,3], dtype=np.uint8)
    return collage




def create_collage(images):
    # TODO: Magic rescaling
    montages = build_montages(images, (256, 256), (len(images),1))
    return montages[0]