import math
import time
import cv2
import numpy as np

# Define your custom dictionary of marker sizes and IDs
marker_sizes = {}  

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
    # c.send(data.encode())
    
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
            # if (0 <= id <= 3) or (8 <= id <= 11):   
            if id == 0 or id == 8:
                angle = round(math.degrees(np.arctan((top[1]-centre[1])/(top[0]-centre[0])))) - 90            
            else:
                angle = round(math.degrees(np.arctan((top[1]-centre[1])/(top[0]-centre[0])))) #+ 90
        except:     
            # if (0 <= id <= 3) or (8 <= id <= 11):       
            if id == 0 or id == 8:
                if(top[1]>centre[1]):
                    angle = 0
                elif(top[1]<centre[1]):
                    angle = -90
            else:
                if(top[1]>centre[1]):
                    angle = 90
                elif(top[1]<centre[1]):
                    angle = 270        
        
        # if not (0 <= id <= 3) or (8 <= id <= 11):               
        #     if(top[0] >= centre[0] and top[1] < centre[1]):
        #         print(f"{id}: angle: {angle}")
        #         angle = 360 + angle   
        #         print(f"{id}: new angle: {angle}")
        #     elif(top[0]<centre[0]): # was 180 + angle
        #         # angle = angle - 90
        #         angle = angle * -1 
        #         angle = angle
        
        if id == 4 or id == 12:               
            if(top[0] >= centre[0] and top[1] < centre[1]):
                print(f"1. {id}: angle_O: {angle}")
                angle = 360 + angle              
                print(f"1. {id}: angle_C: {angle}")     
            elif(top[0]<centre[0]):
                print(f"2. {id}: angle_O: {angle}")                
                angle = 180 + angle                         
                print(f"2. {id}: angle_C: {angle}")
        else:    
            if(top[0] >= centre[0] and top[1] < centre[1]):
                print(f"3. {id}: angle_O: {angle}")
                # angle = 360 + angle                
                angle = angle  + 0
                print(f"3. {id}: angle_C: {angle}")
            elif(top[0]<centre[0]):
                print(f"4. {id}: angle_O: {angle}")
                # angle = 180 + angle
                angle = angle + 180 # most likely
                print(f"4. {id}: angle_C: {angle}")
          
        
        ArUco_marker_angles.update({id: angle})
        
    return ArUco_marker_angles


def mark_ArUco(img, Detected_ArUco_markers,ArUco_marker_angles):
    for id in Detected_ArUco_markers:
        corners = Detected_ArUco_markers[id]
        tl = corners[0][0]
        tr = corners[0][1]
        br = corners[0][2]
        bl = corners[0][3]
        top = int((tl[0]+tr[0])//2), int((tl[1]+tr[1])//2)
        centre = int((tl[0]+tr[0]+bl[0]+br[0])//4), int((tl[1]+tr[1]+bl[1]+br[1])//4)
        img = cv2.line(img,top,centre,(255,0,0),3)
        img = cv2.circle(img, (int(tl[0]),int(tl[1])), 6, (100,100,100), -1)
        img = cv2.circle(img, (int(tr[0]),int(tr[1])), 6, (0,255,0), -1)
        img = cv2.circle(img, (int(br[0]),int(br[1])), 6, (100,100,255), -1)
        img = cv2.circle(img, (int(bl[0]),int(bl[1])), 6, (255,255,255), -1)
        img = cv2.circle(img,centre, 5, (0,0,255), -1)
        img = cv2.putText(img, str(id), centre, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 200), 3, cv2.LINE_AA)
        img = cv2.putText(img, str(ArUco_marker_angles[id]), top, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
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
        
        while True:
            fps_count += 1
            ret, frame = video_capture.read()
            
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