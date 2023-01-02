import cv2
import numpy as np

DRAW_GUI = True

# TODO-Ryan: Don't draw pose too and just make it one function
def draw_bounding_box(overlay, detector_result, camera_params, pose):
    # Copied from AprilTag source

    # Extract the bounding box (x, y)-coordinates for the AprilTag
    # and convert each of the (x, y)-coordinate pairs to integers
    (ptA, ptB, ptC, ptD) = detector_result.corners
    ptB = (int(ptB[0]), int(ptB[1]))
    ptC = (int(ptC[0]), int(ptC[1]))
    ptD = (int(ptD[0]), int(ptD[1]))
    ptA = (int(ptA[0]), int(ptA[1]))

    # draw the bounding box of the AprilTag detection
    cv2.line(overlay, ptA, ptB, (0, 255, 0), 2)
    cv2.line(overlay, ptB, ptC, (0, 255, 0), 2)
    cv2.line(overlay, ptC, ptD, (0, 255, 0), 2)
    cv2.line(overlay, ptD, ptA, (0, 255, 0), 2)

    # draw the center (x, y)-coordinates of the AprilTag
    (cX, cY) = (int(detector_result.center[0]), int(detector_result.center[1]))
    cv2.circle(overlay, (cX, cY), 5, (0, 0, 255), -1)

    # draw the tag family on the overlay
    tagFamily = detector_result.tag_family.decode("utf-8")
    cv2.putText(overlay, tagFamily, (ptA[0], ptA[1] - 15),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # draw the tag id on the overlay
    tagId = str(detector_result.tag_id)
    cv2.putText(overlay, tagId, ((cX, cY)),
    cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 2)

    draw_cube(overlay, camera_params, 1, pose)

# Not done TODO: Finish
def draw_cube(overlay, camera_params, tag_size, pose, z_sign=1):

    opoints =  np.array([
        -1, -1, 0,
         1, -1, 0,
         1,  1, 0,
        -1,  1, 0,
        -1, -1, -2*z_sign,
         1, -1, -2*z_sign,
         1,  1, -2*z_sign,
        -1,  1, -2*z_sign,
    ]).reshape(-1, 1, 3) * 0.5*tag_size

    edges = np.array([
        0, 1,
        1, 2,
        2, 3,
        3, 0,
        0, 4,
        1, 5,
        2, 6,
        3, 7,
        4, 5,
        5, 6,
        6, 7,
        7, 4
    ]).reshape(-1, 2)

    fx, fy, cx, cy = camera_params

    K = np.array([fx, 0, cx, 0, fy, cy, 0, 0, 1]).reshape(3, 3)

    rvec, _ = cv2.Rodrigues(pose[:3,:3])
    tvec = pose[:3, 3]

    dcoeffs = np.zeros(5)

    ipoints, _ = cv2.projectPoints(opoints, rvec, tvec, K, dcoeffs)

    ipoints = np.round(ipoints).astype(int)

    ipoints = [tuple(pt) for pt in ipoints.reshape(-1, 2)]

    for i, j in edges:
        cv2.line(overlay, ipoints[i], ipoints[j], (0, 255, 0), 1, 16)
