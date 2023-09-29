import sys
import math
import time
import numpy as np
import cv2
import cv2.aruco as aruco

def detect_aruco(image):	
    detected_aruco_markers = {}
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector_parameters = aruco.DetectorParameters_create()
    aruco_corners, aruco_ids, _ = aruco.detectMarkers(grayscale_image , aruco_dict, detector_parameters = detector_parameters)
    for index in range(len(aruco_ids)):
        detected_aruco_markers.update({aruco_ids[index][0]: aruco_corners[index]})
    return detected_aruco_markers


def calculate_orientation_in_degrees(detected_aruco_markers):
    ArUco_marker_angles = {}
    for key in detected_aruco_markers:
        aruco_corners = detected_aruco_markers[key]
        top_left = aruco_corners[0][0]	
        top_right = aruco_corners[0][1]	
        bottom_right = aruco_corners[0][2]	
        bottom_left = aruco_corners[0][3]	
        top = (top_left[0]+top_right[0])/2, -((top_left[1]+top_right[1])/2)
        centre = (top_left[0]+top_right[0]+bottom_left[0]+bottom_right[0])/4, -((top_left[1]+top_right[1]+bottom_left[1]+bottom_right[1])/4)
        try:
            angle = round(math.degrees(np.arctan((top[1]-centre[1])/(top[0]-centre[0]))))
        except:
            # add some conditioning here
            if(top[1]>centre[1]):
                angle = 90
            elif(top[1]<centre[1]):
                angle = 270
        if(top[0] >= centre[0] and top[1] < centre[1]):
            angle = 360 + angle
        elif(top[0]<centre[0]):
            angle = 180 + angle
        ArUco_marker_angles.update({key: angle})
    return ArUco_marker_angles

def mark_ArUco(image,detected_aruco_markers,ArUco_marker_angles):
    for key in detected_aruco_markers:
        aruco_corners = detected_aruco_markers[key]
        top_left = aruco_corners[0][0]	
        top_right = aruco_corners[0][1]	
        bottom_right = aruco_corners[0][2]	
        bottom_left = aruco_corners[0][3]	
        top = int((top_left[0]+top_right[0])//2), int((top_left[1]+top_right[1])//2)
        centre = int((top_left[0]+top_right[0]+bottom_left[0]+bottom_right[0])//4), int((top_left[1]+top_right[1]+bottom_left[1]+bottom_right[1])//4)
        image = cv2.line(image,top,centre,(255,0,0),3)
        image = cv2.circle(image,(int(top_left[0]),int(top_left[1])), 6, (100,100,100), -1)
        image = cv2.circle(image,(int(top_right[0]),int(top_right[1])), 6, (0,255,0), -1)
        image = cv2.circle(image,(int(bottom_right[0]),int(bottom_right[1])), 6, (100,100,255), -1)
        image = cv2.circle(image,(int(bottom_left[0]),int(bottom_left[1])), 6, (255,255,255), -1)
        image = cv2.circle(image,centre, 5, (0,0,255), -1)
        image = cv2.putText(image, str(key), centre, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 200), 3, cv2.LINE_AA)
        image = cv2.putText(image, str(ArUco_marker_angles[key]), top, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
    return image

cap = cv2.VideoCapture(0)
while True:
    success, image = cap.read()
    if(success):
            detected_aruco_markers = detect_aruco(image)	
            angle = calculate_orientation_in_degrees(detected_aruco_markers)				## finding orientation of aruco with respective to the menitoned scale in problem statement
            image = mark_ArUco(image,detected_aruco_markers,angle)
    cv2.imshow("Image", image)
    cv2.waitKey(1)
