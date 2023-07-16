import cv2
import numpy as np

# Define the size of the Charuco board (in squares)
squaresX = 8
squaresY = 6
squareLength = 0.04  # length of each square (in meters)
markerLength = 0.02  # length of each marker (in meters)

# Create the Charuco board
board = cv2.aruco.CharucoBoard_create(squaresX, squaresY, squareLength, markerLength, cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250))

# Capture images of the Charuco board
img_paths = ['image1.png', 'image2.png', 'image3.png', ...]  # list of image paths
objpoints = []  # list of object points
imgpoints = []  # list of image points
for img_path in img_paths:
    # Load the image
    img = cv2.imread(img_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect the markers of the Charuco board in the image
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250))
    charuco_corners, charuco_ids, _ = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, board)

    # Collect the object points and image points
    if len(charuco_corners) > 0:
        objpoints.append(board.objPoints)
        imgpoints.append(charuco_corners)

# Calibrate the camera
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save the camera matrix and distortion coefficients to a file
np.savetxt('camera_matrix.txt', mtx)
np.savetxt('distortion_coefficients.txt', dist)
