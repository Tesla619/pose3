import numpy as np
import cv2
import cv2.aruco as aruco
import sys
import math
import time

def detect_ArUco(img):
    Detected_ArUco_markers = {}
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_100)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    parameters = aruco.DetectorParameters_create()
    corners, ids, _ = aruco.detectMarkers(gray , aruco_dict, parameters = parameters)
    if ids is not None:
        for i in range(len(ids)):
            Detected_ArUco_markers.update({ids[i][0]: corners[i]})
        return Detected_ArUco_markers
    else:
        return None


def Calculate_orientation_in_degree(Detected_ArUco_markers):
    ArUco_marker_angles = {}
    for key in Detected_ArUco_markers:
        corners = Detected_ArUco_markers[key]
        tl = corners[0][0]
        tr = corners[0][1]
        br = corners[0][2]
        bl = corners[0][3]
        top = (tl[0]+tr[0])/2, -((tl[1]+tr[1])/2)
        centre = (tl[0]+tr[0]+bl[0]+br[0])/4, -((tl[1]+tr[1]+bl[1]+br[1])/4)
        try:
            angle = round(math.degrees(np.arctan((top[1]-centre[1])/(top[0]-centre[0]))))
        except:
            # add conditioning here for different ids later on
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


def mark_ArUco(img,Detected_ArUco_markers,ArUco_marker_angles):
    for key in Detected_ArUco_markers:
        corners = Detected_ArUco_markers[key]
        tl = corners[0][0]
        tr = corners[0][1]
        br = corners[0][2]
        bl = corners[0][3]
        top = int((tl[0]+tr[0])//2), int((tl[1]+tr[1])//2)
        centre = int((tl[0]+tr[0]+bl[0]+br[0])//4), int((tl[1]+tr[1]+bl[1]+br[1])//4)
        img = cv2.line(img,top,centre,(255,0,0),3)
        img = cv2.circle(img,(int(tl[0]),int(tl[1])), 6, (100,100,100), -1)
        img = cv2.circle(img,(int(tr[0]),int(tr[1])), 6, (0,255,0), -1)
        img = cv2.circle(img,(int(br[0]),int(br[1])), 6, (100,100,255), -1)
        img = cv2.circle(img,(int(bl[0]),int(bl[1])), 6, (255,255,255), -1)
        img = cv2.circle(img,centre, 5, (0,0,255), -1)
        img = cv2.putText(img, str(key), centre, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 200), 3, cv2.LINE_AA)
        img = cv2.putText(img, str(ArUco_marker_angles[key]), top, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
    return img


cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    if(success):
            Detected_ArUco_markers = detect_ArUco(img)	
            if(Detected_ArUco_markers is not None):
                angle = Calculate_orientation_in_degree(Detected_ArUco_markers)		
                img = mark_ArUco(img,Detected_ArUco_markers,angle)
    cv2.imshow("Image", img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break