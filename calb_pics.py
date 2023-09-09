import cv2
import os
import time

# Constants for ChArUco board
SQUARE_LENGTH = 0.10
MARKER_LENGTH = 0.08
DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
BOARD = cv2.aruco.CharucoBoard_create(2, 4, SQUARE_LENGTH, MARKER_LENGTH, DICT)

def show_charuco_board(board, width=1280, height=720):
    """Display a Charuco board for visualization."""
    # Draw the ChArUco board on a blank image
    board_image = board.draw((width, height))
    
    # Display the board
    cv2.imshow('ChArUco Board', board_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_next_attempt_folder(base_directory="Calibration\\Pics"):
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

    folder_index = 0
    count = 0

    countdown_start_time = None

    print(f"Press 'c' to capture a set of images. Number of images per press: {num_images_per_press}.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # ArUco marker detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, DICT)
        frame_with_markers = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)

        # ChArUco corners interpolation
        all_corners_detected = False
        if ids is not None:
            _, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, BOARD)
            frame_with_markers = cv2.aruco.drawDetectedCornersCharuco(frame_with_markers, charuco_corners, charuco_ids)
            
            if charuco_corners is not None:
                all_corners_detected = len(charuco_corners) == (BOARD.chessboardCorners.shape[0])

        if all_corners_detected:
            if countdown_start_time is None:
                countdown_start_time = time.time()
            
            elapsed_time = time.time() - countdown_start_time
            seconds_remaining = 5 - int(elapsed_time)

            if seconds_remaining <= 0:
                # Capture image automatically
                current_folder = os.path.join(base_directory, f"set_{folder_index}_auto")
                if not os.path.exists(current_folder):
                    os.makedirs(current_folder)
                
                for _ in range(num_images_per_press):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    if resolution != downsample_resolution:
                        frame = cv2.resize(frame, downsample_resolution)
                    filename = os.path.join(current_folder, f"image_{count:02}.jpg")
                    cv2.imwrite(filename, frame)
                    print(f"Saved {filename}")
                    count += 1
                
                folder_index += 1
                count = 0
                countdown_start_time = None  # Reset countdown
            else:
                display_overlay(frame_with_markers, f"READY TO CAPTURE! {seconds_remaining}")
        else:
            countdown_start_time = None

        cv2.imshow('Camera Feed with Markers', frame_with_markers)

        key = cv2.waitKey(1)
        if key == ord('c'):
            current_folder = os.path.join(base_directory, f"set_{folder_index}")
            if not os.path.exists(current_folder):
                os.makedirs(current_folder)
            count = 0
            for _ in range(num_images_per_press):
                ret, frame = cap.read()
                if not ret:
                    break
                if resolution != downsample_resolution:
                    frame = cv2.resize(frame, downsample_resolution)
                filename = os.path.join(current_folder, f"image_{count:02}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Saved {filename}")
                count += 1

            folder_index += 1
            count = 0
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    #show_charuco_board(BOARD)
    capture_images()
