from __future__ import print_function
import numpy as np
import cv2
import argparse

# Copied from AprilTag library source code
# and edited to work with live video stream
def main():

    parser = argparse.ArgumentParser(
        description='calibrate camera intrinsics using OpenCV')

    parser.add_argument('-r', '--rows', metavar='N', type=int,
                        required=True,
                        help='# of chessboard corners in vertical direction')

    parser.add_argument('-c', '--cols', metavar='N', type=int,
                        required=True,
                        help='# of chessboard corners in horizontal direction')

    parser.add_argument('-s', '--size', metavar='NUM', type=float, default=1.0,
                        help='chessboard square size in user-chosen units (should not affect results)')

    parser.add_argument('-d', '--show-detections', action='store_true',
                        help='show detections in window')

    parser.add_argument('-i', '--input_camera', type=int,
                    default=0, help='change which camera to reac from by openCV id')

    options = parser.parse_args()

    if options.rows < options.cols:
        patternsize = (options.cols, options.rows)
    else:
        patternsize = (options.rows, options.cols)

    cam = options.input_camera

    sz = options.size

    x = np.arange(patternsize[0])*sz
    y = np.arange(patternsize[1])*sz

    xgrid, ygrid = np.meshgrid(x, y)
    zgrid = np.zeros_like(xgrid)
    opoints = np.dstack((xgrid, ygrid, zgrid)).reshape((-1, 1, 3)).astype(np.float32)

    imagesize = None

    cap = cv2.VideoCapture(cam)

    ipoints = []

    while True:

        ret, rgb = cap.read()
        
        if rgb is None:
            print('warning: error getting data from webcam, ending')
            break

        cursize = (rgb.shape[1], rgb.shape[0])
        
        if imagesize is None:
            imagesize = cursize
        else:
            assert imagesize == cursize

        print('Received frame of size {}x{}'.format(*imagesize))

        if len(rgb.shape) == 3:
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        else:
            gray = rgb
        
        retval, corners = cv2.findChessboardCorners(gray, patternsize, None)

        if options.show_detections:
            display = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            cv2.drawChessboardCorners(display, patternsize, corners, retval)
            cv2.imshow("Display", display)
            while cv2.waitKey(5) not in range(128): pass

        if not retval:
            # print('warning: no chessboard found, skipping')
            print('nothing found')
        else:
            print('checkerboard aquired!')
            ipoints.append( corners )


        cv2.imshow("RGB", rgb)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    flags = (cv2.CALIB_ZERO_TANGENT_DIST |
             cv2.CALIB_FIX_K1 |
             cv2.CALIB_FIX_K2 |
             cv2.CALIB_FIX_K3 |
             cv2.CALIB_FIX_K4 |
             cv2.CALIB_FIX_K5 |
             cv2.CALIB_FIX_K6)

    opoints = [opoints] * len(ipoints)

    retval, K, dcoeffs, rvecs, tvecs = cv2.calibrateCamera(opoints, ipoints, imagesize,
                                                           cameraMatrix=None,
                                                           distCoeffs=np.zeros(5),
                                                           flags=flags)

    assert( np.all(dcoeffs == 0) )
    
    fx = K[0,0]
    fy = K[1,1]
    cx = K[0,2]
    cy = K[1,2]

    params = (fx, fy, cx, cy)

    print()
    print('all units below measured in pixels:')
    print('  fx = {}'.format(K[0,0]))
    print('  fy = {}'.format(K[1,1]))
    print('  cx = {}'.format(K[0,2]))
    print('  cy = {}'.format(K[1,2]))
    print()
    print('pastable into Python:')
    print('  fx, fy, cx, cy = {}'.format(repr(params)))
    print()

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
