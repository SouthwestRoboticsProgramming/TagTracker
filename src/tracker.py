from cameras import *
from overlays import *
import math
import apriltag
import cv2

class _DetectorOptions: # Converts JSON into object for apriltag's dector to read
    def __init__(self, dict=None):
        if dict:
            for key, value in dict.items():
                setattr(self, key, value)

class Detector:
    def __init__(self, options):
        options = _DetectorOptions(options)
        self.detector = apriltag.Detector(options)

    def get_estimated_poses(self, image, camera_params):

        # Make a list of estimated poses to add to
        estimated_poses = []

        # Convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find basic information about tag (center location, ID, family...)
        results = self.detector.detect(gray)

        # Estimate the pose of the camera relative to each target
        for result in results:
            # Undistort corners

            # print(result.corners)
            # for j in range(len(result.corners)):
            #     result.corners[j] = cv2.undistortPoints(result.corners[j].reshape(-1, 2), camera.matrix, dist_coeffs, P=new_mtx).reshape(-1)
            # print(result.corners)

            pose, e0, e1 = self.detector.detection_pose(result, camera_params)

            # Draw bounding box
            draw_bounding_box(image, result, camera_params, pose)


            # Find distance to center of image
            center = result.center
            diff_y = (image.shape[0] / 2) - center[1]
            diff_x = (image.shape[1] / 2) - center[0]
            
            distance_squared = math.pow(diff_x, 2) + math.pow(diff_y, 2)


            # TODO Finish
            # TODO: What are the 'e's?
            # TODO: Scale pose by tag size
            estimated_poses.append({
                'pose': pose,
                'tag_id': result.tag_id,
                'tag_family': result.tag_family,
                'e0': e0,
                'e1': e1,
                'distance_to_center_squared': distance_squared
            })

        return estimated_poses
