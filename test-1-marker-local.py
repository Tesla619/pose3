import random
import time
import asyncio
import websockets
import socket
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util

# Load the dictionary and parameters
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
parameters = cv2.aruco.DetectorParameters_create()

# Define the size of the markers (in meters)
marker_size = 0.05

red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)

cap = cv2.VideoCapture(0)

# Define the camera matrix and distortion coefficients
# camera_matrix = np.array(
#     [
#         [6.73172250e02, 0.00000000e00, 3.21652381e02],
#         [0.00000000e00, 6.73172250e02, 2.40854103e02],
#         [0.00000000e00, 0.00000000e00, 1.00000000e00],
#     ]
# )
# distortion_coefficients = np.array(
#     [-2.87888863e-01, 9.67075352e-02, 1.65928771e-03, -5.19671229e-04, -1.30327183e-02]
# )

camera_matrix = np.loadtxt("Calibration\\Pics\\Final\\camera_matrix_hp.txt")
distortion_coefficients = np.loadtxt("Calibration\\Pics\\Final\\distortion_coefficients_hp.txt")

# camera_matrix = np.loadtxt("Calibration\\Pics\\Final\\camera_matrix_hp_OLD.txt")
# distortion_coefficients = np.loadtxt("Calibration\\Pics\\Final\\distortion_coefficients_hp_OLD.txt")

# camera_matrix = np.loadtxt("Calibration\\Pics\\Final\\camera_matrix_hp_first.txt")
# distortion_coefficients = np.loadtxt("Calibration\\Pics\\Final\\distortion_coefficients_hp_first.txt")

print("Main Camera Matrix:\n", camera_matrix)
print("\nMain Distortion Coefficients:\n", distortion_coefficients)

def receive_frames():
    while True:
        ret, frame = cap.read()

        # Check if the frame was read successfully
        if not ret:
            print("Error: Could not read frame.")
            break

        frame_width = 640
        frame_height = 480
        size = (frame_width, frame_height)

        ############################## ArUco Detection #########################################

        # Convert frame to grayscale for ArUco detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect the markers in the frame
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            gray, dictionary, parameters=parameters
        )

        # If markers are detected, estimate their pose
        if ids is not None:  # and len(ids) >= 2:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_size, camera_matrix, distortion_coefficients
            )
            
            # Draw the axes of the markers
            for i in range(len(ids)):
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                cv2.aruco.drawAxis(
                    frame,
                    camera_matrix,
                    distortion_coefficients,
                    rvecs[i],
                    tvecs[i],
                    marker_size,
                )

            if ids[i] == 0:  # FOR TESTING
                # Rotation matrix
                RVX = (
                    f"ID{ids[i]}: Rotation Vector X: {rvecs[i][0][0] * (180/np.pi)} degrees"
                )
                RVY = (
                    f"ID{ids[i]}: Rotation Vector Y: {rvecs[i][0][1] * (180/np.pi)} degrees"
                )
                RVZ = (
                    f"ID{ids[i]}: Rotation Vector Z: {rvecs[i][0][2] * (180/np.pi)} degrees"
                )   

                # Translation matrix
                TVX = f"ID{ids[i]}: Translation Vector X: {tvecs[i][0][0]} meters"
                TVY = f"ID{ids[i]}: Translation Vector Y: {tvecs[i][0][1]} meters"
                TVZ = f"ID{ids[i]}: Translation Vector Z: {tvecs[i][0][2]} meters"

                xdef = 120
                ydef = 150
                yoff = 25
                size = 0.4
                thick = 1

                cv2.putText(
                    frame,
                    RVX,
                    (xdef, ydef + (0000 * 0) + 0),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    size,
                    red,
                    thick,
                )
                
                cv2.putText(
                    frame,
                    RVY,    
                    (xdef, ydef + (yoff * 1) + 0),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    size,
                    green,
                    thick,
                )
                
                cv2.putText(
                    frame,
                    RVZ,
                    (xdef, ydef + (yoff * 2) + 0),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    size,
                    blue,
                    thick,
                )

                cv2.putText(
                    frame,
                    TVX,
                    (xdef, ydef + (yoff * 3) + 9),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    size,
                    red,
                    thick,
                )

                cv2.putText(
                    frame,
                    TVY,
                    (xdef, ydef + (yoff * 4) + 9),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    size,
                    green,
                    thick,
                )

                cv2.putText(
                    frame,
                    TVZ,
                    (xdef, ydef + (yoff * 5) + 9),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    size,
                    blue,
                    thick,
                )

                # cv2.putText(image, f"{label}: {int(score*100)} %", (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
                
        # Display output
        cv2.imshow("Results", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyAllWindows()
            break            

if __name__ == "__main__":
    receive_frames()
