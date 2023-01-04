# Used to send values back to RoboRIO
from networktales import NetworkTablesInstance

class Network:
    table = None

    tags = []

    def __init__(self, team, is_server, max_tags):
        nt = NetworkTablesInstance.getDefault()
        if is_server:
            print("Starting NetworkTables server")
            nt.startServer()
        else:
            print(f"Connecting to NetworkTables for team {team}")
            nt.startClientTeam(team)
            nt.startDSClient()

        # Create a table to publish values to
        self.table = nt.getTable('tagtracker')

        for i in range(max_tags):
            self.tags.append(_Tag(self.table, i))

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

    

