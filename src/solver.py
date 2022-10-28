# Solves for robot position based on results of found tags
# from main import logger
# TODO: Make logging work
import numpy as np

class RobotPoseSolver:
    def __init__(self, environment_dict):
        # Unpack tag positions into master list
        tag_list = [None] * 586 # Total number of possible id's

        if not environment_dict['tags']:
            # logger.error('No tags defined! Quitting')
            raise Exception('No tags defined in environment JSON')

        for tag in environment_dict['tags']:
            # Match tag info up with their ID in the list
            id = tag['id']
            tag_list[id] = tag

        self.tag_list = tag_list
        self.tag_family = environment_dict['tag_family']

        if self.tag_family != "36h11":
            '''logger.warning('Are you sure that you want to look for, tags in the \
                 family {}. FRC uses 36h11'.format(self.tag_family))
            '''
    def solve(self, detection_poses):
        if not detection_poses:
            return

        # Master list of estimated poses to be combined
        estimated_poses_list = []

        # Apply camera and tag pose to estimated pose
        for pose_dict in detection_poses:
            estimated_pose = pose_dict['pose']
            camera_pose = pose_dict['camera'].robot_position
            tag_id = pose_dict['tag_id']
            tag_family = pose_dict['tag_family']

            # Find the tag info that matches that tag
            if not (self.tag_family in str(tag_family)):
                # TODO: Log warning
                break

            # Get the info for the tag
            tag_dict = self.tag_list[tag_id]

            if not tag_dict:
                # TODO: Log warning
                break

            tag_pose = tag_dict['transform']

            print(tag_dict['size'])

            # Convert to numpy arrarys for math
            estimated_pose = np.array(estimated_pose)
            camera_pose = np.array(camera_pose)
            tag_pose = np.array(tag_pose)

            # Take into account pose of the camera and tag
            without_camera = np.subtract(estimated_pose, tag_pose)
            final_pose = np.subtract(without_camera, camera_pose)
            # TODO: Test with rotation
            
            estimated_poses_list.append(final_pose)


        # Combine poses with average (at least for now)
        
        total = sum(estimated_poses_list)
        average = total / len(estimated_poses_list)

        print(average)



        return (0, 0, 0)
    