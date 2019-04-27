# USAGE
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat --video blink_detection_demo.mp4
# python detect_blinks.py --shape-predictor shape_predictor_68_face_landmarks.dat

# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import RPi.GPIO as gpio
from servo import *
#from datetime import datetime, timedelta
#import heapq


cap = cv2.VideoCapture(0)
# Get the Default resolutions
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

servo = initServo()


# Define the codec and filename.
#out = cv2.VideoWriter('output.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("-v", "--video", type=str, default="",
	help="path to input video file")
args = vars(ap.parse_args())

# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold
EYE_AR_UPPER_THRESH = 0.39
EYE_AR_LOWER_THRESH = 0.22
EYE_AR_CONSEC_FRAMES = 2

STARTED_SEQUENCE = False

# initialize the frame counters and the total number of blinks
COUNTER = 0
SECONDARY_COUNTER = 0
TOTAL = 0

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
# vs = FileVideoStream(args["video"]).start()
# fileStream = True
fileStream = False
vs = VideoStream(usePiCamera=True).start()
time.sleep(1.0)

print("[INFO] started video stream")

try:

	# loop over frames from the video stream
	while True:
		# if this is a file video stream, then we need to check if
		# there any more frames left in the buffer to process
		if fileStream and not vs.more():
			break

		# grab the frame from the threaded video file stream, resize
		# it, and convert it to grayscale
		# channels)
		frame = vs.read()

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# detect faces in the grayscale frame
		rects = detector(gray, 0)

		# loop over the face detections
		if len(rects) == 0:
			COUNTER = 0
			SECONDARY_COUNTER = 0
			STARTED_SEQUENCE = False
		
		for rect in rects:
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)

			# extract the left and right eye coordinates, then use the
			# coordinates to compute the eye aspect ratio for both eyes
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = eye_aspect_ratio(leftEye)
			rightEAR = eye_aspect_ratio(rightEye)

			# average the eye aspect ratio together for both eyes
			ear = (leftEAR + rightEAR) / 2.0

			# compute the convex hull for the left and right eye, then
			# visualize each of the eyes
			leftEyeHull = cv2.convexHull(leftEye)
			rightEyeHull = cv2.convexHull(rightEye)
			cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

			if (not STARTED_SEQUENCE):
				print('not started ' + str(COUNTER) + ' ear: ' + str(ear))
				if (COUNTER >= EYE_AR_CONSEC_FRAMES) and (ear <= EYE_AR_UPPER_THRESH):
					STARTED_SEQUENCE = True
					COUNTER = 0
					print('Started!')
					cv2.putText(frame, "Step 1", (180, 500),
						cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
				else:
					if (ear > EYE_AR_UPPER_THRESH):
						COUNTER += 1
						print('up')
					else:
						COUNTER = 0
						print('fail')
			else:
				COUNTER += 1
				print('counter ' + str(COUNTER) + ' ear: ' + str(ear))
				if (COUNTER > (3*EYE_AR_CONSEC_FRAMES)):
					print('TIMEOUt')
					COUNTER = 0
					SECONDARY_COUNTER = 0
					STARTED_SEQUENCE = False
					cv2.putText(frame, "TIMEOUT", (180, 500),
						cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)

				if (ear < EYE_AR_LOWER_THRESH):
					print('low')
					SECONDARY_COUNTER += 1

				if (SECONDARY_COUNTER >= EYE_AR_CONSEC_FRAMES):
					print('SUCCESS')
					TOTAL += 1
					
					rotate90(servo, -1)
					
					COUNTER = 0
					SECONDARY_COUNTER = 0
					STARTED_SEQUENCE = False
					cv2.putText(frame, "Step 2", (180, 500),
						cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
					


			# draw the total number of blinks on the frame along with
			# the computed eye aspect ratio for the frame
			cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
				cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
				cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

		# show the frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF

		#out.write(frame)

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

# do a bit of cleanup
except KeyboardInterrupt:
	print('yeet')
	cv2.destroyAllWindows()
	cap.release()
	#out.release()
	vs.stop()
	disposeServo(servo)
