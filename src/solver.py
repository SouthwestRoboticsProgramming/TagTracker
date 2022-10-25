# Solves for robot position based on results of found tags


# Stores location of tag relative to a chosen point

class TagPose:
    def __init__(self, tag_id, position, rotation_q):
        self.tag_id = tag_id
        self.position = position
        self.rotation_q = rotation_q

class CameraPose:
    def __init__(self, tag_id, position, rotation_q):
        self.tag_id = tag_id
        self.position = position
        self.rotation_q = rotation_q

class RobotPose:
    def __init__(self, position, rotation_q):
        self.position = position
        self.rotation_q = rotation_q

class RobotPoseSolver:
    def __init__(self, tag_poses, camera_pose):
        # Store the tags' positions based on their ID
        self.tags = {}
        for pose in tag_poses:
            self.tags[pose.tag_id] = pose

        # Store the camera's pose
        # TODO: Store multiple cameras like the tags are
        self.camera = camera_pose
    
    def solve(self, detect_results):
        """
        Solves for the robot's position based on the detection results

        detect_results should be a list of tag info
        # TODO: Should be a dict from camera ID to list of tag info when we have multiple cameras
        """

        if len(detect_results) == 0:
            return None

        # Estimate position with each tag
        estimates = []
        for tag_info in detect_results:
            estimates.append(self._estimate_pose(self.camera, tag_info))

        # Find average position
        result_x = 0
        result_y = 0
        result_z = 0
        for estimate in estimates:
            result_x += estimate.position[0]
            result_y += estimate.position[1]
            result_z += estimate.position[2]
        result_x /= len(estimates)
        result_y /= len(estimates)
        result_z /= len(estimates)

        # TODO: Figure out quaternion average
        return RobotPose((result_x, result_y, result_z), (1, 0, 0, 0))

    def _estimate_pose(self, camera_pose, tag_info):
        # TODO: Take camera pose and tag's world pose into account
        return RobotPose(tag_info['pose'], tag_info['quaternion'])
