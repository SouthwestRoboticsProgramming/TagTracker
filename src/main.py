import cv2
import time
import json
import warnings
from argparse import ArgumentParser

from tracker import Detector
from network import Network
from cameras import Camera
from overlays import draw_fps

def main():
    # Create a parser to allow variable arguments
    parser = ArgumentParser(prog='AprilTag tracker',
                            description='AprilTag tracker for FRC')
    parser.add_argument('-i', '--networktable_ip', type=str, default='localhost', metavar='', help='RoboRIO ip to access network tables')
    parser.add_argument('-c', '--cameras', type=str, default='cameras.json', metavar='', help='Path to camera definition JSON')
    parser.add_argument('-d', '--detector', type=str, default='detector.json', metavar='', help='Path to detector definition JSON')
    parser.add_argument('-n', '--no_gui',  action='store_true', help='Hide OpenCV gui.')

    args = parser.parse_args()

    # Configure NetworkTables
    networktable_ip = args.networktable_ip
    # networktable_ip = False if networktable_ip == 'localhost' else networktable_ip
    network = Network(networktable_ip, 5) # Max tag info is 5

    # Exctract cameras JSON
    try:
        cameras_json = open(args.cameras, 'r')
        cameras = json.load(cameras_json)
        print("Cameras JSON loaded")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        warnings.warn("Could not open cameras JSON, quitting")
        raise FileNotFoundError(f"Could not open cameras JSON '{args.cameras}', is the path relative to /TagTracker?") from exc


    cameras_json.close()

    # Extract detector JSON
    try:
        detector_json = open(args.detector, 'r')
        detector = json.load(detector_json)
        print("Detector JSON loaded")
    except (FileNotFoundError, json.JSONDecodeError) as err:
        warnings.warn("Could not open detector JSON, qutting")
        raise FileNotFoundError(f"Could not open detector JSON '{args.detector}', is the path relative to /TagTracker?") from err


    detector_json.close()

    # Setup a detector with the JSON settings
    detector = Detector(detector)

    # Configure cameras
    cameras_info = cameras['cameras']

    camera = Camera(cameras_info[0])

    # Main loop, run all the time like limelight
    while True:
        tic = time.perf_counter();
        image = camera.capture.read()
        detection_poses = detector.get_estimated_poses(image, camera.camera_params)

        network.put(detection_poses)

        toc = time.perf_counter()
        fps = 1 / (toc - tic)
        draw_fps(image, fps)
        
        cv2.imshow("img", image)

        # Q to stop the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # print(f"FPS: {1/(toc-tic)}")

    # Safely close video operation
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
