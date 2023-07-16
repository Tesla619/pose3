import numpy as np
import cv2
import os
import cv2.aruco as aruco

def generate_aruco_marker(marker_id, markerSize, marker_size_cm, resolution_ppcm, image_path):
    # Calculate the marker size in pixels at the specified resolution
    marker_size_pixels_res = int(marker_size_cm * resolution_ppcm)

    # Create a dictionary with the desired ArUco marker parameters    
    key = getattr(cv2.aruco,f'DICT_{markerSize}X{markerSize}_1000')    
    aruco_dict = aruco.getPredefinedDictionary(key)   

    # Create an image with the ArUco marker
    marker_image = aruco.drawMarker(aruco_dict, marker_id, marker_size_pixels_res)

    # Save the marker image to a file
    cv2.imwrite(image_path, marker_image)


def generate_white_box(box_size_cm, resolution_ppcm, output_path):
    # Calculate the box size in pixels
    box_size_pixels = int(box_size_cm * resolution_ppcm)

    # Create a white box image
    box_image = np.ones((box_size_pixels, box_size_pixels), dtype=np.uint8) * 255

    # Save the white box image to a file
    cv2.imwrite(output_path, box_image)
    print("White box generation complete!")

# White box generation settings
box_size_cm = 5.4 
white_res_ppcm = 37.84  
output_path = "Markers/white_box.png"

# Marker generation settings
markerSizeStart = 6
markerSizeEnd = 6
num_markers = 20
marker_size_cm = 5
marker_res_ppcm = 37.8

# Generate white box
generate_white_box(box_size_cm, white_res_ppcm, output_path)

# Generate markers
os.makedirs("Markers/Generated_Markers", exist_ok=True)

for i in range(markerSizeEnd+1):
    if i >= markerSizeStart:
        for j in range(num_markers):
            marker_id = j
            marker_path = f"Markers/Generated_Markers/{i}x{i}_marker_{j}.png"
            generate_aruco_marker(marker_id, i, marker_size_cm, marker_res_ppcm, marker_path)
            print(f"Generated {i}x{i}_marker_{j}")

# Generate box markers
os.makedirs("Markers/Generated_Box_Markers", exist_ok=True)

for i in range(markerSizeEnd+1):
    if i >= markerSizeStart:
        for j in range(num_markers):
            # Load the images
            background = cv2.imread("Markers/white_box.png")
            marker_path = f"Markers/Generated_Markers/{i}x{i}_marker_{j}.png"
            overlay = cv2.imread(marker_path)

            # Extract the dimensions of the image
            height_b, width_b, channels_b = background.shape
            height_o, width_o, channels_o = overlay.shape

            # ROI Algorithm
            y , x = tuple((background.shape[i] - overlay.shape[i]) // 2 for i in range(2))
            h , w = overlay.shape[:2]

            # Create a mask
            mask = np.zeros(background.shape[:2], dtype=np.uint8)
            mask[y:y+h, x:x+w] = 255

            # Loop over each pixel in the background image and update based on the mask
            for k in range(background.shape[0]):
                for v in range(background.shape[1]):
                    if mask[k, v] != 0:
                        background[k, v] = overlay[k-y, v-x]
            
            # Save the modified image
            box_marker_path = f"Markers/Generated_Box_Markers/{i}x{i}_marker_{j}.png"
            cv2.imwrite(box_marker_path, background)
            print(f"Generated {i}x{i}_box_marker_{j}")