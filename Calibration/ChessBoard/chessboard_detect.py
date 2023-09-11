import cv2
import numpy as np

# Define the chessboard dimensions
chessboard_size = (7, 7)

# Define the size of each square in millimeters
square_size_mm = 30.0

# Calculate the size of the chessboard in pixels, adding space for the border
chessboard_width_pixels = int((chessboard_size[0] + 2) * square_size_mm)
chessboard_height_pixels = int((chessboard_size[1] + 2) * square_size_mm)

# Create an empty white chessboard
chessboard = np.ones((chessboard_height_pixels, chessboard_width_pixels, 3), dtype=np.uint8) * 255

# Create the chessboard pattern with a border
for i in range(int(square_size_mm), int(chessboard_height_pixels - square_size_mm), int(square_size_mm)):
    for j in range(int(square_size_mm), int(chessboard_width_pixels - square_size_mm), int(square_size_mm)):
        if (i // int(square_size_mm) + j // int(square_size_mm)) % 2 == 1:
            chessboard[i:i + int(square_size_mm), j:j + int(square_size_mm)] = [0, 0, 0]

# Apply a slight blur to the image
chessboard = cv2.GaussianBlur(chessboard, (5, 5), 0)

# Save the generated chessboard image
chessboard_path = 'Calibration/ChessBoard/chessboard.png'
cv2.imwrite(chessboard_path, chessboard)

# Load the generated chessboard image
chessboard_image = cv2.imread(chessboard_path)

# Convert to grayscale
gray = cv2.cvtColor(chessboard_image, cv2.COLOR_BGR2GRAY)

# Find chessboard corners
ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

# If corners are found, draw them on the image
if ret:
    cv2.drawChessboardCorners(chessboard_image, chessboard_size, corners, ret)
    # Save the image with detected corners
    cv2.imwrite(chessboard_path, chessboard_image)
    print(f"Chessboard image saved to {chessboard_path}")
else:
    print("Chessboard corners not found.")

# Display the generated and detected chessboard
cv2.imshow('Generated and Detected Chessboard', chessboard_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
