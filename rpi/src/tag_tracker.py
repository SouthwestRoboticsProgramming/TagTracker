from gui import *
import apriltag
import cv2

class _DetectorOptions: # Converts JSON into object for apriltag's dector to read
    def __init__(self, dict=None):
        if dict:
            for key, value in dict.items():
                setattr(self, key, value)

class Detector: # Rename?
    def __init__(self, options):
        options = _DetectorOptions(options)
        self.detector = apriltag.Detector(options)

    def estimate_pose(self, image, camera_params):
        estimated_poses = []

        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find basic information about tag (center location, ID, family...)
        results = self.detector.detect(gray)

        for result in results:
            # TODO: Undistort corners

            pose, e0, e1 = self.detector.detection_pose(result, camera_params)

            # Draw bounding box
            draw_bounding_box(image, result, camera_params, pose)

            estimated_poses.append({
                'pose': pose,
                'tag_id': result.tag_id,
                'tag_family': result.tag_family,
                'e0': e0,
                'e1': e1
            })

        return estimated_poses




