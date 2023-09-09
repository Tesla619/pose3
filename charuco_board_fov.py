import cv2
import cv2.aruco as aruco
import math

# A1 paper dimensions in meters
paper_width = 0.841
paper_height = 0.594

# Margin for printing in meters
margin = 0.02  # 2 cm

# DPI scaling for printer
dpi = 1000

# Given FOV angle in degrees and distance in meters
fov_degrees = 77
distance_to_object = 1  # 1 meter

# Calculate the horizontal and vertical FOV angles in radians
fov_radians = math.radians(fov_degrees)
horizontal_fov_radians = 2 * math.atan(math.tan(fov_radians / 2) * (16 / 9))  # Assuming 16:9 aspect ratio
vertical_fov_radians = 2 * math.atan(math.tan(fov_radians / 2))

# Calculate the width and height of the observable area at the given distance
observable_width = 2 * distance_to_object * math.tan(horizontal_fov_radians / 2)
observable_height = 2 * distance_to_object * math.tan(vertical_fov_radians / 2)

print(f"Observable width at {distance_to_object}m: {observable_width:.2f} meters")
print(f"Observable height at {distance_to_object}m: {observable_height:.2f} meters")

# Adjust the paper dimensions to account for the margin
adjusted_paper_width = paper_width - 2 * margin
adjusted_paper_height = paper_height - 2 * margin

# Fixed square size in meters
fixed_square_size = 0.10
print(f"Fixed square size: {fixed_square_size:.2f} meters")

# Calculate the number of squares in each direction based on the fixed square size
squaresX = int(adjusted_paper_width / fixed_square_size)
squaresY = int(adjusted_paper_height / fixed_square_size)

# Use the same ArUco dictionary as your markers
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)

# Create a Charuco board
board = aruco.CharucoBoard_create(squaresX, squaresY, fixed_square_size, fixed_square_size * 0.8, dictionary)

# Define the image size (in pixels)
image_size = (int(paper_width * dpi), int(paper_height * dpi))

# Generate the Charuco board image
board_image = board.draw(image_size)

# Save the board image to a file
cv2.imwrite('To Print\\A1\\charuco_board_fov.png', board_image)

# Display the board (optional)
cv2.imshow('Charuco Board FOV', board_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
