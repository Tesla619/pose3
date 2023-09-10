import cv2
import numpy as np

# ChArUco board parameters
# board, board_length, marker_size = cv2.aruco.CharucoBoard_create(2, 4, 0.10, 0.08 * 1.0, dictionary), 0.10 * 4, 0.08 * 1.0   # physical
# board, board_length, marker_size = cv2.aruco.CharucoBoard_create(2, 4, 0.09, 0.09 * 0.8, dictionary), 0.09 * 4, 0.09 * 0.8   # generated A3
# board, board_length, marker_size = cv2.aruco.CharucoBoard_create(5, 7, 0.04, 0.02 * 1.0, dictionary), 0.04 * 7, 0.02 * 1.0   # documentation generated
# board, board_length, marker_size = cv2.aruco.CharucoBoard_create(5, 8, 0.10, 0.10 * 0.8, dictionary), 0.10 * 8, 0.10 * 0.8   # generated A1

def select_board_config(board_type, dictionary):
    configs = {
        '1': (cv2.aruco.CharucoBoard_create(2, 4, 0.10, 0.080, dictionary), 0.40, 0.080), # physical
        '2': (cv2.aruco.CharucoBoard_create(2, 4, 0.09, 0.072, dictionary), 0.36, 0.072), # generated A3
        '3': (cv2.aruco.CharucoBoard_create(5, 7, 0.04, 0.020, dictionary), 0.28, 0.020), # documentation generated
        '4': (cv2.aruco.CharucoBoard_create(8, 5, 0.10, 0.080, dictionary), 0.80, 0.080)  # generated A1
    }
    
    return configs.get(board_type, (None, None, None))

# ArUco dictionary and parameters
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
parameters = cv2.aruco.DetectorParameters_create()
board, board_length, marker_size = select_board_config('4', dictionary)                             # CHANGE SET HERE @@@@@@@@@@@@@@@@@@@

# generate_charuco_board(0.841, 0.594, 0.10, dpi, 0.02, 'To Print\\A1', 'A1_charuco_board.png')


# Load the image
image_path = 'Calibration\\Pics\\Test\\8.png'                                                       # CHANGE PIC HERE @@@@@@@@@@@@@@@@@@@
image = cv2.imread(image_path)

# Load camera matrix and distortion coefficients
camera_matrix = np.array(
    [
        [6.73172250e02, 0.00000000e00, 3.21652381e02],
        [0.00000000e00, 6.73172250e02, 2.40854103e02],
        [0.00000000e00, 0.00000000e00, 1.00000000e00],
    ]
)
distortion_coefficients = np.array(
    [-2.87888863e-01, 9.67075352e-02, 1.65928771e-03, -5.19671229e-04, -1.30327183e-02]
)

# Convert image to grayscale for ArUco detection
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect the markers in the image
corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

# If markers are detected, estimate their pose
if ids is not None and len(ids) > 0:
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, camera_matrix, distortion_coefficients)

    # Draw the axes of the markers
    for i in range(len(ids)):
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        cv2.aruco.drawAxis(image, camera_matrix, distortion_coefficients, rvecs[i], tvecs[i], marker_size)

# Detect the ChArUco board
ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, board)

if ret > 0:
    # The variable 'charuco_ids' contains the IDs of detected ChArUco markers
    num_detected_charuco_markers = len(charuco_ids)
    print(f"Number of detected ChArUco markers: {num_detected_charuco_markers}")

    # You can also print the IDs of detected ChArUco markers
    print(f"Detected ChArUco marker IDs: {charuco_ids}")
    
    cv2.aruco.drawDetectedCornersCharuco(image, charuco_corners, charuco_ids)

    # Check if enough corners are detected for pose estimation
    if len(charuco_corners) >= 0: #was 4
        # Define empty variables for rotation and translation vectors
        charuco_rvec, charuco_tvec = np.zeros((3, 1)), np.zeros((3, 1))
        #charuco_rvec, charuco_tvec = np.zeros((1, 3)), np.zeros((1, 3))
        #charuco_rvec, charuco_tvec = np.empty((3, 1)), np.empty((3, 1))
        #charuco_rvec, charuco_tvec = np.empty((1, 3)), np.empty((1, 3))
        #charuco_rvec, charuco_tvec = None, None
    
        # Call the function to estimate the pose
        retval, charuco_rvec, charuco_tvec = cv2.aruco.estimatePoseCharucoBoard(charuco_corners, charuco_ids, board, camera_matrix, distortion_coefficients, charuco_rvec, charuco_tvec)

        # Check if the pose estimation was successful
        print(retval)
        
        # Draw the axes for the ChArUco board
        # cv2.drawFrameAxes(image, camera_matrix, distortion_coefficients, charuco_rvec, charuco_tvec, board_length)
    else:
        print(f"Not enough corners detected.")                    

# Display the resulting image
cv2.imshow('ChArUco Board Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()


# #Convert Rodriguez Rotation Vector to Quaternion
# def rvec2Quartenion(rvec):
#     theta = cv2.norm(rvec)
#     return (
#         rvec[0]/theta*np.sin(theta/2), 
#         rvec[1]/theta*np.sin(theta/2), 
#         rvec[2]/theta*np.sin(theta/2), 
#         np.cos(theta/2)
#     )