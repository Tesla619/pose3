import cv2

def generate_charuco_board(width_mm, height_mm, filename):
    DPI = 600
    MARGIN = 10  # 1cm margin, converted to mm
    DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
    
    # Calculate usable width and height
    usable_width_mm = width_mm - 2 * MARGIN
    usable_height_mm = height_mm - 2 * MARGIN

    # Determine maximum square length
    SQUARE_LENGTH = min(usable_width_mm / SQUARES_X, usable_height_mm / SQUARES_Y)
    
    # Set marker length to be 75% of the square length
    MARKER_LENGTH = 0.75 * SQUARE_LENGTH

    # Generate Charuco board
    board = cv2.aruco.CharucoBoard_create(
        SQUARES_X, SQUARES_Y, SQUARE_LENGTH, MARKER_LENGTH, DICTIONARY)

    # Draw the board
    IMAGE_WIDTH = int(width_mm * (DPI / 25.4))
    IMAGE_HEIGHT = int(height_mm * (DPI / 25.4))
    image = board.draw((IMAGE_WIDTH, IMAGE_HEIGHT))

    # Save the generated Charuco board to a file
    cv2.imwrite(filename, image)

    print(f"Charuco board saved as {filename}, Width: {IMAGE_WIDTH}, Height: {IMAGE_HEIGHT}, SQ: {SQUARE_LENGTH}, ML: {MARKER_LENGTH}")

SQUARES_X = 5
SQUARES_Y = 7

# Paper sizes in millimeters
PAPER_SIZES = {
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297)
}

for paper, dimensions in PAPER_SIZES.items():
    generate_charuco_board(dimensions[0], dimensions[1], f"To Print\\Fixed\\{paper}\\{paper}_charuco_board_fixed.png")
