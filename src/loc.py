class Localization:
    def __init__(self):
        pass

    def getPosition(self, detection_poses):
        # Debugging
        for pose_dict in detection_poses:
            pose = pose_dict['pose']
            x = pose[0][3]
            y = pose[1][3]
            z = pose[2][3]
            print("X: {}, Y: {}, Z: {}".format(x,y,z))
