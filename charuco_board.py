import os
import cv2
import cv2.aruco as aruco

def generate_charuco_board(paper_width, paper_height, fixed_square_size, dpi, margin, output_path, output_filename):
    # Adjust the paper dimensions to account for the margin
    adjusted_paper_width = paper_width - 2 * margin
    adjusted_paper_height = paper_height - 2 * margin

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
    
    os.makedirs(output_path, exist_ok=True)
    
    # Save the board image to a file
    cv2.imwrite(output_path + '\\' + output_filename, board_image)
    
    print(squaresX)
    print(squaresY)
    
    # Display the board (optional)
    cv2.imshow(f'Charuco Board - {output_filename}', board_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# DPI scaling for printer
dpi = 1000

# A1 paper dimensions in meters, fixed square size, and margin
# generate_charuco_board(0.841, 0.594, 0.10, dpi, 0.02, 'To Print\\A1', 'A1_charuco_board.png')

# For A2
# generate_charuco_board(0.420, 0.594, 0.10, dpi, 0.02, 'To Print\\A2', 'A2_charuco_board.png')

# For A3
generate_charuco_board(0.297, 0.420, 0.09, dpi, 0.02, 'To Print\\A3', 'A3_charuco_board.png')

# For A4
# generate_charuco_board(0.210, 0.297, 0.08, dpi, 0.01, 'To Print\\A4', 'A4_charuco_board.png')