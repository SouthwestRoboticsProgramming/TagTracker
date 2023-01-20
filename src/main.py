import logging
from networktables import NetworkTables
import time

# Get field data to improve logging
fms = NetworkTables.getTable("FMSInfo")
match_type = fms.getEntry('MatchType')
match_number = fms.getEntry('MatchNumber')

# Configure logging first so other files can use the same formatting
LOG_FILENAME = 'Tracker.Log'
TIME_FORMAT = f"%y %a %b {match_type.getString('Test Match')} {match_number.getString('0')}"

LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt=TIME_FORMAT)
logger = logging.getLogger()


from argparse import ArgumentParser
from tag_tracker import *
from solver import *
from shufflelog_api import ShuffleLogAPI
from driver_station import get_driver_frame
import json

def main():
    # Create a parser to allow variable arguments
    parser = ArgumentParser(prog='AprilTag tracker',
                            description='AprilTag tracker for FRC')
    parser.add_argument('-i', '--networktable_ip', type=str, default='localhost', metavar='', help='RoboRIO ip to access network tables')
    parser.add_argument('-e', '--environment', type=str, default='environment.json', metavar='', help='Path to environment definition JSON')
    parser.add_argument('-c', '--cameras', type=str, default='cameras.json', metavar='', help='Path to camera definition JSON')
    parser.add_argument('-d', '--detector', type=str, default='detector.json', metavar='', help='Path to detector definition JSON')
    parser.add_argument('-n', '--no_gui',  action='store_true', help='Hide OpenCV gui.')

    args = parser.parse_args()

    # Configure NetworkTables
    networktable_ip = args.networktable_ip
    if networktable_ip:
        NetworkTables.initialize(server=networktable_ip)
    else:
        NetworkTables.initialize()
    # Tables to send back to RoboRIO and driver station
    table = NetworkTables.getTable("apriltag")

    # Extract environment JSON
    try:
        environment_json = open(args.environment, 'r')
        environment = json.load(environment_json)
        logger.info("Environment JSON loaded")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.exception("Could not open envionment JSON, quitting")
        raise FileNotFoundError(f"Could not open environment JSON '{args.environment}', is the path relative to /TagTracker/?") from e


    environment_json.close()

    # Exctract cameras JSON
    try:
        cameras_json = open(args.cameras, 'r')
        cameras = json.load(cameras_json)
        logger.info("Cameras JSON loaded")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.exception("Could not open cameras JSON, quitting")
        raise FileNotFoundError(f"Could not open cameras JSON '{args.cameras}', is the path relative to /TagTracker?") from exc


    cameras_json.close()

    # Extract detector JSON
    try:
        detector_json = open(args.detector, 'r')
        detector = json.load(detector_json)
        logger.info("Detector JSON loaded")
    except (FileNotFoundError, json.JSONDecodeError) as err:
        logger.exception("Could not open detector JSON, qutting")
        raise FileNotFoundError(f"Could not open detector JSON '{args.detector}', is the path relative to /TagTracker?") from err


    detector_json.close()

    # Setup a detector with the JSON settings
    detector = Detector(logger, detector)

    camera_list = [Camera(camera_info) for camera_info in cameras['cameras']]

    # Setup a camera array with the JSON settings
    camera_array = CameraArray(logger, camera_list)

    # Create a solver to filter estimated positions
    # and localize robot
    solver = RobotPoseSolver(environment)

    # Initialize ShuffleLog API
    messenger_params = {
        'host': 'localhost',
        'port': 5805,
        'name': 'TagTracker',
        'mute_errors': True
    }
    api = ShuffleLogAPI(messenger_params, environment['tags'], cameras['cameras'])


    # Main loop, run all the time like limelight
    while True:
        tic = time.perf_counter();
        data = camera_array.read_cameras()
        detection_poses = detector.getPoses(data)

        position, matrices = solver.solve(detection_poses)

        if not args.no_gui:
            for i, image in enumerate(data):
                cv2.imshow(str(i), image['image'])

        # Send the solved position back to robot
        api.publish_test_matrices(matrices)
        if position is None: position = [0, 0, 0]
        table.putNumberArray('position', position)

        # Read incoming API messages
        api.read()

        # Q to stop the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        toc = time.perf_counter()
        print(f"FPS: {1/(toc-tic)}")

    # Disconnect from Messenger
    api.shutdown()

    # Safely close video operation
    cv2.destroyAllWindows()
    camera_array.release_cameras()


if __name__ == '__main__':
    main()
