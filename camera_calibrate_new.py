import cv2
import numpy as np
import glob

# Constants for ChArUco board
# SQUARE_LENGTH = 0.118     # A1
# MARKER_LENGTH = 0.088     # A1

SQUARE_LENGTH = 0.057       # A3
MARKER_LENGTH = 0.043       # A3

DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
BOARD = cv2.aruco.CharucoBoard_create(5, 7, SQUARE_LENGTH, MARKER_LENGTH, DICT)

def read_filenames_from_directory(directory_path):
    return glob.glob(f"{directory_path}/*.jpg")

def calibrate_camera(filenames):
    all_charuco_corners = []
    all_charuco_ids = []
    
    imsize = None  # Default assignment

    for fname in filenames:        
        image = cv2.imread(fname)           
        if image is None:
            print(f"Failed to load {fname}")
            continue
        
        resized_image = cv2.resize(image, (640, 480))
        gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, DICT)
        
        if len(corners) > 0:
            img_with_aruco = cv2.aruco.drawDetectedMarkers(resized_image.copy(), corners, ids)
            cv2.imshow(fname, img_with_aruco)  # Using filename as the window title
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            _, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, BOARD)
            if charuco_corners is not None and charuco_ids is not None and len(charuco_corners) > 4: # was 3 instead of 2
                all_charuco_corners.append(charuco_corners)
                all_charuco_ids.append(charuco_ids)
            else:
                print(f"Charuco corners not found for {fname} or less than 4 corners detected.")
        else:
            img_with_aruco = cv2.aruco.drawDetectedMarkers(image.copy(), corners, ids)
            cv2.imshow(fname, img_with_aruco)  # Using filename as the window title
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            print(f"Aruco markers not detected in {fname}.")

        imsize = gray.shape
        print(fname)
        
        if imsize is None:
            raise ValueError("Failed to process any images for calibration.")
    
    return cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, BOARD, imsize, None, None)

if __name__ == '__main__':
    image_directory = 'Calibration\\Pics\\Final'
    filenames = read_filenames_from_directory(image_directory)    
    ret, camera_matrix, distortion_coefficients, _, _ = calibrate_camera(filenames)

    print("Camera Matrix:\n", camera_matrix)
    print("Distortion Coefficients:\n", distortion_coefficients)

    # Save to text files
    np.savetxt('Calibration\\Pics\\Final\\camera_matrix_hp.txt', camera_matrix)
    np.savetxt('Calibration\\Pics\\Final\\distortion_coefficients_hp.txt', distortion_coefficients)