import os
import cv2
import time
import numpy as np
import cv2.aruco as aruco

def generate_aruco_marker(marker_id, markerSize, marker_size_cm, resolution_ppcm, image_path):
    marker_size_pixels_res = int(marker_size_cm * resolution_ppcm)
    key = getattr(cv2.aruco, f'DICT_{markerSize}X{markerSize}_1000')    
    aruco_dict = aruco.getPredefinedDictionary(key)
    marker_image = aruco.drawMarker(aruco_dict, marker_id, marker_size_pixels_res)
    cv2.imwrite(image_path, marker_image)

def generate_white_box(box_size_cm, resolution_ppcm, output_path, border_thickness=2):
    # Calculate the box size in pixels
    box_size_pixels = int(box_size_cm * resolution_ppcm)

    # Create a white box image
    box_image = np.ones((box_size_pixels, box_size_pixels), dtype=np.uint8) * 255

    # Add a black border
    box_image[0:border_thickness, :] = 0  # Top border
    box_image[-border_thickness:, :] = 0  # Bottom border
    box_image[:, 0:border_thickness] = 0  # Left border
    box_image[:, -border_thickness:] = 0  # Right border

    # Save the white box image with a black border to a file
    cv2.imwrite(output_path, box_image)

    
def generate_A4_sheet_with_markers(box_marker_paths, A4_width_cm, A4_height_cm, box_size_cm, resolution_ppcm, output_path, margin_cm=1):
    A4_width_pixels = int(A4_width_cm * resolution_ppcm)
    A4_height_pixels = int(A4_height_cm * resolution_ppcm)
    A4_image = np.ones((A4_height_pixels, A4_width_pixels), dtype=np.uint8) * 255

    box_marker_pixel_size = int(box_size_cm * resolution_ppcm)
    
    # Calculate the number of markers that can fit horizontally and vertically
    num_markers_horizontal = int(A4_width_cm // (box_size_cm + margin_cm))
    num_markers_vertical = int(A4_height_cm // (box_size_cm + margin_cm))
    
    # Calculate total space required for markers and margins
    total_width_required = num_markers_horizontal * (box_size_cm + margin_cm) - margin_cm  # minus margin_cm to remove the margin after the last marker
    total_height_required = num_markers_vertical * (box_size_cm + margin_cm) - margin_cm
    
    # Calculate starting coordinates to draw markers such that they are centered on the A4 sheet
    start_x = (A4_width_cm - total_width_required) / 2 * resolution_ppcm
    start_y = (A4_height_cm - total_height_required) / 2 * resolution_ppcm

    y_coord = start_y
    for _ in range(num_markers_vertical):
        x_coord = start_x
        for _ in range(num_markers_horizontal):
            if not box_marker_paths:
                break
            box_marker_path = box_marker_paths.pop(0)
            box_marker_img = cv2.imread(box_marker_path, cv2.IMREAD_GRAYSCALE)
            A4_image[int(y_coord):int(y_coord+box_marker_pixel_size), int(x_coord):int(x_coord+box_marker_pixel_size)] = box_marker_img
            x_coord += (box_size_cm + margin_cm) * resolution_ppcm
        y_coord += (box_size_cm + margin_cm) * resolution_ppcm

    cv2.imwrite(output_path, A4_image)


# Get user input for marker_size_cm
try:
    marker_size_cm = float(input("Enter the marker size in cm: "))
except ValueError:
    print("Invalid input! Please enter a valid number.")
    exit()

box_size_cm = marker_size_cm + 0.4

# Check if the markers fit on A4 paper
margin_cm = 1
A4_width_cm, A4_height_cm = 21 - 2, 29.7 - 2
num_markers_horizontal = int(A4_width_cm // (marker_size_cm + margin_cm))
num_markers_vertical = int(A4_height_cm // (marker_size_cm + margin_cm))

if num_markers_horizontal < 1 or num_markers_vertical < 1:
    print("The markers are too large for the A4 size.")
    exit()

# Settings
resolution_ppcm = 37.8
output_path = f"Markers/{marker_size_cm}cm/white_box.png"
markerSizeStart, markerSizeEnd = 6, 6
num_markers = 20

os.makedirs(f"Markers/{marker_size_cm}cm/Generated_Markers", exist_ok=True)
os.makedirs(f"Markers/{marker_size_cm}cm/Generated_Box_Markers", exist_ok=True)
generate_white_box(box_size_cm, resolution_ppcm, output_path)

for i in range(markerSizeStart, markerSizeEnd+1):
    for j in range(num_markers):
        marker_id = j
        marker_path = f"Markers/{marker_size_cm}cm/Generated_Markers/{i}x{i}_marker_id{j}_{marker_size_cm}cm.png"
        generate_aruco_marker(marker_id, i, marker_size_cm, resolution_ppcm, marker_path)

for i in range(markerSizeStart, markerSizeEnd+1):
    for j in range(num_markers):
        background = cv2.imread(f"Markers/{marker_size_cm}cm/white_box.png")
        marker_path = f"Markers/{marker_size_cm}cm/Generated_Markers/{i}x{i}_marker_id{j}_{marker_size_cm}cm.png"
        overlay = cv2.imread(marker_path)

        y, x = tuple((background.shape[d] - overlay.shape[d]) // 2 for d in range(2))
        h, w = overlay.shape[:2]
        background[y:y+h, x:x+w] = overlay
        box_marker_path = f"Markers/{marker_size_cm}cm/Generated_Box_Markers/{i}x{i}_marker_id{j}_{marker_size_cm}cm.png"
        cv2.imwrite(box_marker_path, background)

markers_per_row = int(A4_width_cm // (box_size_cm + 1))
markers_per_col = int(A4_height_cm // (box_size_cm + 1))
sheet_folder = f"Markers/{marker_size_cm}cm/{marker_size_cm}cm sheets"
os.makedirs(sheet_folder, exist_ok=True)

box_marker_paths = [f"Markers/{marker_size_cm}cm/Generated_Box_Markers/{i}x{i}_marker_id{j}_{marker_size_cm}cm.png" 
                    for i in range(markerSizeStart, markerSizeEnd+1) for j in range(num_markers)]

sheet_count = len(box_marker_paths) // (markers_per_row * markers_per_col)
for i in range(sheet_count):
    markers_for_this_sheet = box_marker_paths[i * markers_per_row * markers_per_col : (i+1) * markers_per_row * markers_per_col]
    output_sheet_path = f"Markers/{marker_size_cm}cm/{marker_size_cm}cm sheets/sheet_{i+1}.png"
    generate_A4_sheet_with_markers(markers_for_this_sheet, A4_width_cm, A4_height_cm, box_size_cm, resolution_ppcm, output_sheet_path)

# Handling leftover markers
remaining_markers = len(box_marker_paths) % (markers_per_row * markers_per_col)
if remaining_markers:
    markers_for_last_sheet = box_marker_paths[-remaining_markers:]
    output_sheet_path = f"Markers/{marker_size_cm}cm/{marker_size_cm}cm sheets/sheet_{sheet_count+1}.png"
    generate_A4_sheet_with_markers(markers_for_last_sheet, A4_width_cm, A4_height_cm, box_size_cm, resolution_ppcm, output_sheet_path)

print("All tasks complete!")