import math
import time
import asyncio
import websockets
import socket
# import tensorflow as tf
import cv2
import numpy as np
# from object_detection.utils import label_map_util

# # Load the dictionary and parameters
# dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
# parameters = cv2.aruco.DetectorParameters_create()

# Define your custom dictionary of marker sizes and IDs
marker_sizes = {}

# Initialize variables
window_size = 20  # Adjust the window size as needed
current_orientation = 0.0
previous_angle = 0.0
previous_angles = [0.0] * window_size   

# Set the size values for the specified ID ranges
for id_range, size in [(range(0, 4), 0.05), (range(12, 17), 0.05), (range(5, 12, 2), 0.065), (range(4, 7, 2), 0.08), (range(8, 11, 2), 0.125)]:
    for marker_id in id_range:
        marker_sizes[marker_id] = size

# Define the camera matrix and distortion coefficients
camera_matrix = np.loadtxt("Calibration\\Pics\\Final\\camera_matrix_hp.txt")
distortion_coefficients = np.loadtxt("Calibration\\Pics\\Final\\distortion_coefficients_hp.txt")

def send_to_matlab(variable):
    # Convert variable to a string and add the terminator
    data = str(variable) + "\n"  # Newline character as the terminator

    # Send the data
    c.send(data.encode())
    
# def detect_ArUco(img):
    


def Calculate_orientation_in_degree(Detected_ArUco_markers):
    ArUco_marker_angles = {}
    for id in Detected_ArUco_markers:        
        corners = Detected_ArUco_markers[id]
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
                print("90 HERE")
            elif(top[1]<centre[1]):
                angle = 270
                print("270 HERE")
        if(top[0] >= centre[0] and top[1] < centre[1]):
            angle = 360 + angle
            print("360 + HERE")
        elif(top[0]<centre[0]):
            angle = 180 + angle
            print("180 + here HERE")
            
        if (0 <= id <= 3) or (8 <= id <= 11):
            ArUco_marker_angles.update({id: angle-90})
        else:
            ArUco_marker_angles.update({id: angle})
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


def receive_frames():
        video_capture = cv2.VideoCapture(0)
        start_time = time.time()

        frame_width = int(video_capture.get(3))
        frame_height = int(video_capture.get(4))
        size = (frame_width, frame_height)

        # Initialize video writer
        result = cv2.VideoWriter(
            "Results/result.avi", cv2.VideoWriter_fourcc(*"MJPG"), 15, size
        )
        
        # Initialize variables
        numbers = []
        numbers.append(int(0))
        counter = 0
        fps_count = 0
        
        # Define the order of marker IDs to process
        # desired_marker_order = [0, 4, 8, 12]
        # desired_marker_order = [1, 5, 9, 13]
        # desired_marker_order = [2, 6, 10, 14]
        # desired_marker_order = [3, 7, 11, 15]
        desired_marker_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        
        while True:
            fps_count += 1
            ret, frame = video_capture.read()
            
            ############################## NEW ArUco Detection #########################################
            
            
            
            Detected_ArUco_markers = {}
            aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_100)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, _ = cv2.aruco.detectMarkers(gray , aruco_dict, parameters = parameters)
            
            if ids is not None:
                for i in range(len(ids)):
                    Detected_ArUco_markers.update({ids[i][0]: corners[i]})
                    angle = Calculate_orientation_in_degree(Detected_ArUco_markers)
                    frame = mark_ArUco(frame,Detected_ArUco_markers,angle)                  

            # FPS calculations
            end_time = time.time()
            fps = int(1 / (end_time - start_time))
            start_time = end_time

            cv2.putText(
                frame,
                f"FPS: {fps}",
                (20, frame_height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                2,
            )

            # Write output video
            result.write(frame)

            # Display output
            cv2.imshow("Results", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        video_capture.release()
        # c.close()


if __name__ == "__main__":    
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.bind(("localhost", 12345))
    # s.listen(5)
    # c, addr = s.accept()

    receive_frames()