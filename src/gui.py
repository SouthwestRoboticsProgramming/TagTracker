import cv2

DRAW_GUI = True

def drawBoundingBox(overlay, detector_result):
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