from cameras import *
from gui import *
import apriltag
import cv2

class _DetectorOptions: # Converts JSON into object for apriltag's dector to read
    def __init__(self, dict=None):
        if dict:
            for key, value in dict.items():
                setattr(self, key, value)

class Detector: # Rename?
    def __init__(self, logger, options):
        options = _DetectorOptions(options)
        self.detector = apriltag.Detector(options)

    def getPoses(self, images, params):

        # Make a list of estimated poses to add to
        estimated_poses = []

        # Find every target in the images
        for image in images:
            # Convert image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Find basic information about tag (center location, ID, family...)
            results = self.detector.detect(gray)

            # Estimate the pose of the camera relative to each target
            for result in enumerate(results):
                # Draw bounding box
                drawBoundingBox(image, result[1])

                pose, e0, e1 = self.detector.detection_pose(result[1], params[result[0]]) # TODO: Tag size
                # TODO Finish
                # TODO: What are the 'e'?
                estimated_poses.append(pose)

            # Log number of tags found
            if estimated_poses:
                logger.debug("Estimated pose on {} AprilTags".format(len(estimated_poses)))

        return estimated_poses