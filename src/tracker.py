import cv2
import apriltag
import numpy
import time

capture = cv2.VideoCapture(2)

# Setup detector
options = apriltag.DetectorOptions(families="tag36h11",
					nthreads=8,
					quad_decimate=1.0,
					quad_blur=1.0)
detector = apriltag.Detector(options)

# fx, fy, cx, cy = (439.728624791082, 414.9782292326142, 401.53713338042627, 211.2873582752417)
fx, fy, cx, cy = (1070.6915287567535, 1067.0306009135409, 323.3232144492538, 323.54374730910564)

camera_params = (fx, fy, cx, cy)




def _draw_pose(overlay, camera_params, tag_size, pose, z_sign=1):

    opoints = numpy.array([
        -1, -1, 0,
         1, -1, 0,
         1,  1, 0,
        -1,  1, 0,
        -1, -1, -2*z_sign,
         1, -1, -2*z_sign,
         1,  1, -2*z_sign,
        -1,  1, -2*z_sign,
    ]).reshape(-1, 1, 3) * 0.5*tag_size

    edges = numpy.array([
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

    K = numpy.array([fx, 0, cx, 0, fy, cy, 0, 0, 1]).reshape(3, 3)

    rvec, _ = cv2.Rodrigues(pose[:3,:3])
    tvec = pose[:3, 3]

    dcoeffs = numpy.zeros(5)

    ipoints, _ = cv2.projectPoints(opoints, rvec, tvec, K, dcoeffs)

    ipoints = numpy.round(ipoints).astype(int)
    
    ipoints = [tuple(pt) for pt in ipoints.reshape(-1, 2)]

    for i, j in edges:
        cv2.line(overlay, ipoints[i], ipoints[j], (0, 255, 0), 1, 16)

    

while True:
	tic = time.perf_counter();
	# Collect frame and convert to grayscale
	ret, image = capture.read()
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	results = detector.detect(gray)

	print("[INFO] {} total AprilTags detected".format(len(results)))

	# loop over the AprilTag detection results
	for r in results:
		# extract the bounding box (x, y)-coordinates for the AprilTag
		# and convert each of the (x, y)-coordinate pairs to integers
		(ptA, ptB, ptC, ptD) = r.corners
		ptB = (int(ptB[0]), int(ptB[1]))
		ptC = (int(ptC[0]), int(ptC[1]))
		ptD = (int(ptD[0]), int(ptD[1]))
		ptA = (int(ptA[0]), int(ptA[1]))
		# draw the bounding box of the AprilTag detection
		cv2.line(image, ptA, ptB, (0, 255, 0), 2)
		cv2.line(image, ptB, ptC, (0, 255, 0), 2)
		cv2.line(image, ptC, ptD, (0, 255, 0), 2)
		cv2.line(image, ptD, ptA, (0, 255, 0), 2)
		# draw the center (x, y)-coordinates of the AprilTag
		(cX, cY) = (int(r.center[0]), int(r.center[1]))
		cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
		# draw the tag family on the image
		tagFamily = r.tag_family.decode("utf-8")
		cv2.putText(image, tagFamily, (ptA[0], ptA[1] - 15),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		#print("[INFO] tag family: {}".format(tagFamily))

		pose, e0, e1 = detector.detection_pose(r, camera_params)
		
		print(pose)

		_draw_pose(image,
				camera_params,
				0.75,
				pose)

	cv2.imshow("Image", image)

	toc = time.perf_counter();
	print(f"FPS: {1 / (toc-tic):0.4f} ");

	# Q to stop the program
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break


capture.release()
cv2.destroyAllWindows()
