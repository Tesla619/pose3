import cv2
import numpy as np

# Constants for ChArUco board
SQUARE_LENGTH = 0.09  # side length of the squares in meters
MARKER_LENGTH = 0.08  # side length of the markers in meters, adjust based on your board design
DICT = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_1000)
BOARD = cv2.aruco.CharucoBoard_create(2, 4, SQUARE_LENGTH, MARKER_LENGTH, DICT)

def read_images_from_directory(directory_path):
    import glob
    return [cv2.imread(img_path) for img_path in glob.glob(f"{directory_path}/*.jpg")]

def calibrate_camera(images):
    all_charuco_corners = []
    all_charuco_ids = []
    decimator = 0
    for image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, DICT)

        if len(corners) > 0:
            _, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, BOARD)
            if charuco_corners is not None and charuco_ids is not None and len(charuco_corners) > 3:
                all_charuco_corners.append(charuco_corners)
                all_charuco_ids.append(charuco_ids)

    imsize = gray.shape
    return cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, BOARD, imsize, None, None)

if __name__ == '__main__':
    image_directory = ('Calibration\\Pics\\')
    images = read_images_from_directory(image_directory)

    ret, camera_matrix, distortion_coefficients, _, _ = calibrate_camera(images)

    print("Camera Matrix:\n", camera_matrix)
    print("Distortion Coefficients:\n", distortion_coefficients)

    # Save to text files
    np.savetxt('camera_matrix_hp.txt', camera_matrix)
    np.savetxt('distortion_coefficients_hp.txt', distortion_coefficients)