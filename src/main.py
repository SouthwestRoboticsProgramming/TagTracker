from argparse import ArgumentParser
from networktables import NetworkTables
from tag_tracker import *
from solver import *
from shufflelog_api import ShuffleLogAPI
import logging
import threading
import json

# Get field data to improve logging
fms = NetworkTables.getTable("FMSInfo")
match_type = fms.getEntry('MatchType')
match_number = fms.getEntry('MatchNumber')

# Configure logging
LOG_FILENAME = 'Tracker.Log'
TIME_FORMAT = '%y %a %b {} {}'.format(match_type.getString('Test Match'), match_number.getString('0'))
LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt=TIME_FORMAT)
logger = logging.getLogger()

def main():
    # Create a parser to allow variable arguments
    parser = ArgumentParser(prog='AprilTag tracker',
                            description='AprilTag tracker for FRC')
    parser.add_argument('-i', '--networktable_ip', type=str, default=None, metavar='', help='RoboRIO ip to access network tables')
    parser.add_argument('-e', '--environment', type=str, default='environment.json', metavar='', help='Path to environment definition JSON')
    parser.add_argument('-c', '--cameras', type=str, default='cameras.json', metavar='', help='Path to camera definition JSON')
    parser.add_argument('-d', '--detector', type=str, default='detector.json', metavar='', help='Path to detector definition JSON')

    args = parser.parse_args()

    # Configure NetworkTables
    networktable_ip = args.networktable_ip
    if networktable_ip: # If valid ip
        NetworkTables.initialize(server=networktable_ip)
    else:
        NetworkTables.initialize() # TODO: Start a new server?

    # Tables to send back to RoboRIO and driver station
    todo_table_name = NetworkTables.getTable("TODO") # TODO: Give it a name

    # Extract environment JSON
    try:
        environment_json = open(args.environment, 'r')
        environment = json.load(environment_json)
        logger.info("Environment JSON loaded")
    except:
        logger.exception("Could not open envionment JSON, quitting")
        raise Exception("Could not open environment JSON '{}', is the path relative to /TagTracker/?".format(args.environment))
    environment_json.close()

    # Exctract cameras JSON
    try:
        cameras_json = open(args.cameras, 'r')
        cameras = json.load(cameras_json)
        logger.info("Cameras JSON loaded")
    except:
        logger.exception("Could not open cameras JSON, quitting")
        raise Exception("Could not open cameras JSON '{}', is the path relative to /TagTracker?".format(args.cameras))
    cameras_json.close()

    # Extract detector JSON
    try:
        detector_json = open(args.detector, 'r')
        detector = json.load(detector_json)
        logger.info("Detector JSON loaded")
    except:
        logger.exception("Could not open detector JSON, qutting")
        raise Exception("Could not open detector JSON '{}', is the path relative to /TagTracker?".format(args.detector))
    detector_json.close()

    # Setup a detector with the JSON settings
    detector = Detector(logger, detector)

    camera_list = []

    for camera_info in cameras['cameras']:
        camera_list.append(Camera(camera_info))

    # Setup a camera array with the JSON settings
    camera_array = CameraArray(logger, camera_list)
    
    # Create a solver to filter estimated positions
    # and localize robot
    solver = RobotPoseSolver(environment)

    # Create an entry to send data back
    solved_position = todo_table_name.getEntry("solved_position")

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
        data = camera_array.read_cameras()

        detection_poses = detector.getPoses(data)

        position, matrices = solver.solve(detection_poses)

        print(position)

        for i, image in enumerate(data):
            cv2.imshow(str(i), image['image'])

        # Send the solved position back to robot
        # TODO

        api.publish_test_matrices(matrices)

        # Read incoming API messages
        api.read()

        # Q to stop the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  

    # Disconnect from Messenger
    api.shutdown()  

if __name__ == '__main__':
    main()

