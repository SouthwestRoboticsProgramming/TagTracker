import cv2
import numpy as np

def draw_fps(image, fps):
    output = image.copy()

    # Remove decimal point
    fps = round(fps)

    color = (255, 0, 0) # Blue
    location = (10, 30)

    cv2.putText(output, str(fps), location, cv2.FONT_HERSHEY_COMPLEX, 1, color)

    return output