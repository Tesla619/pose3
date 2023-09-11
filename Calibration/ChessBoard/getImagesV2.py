import cv2
import os
import time
import numpy as np

# Constants for Chessboard
CHESSBOARD_SIZE = (7, 6)  # 7x6 grid means 8x7 corners
SQUARE_SIZE = 0.10

# Define the camera matrix and distortion coefficients
cameraMatrix = np.array(
    [
        [6.73172250e02, 0.00000000e00, 3.21652381e02],
        [0.00000000e00, 6.73172250e02, 2.40854103e02],
        [0.00000000e00, 0.00000000e00, 1.00000000e00],
    ]
)
distCoeffs = np.array(
    [-2.87888863e-01, 9.67075352e-02, 1.65928771e-03, -5.19671229e-04, -1.30327183e-02]
)

def get_next_attempt_folder(base_directory="Calibration/ChessBoard/images"):
    attempt_number = 1
    while True:
        attempt_folder = os.path.join(base_directory, f"attempt_{attempt_number}")
        if not os.path.exists(attempt_folder):
            os.makedirs(attempt_folder)
            return attempt_folder
        attempt_number += 1

def display_overlay(frame, message):
    h, w, _ = frame.shape
    cv2.putText(frame, message, (w//5, h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5, cv2.LINE_AA)

def capture_images(num_images_per_press=5, resolution=(1280, 720), downsample_resolution=(640, 480)):
    base_directory = get_next_attempt_folder()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Couldn't open the webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    count = 0

    print(f"Press 'c' to capture an image.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        
        # Chessboard corner detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE)

        frame_with_corners = frame.copy()
        if found:
            frame_with_corners = cv2.drawChessboardCorners(frame_with_corners, CHESSBOARD_SIZE, corners, found)

        cv2.imshow('Camera Feed with Corners', frame_with_corners)

        key = cv2.waitKey(1)
        if key == ord('c'):
            if found:
                if resolution != downsample_resolution:
                    frame = cv2.resize(frame, downsample_resolution)
                filename = os.path.join(base_directory, f"image_{count:02}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Saved {filename}")
                count += 1
            else:
                print("No valid chessboard detected. Try again.")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_images()
