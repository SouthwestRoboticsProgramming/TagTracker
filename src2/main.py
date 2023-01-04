import time

import cv2

from cameras import USBCamera
from overlays import *

# Used to send values back to RoboRIO
from networktables import NetworkTablesInstance

def main():
    print("Starting main process")

    team = 2129
    is_server = False

    nt = NetworkTablesInstance.getDefault()
    if is_server:
        print("Starting NetworkTables server")
        nt.startServer()
    else:
        print(f"Connecting to NetworkTables for team {team}")
        nt.startClientTeam(team)
        nt.startDSClient()

    # Create a table to publish values to
    table = nt.getTable('tagtracker')

    # Define single camera to use
    camera = USBCamera("Camera 1", 0)

    # Create stream to show processed images

    # Run pipeline forever
    while True:
        tic = time.perf_counter()

        # Read images from cameras
        image = camera.read()

        # Send images through pipeline to get estimated poses

        # Send estimated poses back to RoboRIO

        toc = time.perf_counter()
        fps = 1 / (toc - tic)
        overlay = draw_fps(image, fps)
        cv2.imshow('Overlay', overlay)

        # Q to stop the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Teardown
    camera.release()

if __name__ == "__main__":
    main()