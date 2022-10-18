# Apriltag Tracker for FRC

This is a python script to track the new Apriltags posted on the FRC field.


## Installation

1. **Install Anaconda** using the steps listed on `https://docs.anaconda.com/anaconda/install/index.html`.

2. **Create an Anaconda virtual envirionment**, this lets us have a specific version of python set up for vision. On linux, run the command `conda create -n apriltags python=3.8`.

3. **Install python dependencies**:
* Install opencv through the command `pip install opencv-contrib-python`. This works for both windows and linux.
* Install apriltag through the command `pip install apriltag`. This works for both windows and linux.

## Setup

1. **Print out chessboad for camera calibration**. I found sucess with the one in the `images` directory.
2. **Run the script `calibrate_camera.py`** with flags for columns, rows, square size, and camera ID. <br>
90% of the time, the camera ID is 0, if not, try IDs 0-10. <br>
Once you get the script to run, hold the camera so that it can see the entirety of the chessboard. Once you get messages in the terminal telling you that it has aquired the chessboard, you can hit the 'q' button to quit. Results from the calibration will be printed in the terminal.

3. **Add the calibration results to `tracker.py`**. Look for the line that matches the output line from the `calibrate_camera.py` script.
