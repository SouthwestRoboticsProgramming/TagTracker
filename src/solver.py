# Solves for robot position based on results of found tags


# Stores location of tag relative to a chosen point
class TagInformation:
    def __init__(self, tag_family, tag_id, x, y, z, quaternion):
        self.tag_family = tag_family
        self.tag_id = tag_id
        self.x = x
        self.y = y
        self.z = z
        self.quaternion = quaternion

