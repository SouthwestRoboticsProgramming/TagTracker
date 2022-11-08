from itertools import product
from messenger import *

def _write_matrix(builder, matrix):
    # Write as column major
    for col, row in product(range(4), range(4)):
        # Float here since ShuffleLog stores matrices as float
        builder.add_float(matrix[row][col])

class ShuffleLogAPI:
    _MSG_QUERY_ENVIRONMENT = "TagTracker:QueryEnvironment"
    _MSG_ENVIRONMENT = "TagTracker:Environment"

    def __init__(self, conn_params, tag_infos, camera_infos):
        host = conn_params['host']
        port = conn_params['port']
        name = conn_params['name']
        mute_errors = conn_params['mute_errors']

        self.msg = MessengerClient(host, port, name, mute_errors=mute_errors)
        self.msg.add_handler(ShuffleLogAPI._MSG_QUERY_ENVIRONMENT, lambda t, r: self._on_query_environment(t, r))
        
        self.tag_infos = tag_infos
        self.camera_infos = camera_infos

    def read(self):
        self.msg.read_messages()

    def shutdown(self):
        self.msg.disconnect()

    # This is temporary
    def publish_detection_data(self, detections):
        builder = self.msg.prepare('TagTracker:TestData')
        builder.add_int(len(detections))
        for detect in detections:
            _write_matrix(builder, detect['pose'])
            _write_matrix(builder, detect['camera'].robot_position)
            builder.add_int(detect['tag_id'])
        builder.send()

    def publish_test_matrices(self, matrices):
        builder = self.msg.prepare('TagTracker:TestMtx')
        builder.add_int(len(matrices))
        for matrix in matrices:
            _write_matrix(builder, matrix)
        builder.send()

    def _on_query_environment(self, type, reader):
        print('[debug] sending environment data to ShuffleLog')
        builder = self.msg.prepare(ShuffleLogAPI._MSG_ENVIRONMENT)

        builder.add_int(len(self.tag_infos))
        for tag in self.tag_infos:
            builder.add_double(tag['size'])
            builder.add_int(tag['id'])
            _write_matrix(builder, tag['transform'])
        
        builder.add_int(len(self.camera_infos))
        for camera in self.camera_infos:
            builder.add_string(camera['name'])
            builder.add_int(camera['port'])
            _write_matrix(builder, camera['robot_pose'])

        builder.send()
