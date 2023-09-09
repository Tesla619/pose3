import cv2
import cv2.aruco as aruco

# Define the Charuco board configuration
squaresX = 6  # Number of squares in the X direction
squaresY = 8  # Number of squares in the Y direction
square_size = 0.075  # Size of each square in meters (adjust as needed)

# Use the same ArUco dictionary as your markers
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)

# Create a Charuco board
board = aruco.CharucoBoard_create(squaresX, squaresY, square_size, square_size * 0.8, dictionary)

# Define the image size (in pixels)
image_size = (640, 480)  # Adjust as needed for your camera's resolution

# Generate the Charuco board image
board_image = board.draw(image_size)

# Save the board image to a file
cv2.imwrite('charuco_board.png', board_image)

# Display the board (optional)
cv2.imshow('Charuco Board', board_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
