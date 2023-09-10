import cv2
import numpy as np
import glob

# Constants for ChArUco board
SQUARE_LENGTH = 0.10
MARKER_LENGTH = 0.08
DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
BOARD = cv2.aruco.CharucoBoard_create(2, 4, SQUARE_LENGTH, MARKER_LENGTH, DICT)

def read_filenames_from_directory(directory_path):
    return glob.glob(f"{directory_path}/*.jpg")

def calibrate_camera(filenames):
    all_charuco_corners = []
    all_charuco_ids = []
    for fname in filenames:
        image = cv2.imread(fname)
        if image is None:
            print(f"Failed to load {fname}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, DICT)
        
        if len(corners) > 0:
            img_with_aruco = cv2.aruco.drawDetectedMarkers(image.copy(), corners, ids)
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
    return cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, BOARD, imsize, None, None)

if __name__ == '__main__':
    image_directory = 'Calibration\\Pics\\Final'
    filenames = read_filenames_from_directory(image_directory)
    ret, camera_matrix, distortion_coefficients, _, _ = calibrate_camera(filenames)

    print("Camera Matrix:\n", camera_matrix)
    print("Distortion Coefficients:\n", distortion_coefficients)

    # Save to text files
    np.savetxt('Calibration\\camera_matrix_hp.txt', camera_matrix)
    np.savetxt('Calibration\\distortion_coefficients_hp.txt', distortion_coefficients)
