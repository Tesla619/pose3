import random
import time
import asyncio
import websockets
import socket
import tensorflow as tf
import cv2
import numpy as np
from object_detection.utils import label_map_util

# Simulated Arm Max Degree of Movment
max_angle = 45 + 1

# Load the dictionary and parameters
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
parameters = cv2.aruco.DetectorParameters_create()

# Define the size of the markers (in meters)
marker_size = 0.05

# Define the camera matrix and distortion coefficients
camera_matrix = np.array([[6.73172250e+02, 0.00000000e+00, 3.21652381e+02],
                          [0.00000000e+00, 6.73172250e+02, 2.40854103e+02],
                          [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
distortion_coefficients = np.array([-2.87888863e-01, 9.67075352e-02, 1.65928771e-03, -5.19671229e-04, -1.30327183e-02])

PATH_TO_SAVED_MODEL = "customTF2/data/inference_graph/saved_model"

# Load label map and obtain class names and ids
category_index=label_map_util.create_category_index_from_labelmap("customTF2/data/label_map.pbtxt",use_display_name=True)

def send_to_matlab(variable):
    # Convert variable to a string and add the terminator
    data = str(variable) + '\n'  # Newline character as the terminator
    
    # Send the data
    c.send(data.encode()) 

def visualise_on_image(image, bboxes, labels, scores, thresh):    
    (h, w, d) = image.shape
    for bbox, label, score in zip(bboxes, labels, scores):
        if score > thresh:
            xmin, ymin = int(bbox[1]*w), int(bbox[0]*h)
            xmax, ymax = int(bbox[3]*w), int(bbox[2]*h)
                  
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0,255,0), 2)            
            cv2.putText(image, f"{label}: {int(score*100)} %", (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)    
    return image

async def receive_frames():
    async with websockets.connect('ws://100.77.189.76:8765') as websocket:
        
        # Load the model
        print("Loading saved model ...")
        detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
        print("Model Loaded!")
    
        #video_capture = cv2.VideoCapture(0)
        start_time = time.time()
    
        frame_width = 640 # int(video_capture.get(3))
        frame_height = 480 # int(video_capture.get(4))
        size = (frame_width, frame_height)
    
        #Initialize video writer
        result = cv2.VideoWriter('5_Results/result.avi', cv2.VideoWriter_fourcc(*'MJPG'),15, size)   
    
        while True:
        
            #ret, frame = video_capture.read() # Make to receive from laptop webcam
            
            # Receive the frame from the websocket
            data = await websocket.recv()

            # Convert the bytes to a NumPy array
            buffer = np.frombuffer(data, dtype=np.uint8)

            # Decode the JPEG image
            frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                
            ############################## Object Detection #########################################
        
            #frame = cv2.flip(frame, 1)
            image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
            # The model expects a batch of images, so also add an axis with `tf.newaxis`.
            input_tensor = tf.convert_to_tensor(image_np)[tf.newaxis, ...]

            # Pass frame through detector
            detections = detect_fn(input_tensor)

            # Set detection parameters
            score_thresh = 0.4   # Minimum threshold for object detection
            max_detections = 1

            # All outputs are batches tensors.
            # Convert to numpy arrays, and take index [0] to remove the batch dimension.
            # We're only interested in the first num_detections.
            scores = detections['detection_scores'][0, :max_detections].numpy()
            bboxes = detections['detection_boxes'][0, :max_detections].numpy()
            labels = detections['detection_classes'][0, :max_detections].numpy().astype(np.int64)
            labels = [category_index[n]['name'] for n in labels]

            # Display detections
            visualise_on_image(frame, bboxes, labels, scores, score_thresh)
            #frame = cv2.flip(frame, 1) # Flip frame back to normal      

            ############################## ArUco Detection #########################################
        
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convert frame to grayscale for ArUco detection

            # Detect the markers in the frame
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

            # If markers are detected, estimate their pose
            if ids is not None: #and len(ids) >= 2:
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, distortion_coefficients)

                # Draw the axes of the markers
                for i in range(len(ids)):
                    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                    cv2.aruco.drawAxis(frame, camera_matrix, distortion_coefficients, rvecs[i], tvecs[i], marker_size)   

                    if ids[i] == 255: # FOR TESTING
                        # Rotation matrix                                
                        print("ID",ids[i], ": Rotation Vector X: ", rvecs[i][0][0] * (180/np.pi), "degrees")
                        print("ID",ids[i], ": Rotation Vector Y: ", rvecs[i][0][1] * (180/np.pi), "degrees")
                        print("ID",ids[i], ": Rotation Vector Z: ", rvecs[i][0][2] * (180/np.pi), "degrees")
                        print("\n\n") 

                        # Translation matrix                                
                        print("ID",ids[i], ": Translation Vector X: ", tvecs[i][0][0], "meters")
                        print("ID",ids[i], ": Translation Vector Y: ", tvecs[i][0][1], "meters")
                        print("ID",ids[i], ": Translation Vector Z: ", tvecs[i][0][2], "meters")
                        print("\n\n") 

                # Interpolate the joint movment on each marker 
                # Logic of combination of markers to determine the robot's pose            
                # Send the robot's pose to matlab via websocket
                
                # Just to Generate movment for testing
                numbers = random.sample(range(max_angle), 5)
                random_res = ','.join(map(str, numbers))
                send_to_matlab(random_res) # Send the robot's pose to matlab via websocket as one string to be parsed

            ############################## Output Overlays #########################################

            # FPS calculations
            end_time = time.time()
            fps = int(1/(end_time - start_time))
            start_time = end_time

            cv2.putText(frame, f"FPS: {fps}", (20,frame_height-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
        
            # Write output video
            result.write(frame)

            # Display output
            cv2.imshow("Results", frame)

            key = cv2.waitKey(1) & 0XFF
            if key == ord("q"):
                break                       
        
        #video_capture.release()
        c.close()

if __name__ == '__main__':
    
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     

    # Setting the machine as server for matlab to connect to
    s.bind(('localhost', 12345))

    # put the socket into listening mode
    s.listen(5)

    # establish a connection with matlab
    c, addr = s.accept()
    
    # receive webcam feed
    asyncio.get_event_loop().run_until_complete(receive_frames())