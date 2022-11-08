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

    def getPoses(self, images):

        # Make a list of estimated poses to add to
        estimated_poses = []

        # Find every target in the images
        for image_dict in images:
            image = image_dict['image']
            camera = image_dict['camera']

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

                pose, e0, e1 = self.detector.detection_pose(result, camera.camera_params)

                # Draw bounding box
                draw_bounding_box(image, result, camera.camera_params, pose)

                # TODO Finish
                # TODO: What are the 'e's?
                # TODO: Scale pose by tag size
                estimated_poses.append({
                    'pose': pose,
                    'camera': camera,
                    'tag_id': result.tag_id,
                    'tag_family' : result.tag_family
                })

            # Log number of tags found
            if estimated_poses:
                logger.debug(f"Estimated pose on {len(estimated_poses)} AprilTags")

        return estimated_poses
