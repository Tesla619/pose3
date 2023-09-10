import cv2

# Define Charuco board parameters
DPI = 2000
SQUARES_X = 5
SQUARES_Y = 7
SQUARE_LENGTH = 160  # size of the chessboard squares in millimeters
MARKER_LENGTH = 120  # size of the ArUco markers in millimeters
DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)

# Generate Charuco board
board = cv2.aruco.CharucoBoard_create(
    SQUARES_X, SQUARES_Y, SQUARE_LENGTH, MARKER_LENGTH, DICTIONARY)

# Draw the board
A1_WIDTH = 594  # in millimeters for A1 size paper
A1_HEIGHT = 841  # in millimeters for A1 size paper
IMAGE_WIDTH = int(A1_WIDTH * (DPI / 25.4))  # convert to pixels using a typical DPI of 1000
IMAGE_HEIGHT = int(A1_HEIGHT * (DPI / 25.4))
image = board.draw((IMAGE_WIDTH, IMAGE_HEIGHT))

# Save the generated Charuco board to a file
cv2.imwrite("To Print\\A1\\A1_charuco_board.png", image)

print("Charuco board saved as charuco_board_A1.png")