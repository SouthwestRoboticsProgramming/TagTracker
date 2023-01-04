# Used to send values back to RoboRIO
from networktables import NetworkTables

class Network:
    table = None

    targets = []

    def __init__(self, ip, max_tags):
        if ip:
            print(f"Connecting to NetworkTables at {ip}")
            NetworkTables.initialize(server=ip)
        else:
            print("Starting NetworkTables server")
            NetworkTables.initialize()

        # Create a table to publish values to
        self.table = NetworkTables.getTable('tagtracker')

        for i in range(max_tags):
            self.targets.append(_Tag(self.table, i))

    def put(self, estimated_poses):

        def sort_distance_to_center(value):
            return value['distance_to_center_squared']

        # Sort poses to find best
        estimated_poses.sort(key=sort_distance_to_center)

        for i, pose in enumerate(estimated_poses):
            if i > len(self.targets): # Can only publish so many poses
                self.targets[i].set(
                    pose['tag_id'],
                    pose['pose'],
                    pose['e0'],
                    pose['e1']
                )

class _Tag:
    id_entry = None
    pose_entry = None
    e0_entry = None
    e1_entry = None

    def __init__(self, table, number):
        self.id_entry = table.getEntry(f"target{number}/id")
        self.pose_entry = table.getEntry(f"target{number}/pose")
        self.e0_entry = table.getEntry(f"target{number}/e0")
        self.e1_entry = table.getEntry(f"target{number}/e1")

    def set(self, tag_id, pose, e0, e1):
        self.id_entry.putNumber(tag_id)
        self.pose_entry.putNumberArray(pose)
        self.e0_entry.putNumber(e0)
        self.e1_entry.putNumber(e1)

    def get(self):
        return (
            self.id_entry.getNumber(0),
            self.pose_entry.getNumberArray([0,0,0]),
            self.e0_entry.getNumber(0.0),
            self.e1_entry.getNumber(0.0)
        )

    

