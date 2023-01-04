import cv2
import numpy as np
import json
import subprocess
import warnings

class Camera:
    def __init__(self, camera_options):
        camera_port = camera_options.get('port')
        cscore_camera = camera_port is None
        self.name = camera_options['name']
        self.robot_position = camera_options['robot_pose']

        # Extract params JSON
        try:
            location = f"camera_params/{camera_options['type']}.json"
            params_json = open(location, 'r')
            params = json.load(params_json)
            print(f"Camera params JSON loaded for {self.name}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            warnings.warn("Could not open camera parameters JSON, qutting")
            raise FileNotFoundError("Could not open cameara params JSON '{}' for {}, \
                is the path relative to /camera_params?".format(camera_options['type'], self.name)) from e

        params_json.close()

        # Convert params to tuple
        self.camera_params = (params['fx'], params['fy'], params['cx'], params['cy'])
        self.distortion = params['dist']
        self.matrix = np.array([
            self.camera_params[0], 0, self.camera_params[2],
            0, self.camera_params[1], self.camera_params[3],
            0, 0, 1
        ]).reshape(3, 3)

        # Configure it as a cscore camera
        if cscore_camera:
            self.capture = _CameraServerCamera(camera_options)
            return


        self.capture = _USBCamera(self.name, camera_port)

    # # Get an image from the camera
    # def read(self):
    #     return np.zeros(shape=(1080, 1920, 3), dtype=np.uint8)

class _USBCamera(Camera):
    capture = None

    def __init__(self, name, camera_port):
        self.capture = cv2.VideoCapture(camera_port)

        print(f"Starting camera '{name}' on port {camera_port}")

    def read(self):
        ret, frame = self.capture.read()
        if not ret:
            print(f"{self.name} was unable to capture an image")
            frame = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

            # Overlay failed message
            cv2.putText(frame, "No input", (80, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (20, 20, 20))

        return frame

    def __del__(self):
        self.capture.release()

class _CameraServerCamera(Camera):

    stream = None
    image_base = None

    def __init__(self, config_dict):
        from cscore import CameraServer, VideoSource, UsbCamera

        path = config_dict['path']

        print(f"Starting camera '{self.name}' on {path}")

        cs = CameraServer.getInstance()
        camera = UsbCamera(self.name, path)

        # Configure camera
        camera.setConfigJson(json.dumps(config_dict))
        camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        self.stream = cs.getVideo(camera=camera)

        # It runs much quicker if an image is preallocated
        width = config_dict['width']
        height = config_dict['height']

        # FIXME: Possibly breaks with B+W camera
        self.image_base = np.zeros(shape=(height, width, 3), dtype=np.uint8)

    def read(self):
        img_time, img = self.stream.grabFrame(self.image_base)

        return self.image_base if img_time == 0 else img



# Works by running the command "udevadm info --name/dev/video0"
def get_cam_serial(cam_id):
    FILTER = "ID_SERIAL_SHORT="

    p = subprocess.Popen('udevadm info --name=/dev/video{} | grep {} | cut -d "=" -f 2'.format(cam_id, FILTER),
                         stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p.status = p.wait()
    response = output.decode('utf-8')
    return response.replace('\n', '')

def get_camera_by_serial(serial):
    for cam_id in range(0, 10):
        s = get_cam_serial(cam_id)
        if s == serial:
            return cam_id
