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
    box_size_pixels = int(box_size_cm * resolution_ppcm)
    box_image = np.ones((box_size_pixels, box_size_pixels), dtype=np.uint8) * 255
    box_image[0:border_thickness, :] = 0
    box_image[-border_thickness:, :] = 0
    box_image[:, 0:border_thickness] = 0
    box_image[:, -border_thickness:] = 0
    cv2.imwrite(output_path, box_image)

def generate_A4_sheet_with_markers(box_marker_paths, start_idx, A4_width_cm, A4_height_cm, box_size_cm, resolution_ppcm, output_path, current_page, total_pages):
    A4_width_pixels = int(A4_width_cm * resolution_ppcm)
    A4_height_pixels = int(A4_height_cm * resolution_ppcm)
    A4_image = np.ones((A4_height_pixels, A4_width_pixels), dtype=np.uint8) * 255

    box_marker_pixel_size = int(box_size_cm * resolution_ppcm)
    
    num_markers_horizontal = int(A4_width_cm // (box_size_cm + margin_cm))
    num_markers_vertical = int(A4_height_cm // (box_size_cm + margin_cm))
    total_width_required = num_markers_horizontal * (box_size_cm + margin_cm) - margin_cm
    total_height_required = num_markers_vertical * (box_size_cm + margin_cm) - margin_cm
    
    start_x = (A4_width_cm - total_width_required) / 2 * resolution_ppcm
    start_y = (A4_height_cm - total_height_required) / 2 * resolution_ppcm

    y_coord = start_y
    current_idx = start_idx
    for _ in range(num_markers_vertical):
        x_coord = start_x
        for _ in range(num_markers_horizontal):
            if current_idx >= len(box_marker_paths):
                break
            box_marker_path = box_marker_paths[current_idx]
            box_marker_img = cv2.imread(box_marker_path, cv2.IMREAD_GRAYSCALE)
            A4_image[int(y_coord):int(y_coord+box_marker_pixel_size), int(x_coord):int(x_coord+box_marker_pixel_size)] = box_marker_img
            x_coord += (box_size_cm + margin_cm) * resolution_ppcm
            current_idx += 1
        y_coord += (box_size_cm + margin_cm) * resolution_ppcm


    # Calculate the end_idx
    end_idx = start_idx + num_markers_horizontal * num_markers_vertical - 1
    if end_idx >= len(box_marker_paths):
        end_idx = len(box_marker_paths) - 1

    
    # Extracting IDs from the filename
    start_id = box_marker_paths[start_idx].split('_id')[1].split('_')[0]
    end_id = box_marker_paths[end_idx].split('_id')[1].split('_')[0]

    # Constructing the marker name for the text overlay
    marker_name = f"{markerSizeStart}x{markerSizeStart}_id{start_id}_-_{end_id}"   
    
    # Adjusting the font size and thickness
    fontScale = 0.75  # adjust this value was 0.5
    thickness = 3    # adjust this value was 2
    
    # Superimposing the name of the markers
    cv2.putText(A4_image, marker_name, (30, A4_height_pixels - 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0, 0, 0), thickness, cv2.LINE_AA)
    
    # Superimposing the page number
    page_number = f"Page {current_page}/{total_pages}"
    cv2.putText(A4_image, page_number, (A4_width_pixels - 200, A4_height_pixels - 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0,0,0), thickness, cv2.LINE_AA)
    
    # Saving the A4 sheet with markers
    cv2.imwrite(output_path, A4_image)


try:
    marker_size_cm = float(input("Enter the marker size in cm: "))
except ValueError:
    print("Invalid input! Please enter a valid number.")
    exit()

box_size_cm = marker_size_cm + 0.4
margin_cm = 1
A4_width_cm, A4_height_cm = 21 - 2, 29.7 - 2

num_markers_horizontal = int(A4_width_cm // (marker_size_cm + margin_cm))
num_markers_vertical = int(A4_height_cm // (marker_size_cm + margin_cm))

if num_markers_horizontal < 1 or num_markers_vertical < 1:
    print("The markers are too large for the A4 size.")
    exit()

resolution_ppcm = 37.8
base_path = os.path.join("Markers", f"{marker_size_cm}cm")
output_path = os.path.join(base_path, "white_box.png")
markerSizeStart, markerSizeEnd = 6, 6
num_markers = 20

os.makedirs(os.path.join(base_path, "Generated_Markers"), exist_ok=True)
os.makedirs(os.path.join(base_path, "Generated_Box_Markers"), exist_ok=True)
generate_white_box(box_size_cm, resolution_ppcm, output_path)

for i in range(markerSizeStart, markerSizeEnd+1):
    for j in range(num_markers):
        marker_path = os.path.join(base_path, "Generated_Markers", f"{i}x{i}_marker_id{j}_{marker_size_cm}cm.png")
        generate_aruco_marker(j, i, marker_size_cm, resolution_ppcm, marker_path)

for i in range(markerSizeStart, markerSizeEnd+1):
    for j in range(num_markers):
        background = cv2.imread(output_path)
        marker_path = os.path.join(base_path, "Generated_Markers", f"{i}x{i}_marker_id{j}_{marker_size_cm}cm.png")
        overlay = cv2.imread(marker_path)
        y, x = tuple((background.shape[d] - overlay.shape[d]) // 2 for d in range(2))
        h, w = overlay.shape[:2]
        background[y:y+h, x:x+w] = overlay
        box_marker_path = os.path.join(base_path, "Generated_Box_Markers", f"{i}x{i}_marker_id{j}_{marker_size_cm}cm.png")
        cv2.imwrite(box_marker_path, background)

sheet_folder = os.path.join(base_path, f"{marker_size_cm}cm sheets")
os.makedirs(sheet_folder, exist_ok=True)

box_marker_paths = [os.path.join(base_path, "Generated_Box_Markers", f"{i}x{i}_marker_id{j}_{marker_size_cm}cm.png") 
                    for i in range(markerSizeStart, markerSizeEnd+1) for j in range(num_markers)]

total_pages = (len(box_marker_paths) + num_markers_horizontal * num_markers_vertical - 1) // (num_markers_horizontal * num_markers_vertical)
sheet_count = len(box_marker_paths) // (num_markers_horizontal * num_markers_vertical)
remainder = len(box_marker_paths) % (num_markers_horizontal * num_markers_vertical)
if remainder:
    sheet_count += 1

for i in range(sheet_count):
    current_page = i + 1
    sheet_path = os.path.join(sheet_folder, f"sheet_{current_page}.png")
    start_idx = i * num_markers_horizontal * num_markers_vertical    
    generate_A4_sheet_with_markers(box_marker_paths, start_idx, A4_width_cm, A4_height_cm, box_size_cm, resolution_ppcm, sheet_path, current_page, total_pages)    

print("All tasks complete!")