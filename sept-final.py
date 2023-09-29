import math
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

#print(marker_sizes)

# Define the camera matrix and distortion coefficients
camera_matrix = np.loadtxt("Calibration\\Pics\\Final\\camera_matrix_hp.txt")
distortion_coefficients = np.loadtxt("Calibration\\Pics\\Final\\distortion_coefficients_hp.txt")

# PATH_TO_SAVED_MODEL = "customTF2/data/inference_graph/saved_model"
# PATH_TO_SAVED_MODEL = "TF_Models/20k/saved_model"
# PATH_TO_SAVED_MODEL = "TF_Models/2k/saved_model"
# PATH_TO_SAVED_MODEL = "TF_Models/OLD/saved_model"
PATH_TO_SAVED_MODEL = "TF_Models/2k_v2/saved_model"

# Load label map and obtain class names and ids
category_index = label_map_util.create_category_index_from_labelmap(
    "TF_Models\label_map.pbtxt", use_display_name=True
)

def send_to_matlab(variable):
    # Convert variable to a string and add the terminator
    data = str(variable) + "\n"  # Newline character as the terminator

    # Send the data
    c.send(data.encode())


def visualise_on_image(image, bboxes, labels, scores, thresh):
    (h, w, d) = image.shape
    for bbox, label, score in zip(bboxes, labels, scores):
        if score > thresh:
            xmin, ymin = int(bbox[1] * w), int(bbox[0] * h)
            xmax, ymax = int(bbox[3] * w), int(bbox[2] * h)

            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(
                image,
                f"{label}: {int(score*100)} %",
                # (xmin, ymin),
                (xmax+10, ymax-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                2,
            )
    return image


async def receive_frames():
    global previous_angle
    global previous_angles 
    async with websockets.connect("ws://192.168.0.101:8765") as websocket:
    #async with websockets.connect("ws://192.168.1.66:8765") as websocket:
        # Load the model
        print("Loading saved model ...")
        detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)
        print("Model Loaded!")

        # video_capture = cv2.VideoCapture(0)
        start_time = time.time()

        frame_width = 640  # int(video_capture.get(3))
        frame_height = 480  # int(video_capture.get(4))
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
            # ret, frame = video_capture.read() # Make to receive from laptop webcam

            # Receive the frame from the websocket
            data = await websocket.recv()

            # Convert the bytes to a NumPy array
            buffer = np.frombuffer(data, dtype=np.uint8)

            # Decode the JPEG image
            frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

            ############################## Object Detection #########################################

            # frame = cv2.flip(frame, 1)
            image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
            # The model expects a batch of images, so also add an axis with `tf.newaxis`.
            input_tensor = tf.convert_to_tensor(image_np)[tf.newaxis, ...]

            # Pass frame through detector
            detections = detect_fn(input_tensor)

            # Set detection parameters
            score_thresh = 0.4  # Minimum threshold for object detection was 0.4
            max_detections = 1

            # All outputs are batches tensors.
            # Convert to numpy arrays, and take index [0] to remove the batch dimension.
            # We're only interested in the first num_detections.
            scores = detections["detection_scores"][0, :max_detections].numpy()
            bboxes = detections["detection_boxes"][0, :max_detections].numpy()
            labels = (
                detections["detection_classes"][0, :max_detections]
                .numpy()
                .astype(np.int64)
            )
            labels = [category_index[n]["name"] for n in labels]

            # Display detections
            visualise_on_image(frame, bboxes, labels, scores, score_thresh)
            # frame = cv2.flip(frame, 1) # Flip frame back to normal

            ############################## ArUco Detection #########################################

            gray = cv2.cvtColor(
                frame, cv2.COLOR_BGR2GRAY
            )  # Convert frame to grayscale for ArUco detection

            # Detect the markers in the frame
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
                gray, dictionary, parameters=parameters
            )

            # If markers are detected, estimate their pose
            if ids is not None:  # and len(ids) >= 2: 
                for desired_id in desired_marker_order:
                    for i in range(len(ids)):
                        marker_id = ids[i][0]
                        marker_size = marker_sizes.get(marker_id, None)

                        if marker_size is not None and marker_id == desired_id:
                        #if marker_size is not None:
                            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                            [corners[i]], marker_size, camera_matrix, distortion_coefficients
                        )
                            # Draw the axes of the markers
                            cv2.aruco.drawDetectedMarkers(frame, [corners[i]], np.array([marker_id]))
                            cv2.aruco.drawAxis(
                                frame,
                                camera_matrix,
                                distortion_coefficients,
                                rvecs[0], # was rvecs[i]
                                tvecs[0], # was tvecs[i]
                                marker_size,
                            )      
                            
                            # Estimate the current orientation angle
                            angle = rvecs[0][0][0] * (180 / np.pi) - 167   
                            buffer = angle * angle     
                            filtered_angle = math.sqrt(buffer)
                            
                            if (0 <= marker_id <= 3):
                                cv2.putText(
                                    frame,                            
                                    f"{0}",
                                    (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.5,
                                    (255, 255, 255),
                                    2,
                                )        
                            # elif (4 <= marker_id <= 7):
                            #     cv2.putText(
                            #         frame,                            
                            #         f"{int(filtered_angle) + 90}",
                            #         (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
                            #         cv2.FONT_HERSHEY_SIMPLEX,
                            #         1.5,
                            #         (255, 255, 255),
                            #         2,
                            #     )
                            elif (12 <= marker_id <= 17):
                                cv2.putText(
                                    frame,                            
                                    #f"{int(filtered_angle) + 90}",
                                    "90",
                                    (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.5,
                                    (255, 255, 255),
                                    2,
                                )
                            else:                                
                                cv2.putText(
                                    frame,                            
                                    #f"{round(filtered_angle, 2)}",
                                    f"{int(filtered_angle)}",
                                    (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.5,
                                    (255, 255, 255),
                                    2,
                                )

                            # Interpolate the joint movment on each marker
                            # Logic of combination of markers to determine the robot's pose
                            # Send the robot's pose to matlab via websocket
                            
                            if fps_count >= 20:                                
                                if not (0 <= marker_id <= 3):                                    
                                    
                                    # if (4 <= marker_id <= 7):
                                    #     numbers.append(int(filtered_angle) + 90)
                                    # else:
                                    #   numbers.append(int(filtered_angle))                                        
                                    numbers.append(int(filtered_angle))
                                    # Increment the counter                                      
                                    counter += 1     

                                # Check if we have added 4 values, then add a fixed 0 and send to MATLAB
                                    if counter == 2:
                                        numbers.append(0)
                                        numbers.append(0)
                                        send_to_matlab(numbers)  # Assuming you have a function send_to_matlab                                    
                                        numbers = []  # Reset the list
                                        counter = 0  # Reset the counter
                                        numbers.append(int(0))
                                        fps_count = 0

                            # Check if there are remaining values in the list (less than 4)
                            # if numbers:
                            #     # Add 0 to complete the list
                            #     while len(numbers) < 4:
                            #         numbers.append(0)
                            #     send_to_matlab(numbers)  # Send the remaining values to MATLAB


                            # # Just to Generate movment for testing                    
                            # result = ",".join(map(str, filtered_angle))
                            # send_to_matlab(result)           # Send the robot's pose to matlab via websocket as one string to be parsed

            ############################## Output Overlays #########################################

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

        # video_capture.release()
        c.close()


if __name__ == "__main__":    
    # Initialize variables
    # window_size = 10  # Adjust the window size as needed
    # current_orientation = 0.0
    # previous_angle = 0.0
    # previous_angles = [0.0] * window_size
    
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Setting the machine as server for matlab to connect to
    s.bind(("localhost", 12345))

    # put the socket into listening mode
    s.listen(5)

    # establish a connection with matlab
    c, addr = s.accept()

    # receive webcam feed
    asyncio.get_event_loop().run_until_complete(receive_frames())
