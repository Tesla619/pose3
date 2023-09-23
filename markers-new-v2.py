import os
import cv2
import time
import math
import numpy as np
import cv2.aruco as aruco

def get_valid_integer_input(prompt, min_value=None, max_value=None):
    while True:
        try:
            user_input = int(input(prompt))
            if (min_value is None or user_input >= min_value) and (max_value is None or user_input <= max_value):
                return user_input
            else:
                print(f"Input must be between {min_value} and {max_value} (inclusive).")
        except ValueError:
            print("Invalid input! Please enter a valid integer.")

def get_valid_float_input(prompt, min_value=None, max_value=None):
    while True:
        try:
            user_input = float(input(prompt))
            if (min_value is None or user_input >= min_value) and (max_value is None or user_input <= max_value):
                return user_input
            else:
                print(f"Input must be between {min_value} and {max_value} (inclusive).")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

def get_valid_bool_input(prompt):
    while True:
        user_input = input(prompt)
        if user_input.lower() == "yes" or user_input.lower() == "1":
            return True
        elif user_input.lower() == "no" or user_input.lower() == "0":
            return False
        else:
            print("Invalid input! Please enter 'Yes' or 'No' (or '1' or '0').")

def select_paper_size(paper_size, paper_margin_cm=1):
    dimensions = {
        0: (84.1 - paper_margin_cm, 118.9 - paper_margin_cm),
        1: (59.4 - paper_margin_cm, 84.1 - paper_margin_cm),
        2: (42.0 - paper_margin_cm, 59.4 - paper_margin_cm),
        3: (29.7 - paper_margin_cm, 42.0 - paper_margin_cm),
        4: (21.0 - paper_margin_cm, 29.7 - paper_margin_cm)
    }

    return dimensions.get(paper_size, (None, None))

def user_inputs():
    while True:  
        try:
            paper_size = get_valid_integer_input("Enter the paper size (A0 (0) to A4 (4)): ", min_value = 0, max_value = 4)
        except ValueError:
            print("Invalid input! Please enter a valid paper size between 0 and 4.")
            
        try:
            marker_dic = get_valid_integer_input("Enter marker dictionary (4-7): ", min_value = 4, max_value = 7)
        except ValueError:
            print("Invalid input! Please enter a valid marker size between 4 and 7.")     
            
        try:
            marker_size_cm = get_valid_float_input("Enter the marker physical size in cm: ")
        except ValueError:
            print("Invalid input! Please enter a valid marker size in cm.")     
        
        #-------In progress-------        
        # try:
        #     num_inputs = get_valid_integer_input("Enter the number of marker physical sizes in cm to generate: ", min_value = 1)
        # except ValueError:
        #     print("Invalid input! Please enter a valid paper size between 0 and 4.")        
        
        # physical_sizes_list = []
        # for i in range(num_inputs):
        #     try:
        #         user_input = get_valid_float_input(f"Enter the marker physical size in cm for input {i + 1}: ")
        #         physical_sizes_list.append(user_input)
        #     except ValueError:
        #         print("Invalid input! Please enter a valid number.")
        #         #make exit maybe
        #-------In progress-------
        
        print("\nSelect an ID range type:")
        print("1. Single Range (single value)")
        print("2. Custom Range (start to end)")
        print("3. Custom Range (inputed by user)")
        print("4. Multiple Ranges (multiple start and end)")        
        
        choice = input("Enter your choice (1/2/3/4): ")
        
        if choice == '1':
            try:
                value = get_valid_integer_input("\nEnter a single value: ")
                return paper_size, marker_dic, marker_size_cm, choice, value + 1
            except ValueError:
                print("\nInvalid input! Please enter a valid integer.")
        elif choice == '2':
            try:
                start = get_valid_integer_input("\nEnter the start of the range: ")
                end = get_valid_integer_input("Enter the end of the range: ")
                if start <= end:
                    return paper_size, marker_dic, marker_size_cm, choice, list(range(start, end + 1))
                else:
                    print("\nInvalid range! Start should be less than or equal to end.")
            except ValueError:
                print("\nInvalid input! Please enter valid integers for start and end.")
        elif choice == '3':
            #-------In progress-------
            return paper_size, marker_dic, marker_size_cm, choice, list(range(start, end + 1))
        elif choice == '4':
            try:
                num_ranges = get_valid_integer_input("\nEnter the number of ranges: ")
                ranges = []
                for i in range(num_ranges):
                    start = get_valid_integer_input(f"\nEnter the start of range {i + 1}: ")
                    end = get_valid_integer_input(f"Enter the end of range {i + 1}: ")
                    if start <= end:
                        ranges.append(list(range(start, end + 1)))
                    else:
                        print(f"\nInvalid range for range {i + 1}! Start should be less than or equal to end.")
                return paper_size, marker_dic, marker_size_cm, choice, ranges
            except ValueError:
                print("\nInvalid input! Please enter valid integers for ranges.")
        else:
            print("\nInvalid choice! Please select 1, 2, 3 or 4.")

def generate_aruco_marker(marker_id, marker_dic, marker_size_cm, resolution_ppcm, image_path):
    marker_size_pixels_res = int(marker_size_cm * resolution_ppcm)
    key = getattr(cv2.aruco, f'DICT_{marker_dic}X{marker_dic}_1000')    
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

def generate_sheet_with_markers(printBool, box_marker_paths, start_idx, paper_width_cm, paper_height_cm, box_size_cm, resolution_ppcm, output_path, current_page, total_pages, margin_cm, marker_dic):
    
    fontScale, thickness = 0.35, 1    
    width_pixels = int(paper_width_cm * resolution_ppcm)
    height_pixels = int(paper_height_cm * resolution_ppcm)
    
    if printBool:
        print("\n")
        print(f"width_pixels: {width_pixels}")
        print(f"height_pixels: {height_pixels}")

    sheet_image = np.ones((height_pixels, width_pixels), dtype=np.uint8) * 255

    box_marker_pixel_size = int(box_size_cm * resolution_ppcm)
    if printBool: print(f"box_marker_pixel_size: {box_marker_pixel_size}")
    
    num_markers_horizontal = int(paper_width_cm // (box_size_cm + margin_cm))
    num_markers_vertical = int(paper_height_cm // (box_size_cm + margin_cm))
    
    if printBool: 
        print(f"num_markers_horizontal: {num_markers_horizontal}")
        print(f"num_markers_vertical: {num_markers_vertical}")
    
    total_width_required = num_markers_horizontal * (box_size_cm + margin_cm) - margin_cm
    total_height_required = num_markers_vertical * (box_size_cm + margin_cm) - margin_cm
    
    if printBool: 
        print(f"total_width_required: {total_width_required}")
        print(f"total_height_required: {total_height_required}")
    
    start_x = (paper_width_cm - total_width_required) / 2 * resolution_ppcm
    start_y = (paper_height_cm - total_height_required) / 2 * resolution_ppcm
    
    if printBool: 
        print(f"start_x: {start_x}")
        print(f"start_y: {start_y}")

    y_coord = start_y
    current_idx = start_idx
    
    for _ in range(num_markers_vertical):
        x_coord = start_x
        for _ in range(num_markers_horizontal):
            if current_idx >= len(box_marker_paths):
                break
            box_marker_path = box_marker_paths[current_idx]
            box_marker_img = cv2.imread(box_marker_path, cv2.IMREAD_GRAYSCALE)
            sheet_image[int(y_coord):int(y_coord+box_marker_pixel_size), int(x_coord):int(x_coord+box_marker_pixel_size)] = box_marker_img
            x_coord += (box_size_cm + margin_cm) * resolution_ppcm
            current_idx += 1
        y_coord += (box_size_cm + margin_cm) * resolution_ppcm

    end_idx = start_idx + num_markers_horizontal * num_markers_vertical - 1
    if end_idx >= len(box_marker_paths):
        end_idx = len(box_marker_paths) - 1
    if printBool: print(f"end_idx: {end_idx}")

    start_id = box_marker_paths[start_idx].split('_id')[1].split('_')[0]
    end_id = box_marker_paths[end_idx].split('_id')[1].split('_')[0]    
    
    if printBool: 
        print(f"start_id: {start_id}")
        print(f"end_id: {end_id}")
    
    marker_dic_name = f"{marker_dic}x{marker_dic}"  
    cv2.putText(sheet_image, marker_dic_name, (width_pixels - 40, height_pixels - 110), cv2.FONT_HERSHEY_SIMPLEX, fontScale * 1.5, (0, 0, 0), thickness, cv2.LINE_AA)
    
    size_cm = f"{box_size_cm-0.4}"
    cv2.putText(sheet_image, size_cm, (width_pixels - 40, height_pixels - 85), cv2.FONT_HERSHEY_SIMPLEX, fontScale * 1.5, (0,0,0), thickness, cv2.LINE_AA)
    
    marker_id_range = f"{start_id}-{end_id}"
    cv2.putText(sheet_image, marker_id_range, (width_pixels - 40, height_pixels - 60), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0, 0, 0), thickness, cv2.LINE_AA)
    
    page_number = f"{current_page}/{total_pages}"
    cv2.putText(sheet_image, page_number, (width_pixels - 40, height_pixels - 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale * 1.5, (0,0,0), thickness, cv2.LINE_AA)
    
    cv2.imwrite(output_path, sheet_image)

    if printBool: print(f"Saved sheet with markers to: {output_path}")

def all_generate(marker_dic, marker_size_cm, paper_width_cm, paper_height_cm, resolution_ppcm, margin_cm, marker_num, debug = 0):  # marker_num still in progress
    
    box_size_cm = marker_size_cm + 0.4    
    num_markers_horizontal = int(paper_width_cm // (box_size_cm + margin_cm))
    num_markers_vertical = int(paper_height_cm // (box_size_cm + margin_cm))

    if num_markers_horizontal < 1 or num_markers_vertical < 1:
        print("The markers are too large for the selected size.")
        exit()

    base_path = os.path.join("Markers", f"{marker_size_cm}cm")
    output_path = os.path.join(base_path, "white_box.png")    
    # marker_num = 16 + 1

    os.makedirs(os.path.join(base_path, "Generated_Markers"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "Generated_Box_Markers"), exist_ok=True)
    generate_white_box(box_size_cm, resolution_ppcm, output_path)
    
    for i in range(marker_num):
    #for i in range(len(marker_num)):
        marker_path = os.path.join(base_path, "Generated_Markers", f"{marker_dic}x{marker_dic}_marker_id{i}_{marker_size_cm}cm.png")
        generate_aruco_marker(i, marker_dic, marker_size_cm, resolution_ppcm, marker_path)

    for i in range(marker_num):
        background = cv2.imread(output_path)
        marker_path = os.path.join(base_path, "Generated_Markers", f"{marker_dic}x{marker_dic}_marker_id{i}_{marker_size_cm}cm.png")
        overlay = cv2.imread(marker_path)
        y, x = tuple((background.shape[d] - overlay.shape[d]) // 2 for d in range(2))
        h, w = overlay.shape[:2]
        background[y:y+h, x:x+w] = overlay
        box_marker_path = os.path.join(base_path, "Generated_Box_Markers", f"{marker_dic}x{marker_dic}_marker_id{i}_{marker_size_cm}cm.png")
        cv2.imwrite(box_marker_path, background)

    sheet_folder = os.path.join(base_path, f"{marker_size_cm}cm sheets")
    os.makedirs(sheet_folder, exist_ok=True)

    box_marker_paths = [os.path.join(base_path, "Generated_Box_Markers", f"{marker_dic}x{marker_dic}_marker_id{i}_{marker_size_cm}cm.png") 
                        for i in range(marker_num)]

    # Calculate the number of markers on a single sheet
    markers_per_sheet = num_markers_horizontal * num_markers_vertical

    # Calculate the total number of sheets required
    sheet_count = math.ceil(len(box_marker_paths) / markers_per_sheet)

    if debug:
        print("\n")
        print(f"len(box_marker_paths): {len(box_marker_paths)}\n")
        print(f"num_markers_horizontal: {num_markers_horizontal}\n")
        print(f"num_markers_vertical: {num_markers_vertical}\n")
        print(f"markers_per_sheet: {markers_per_sheet}\n")
        print(f"sheet_count: {sheet_count}\n")

    for i in range(sheet_count):
        current_page = i + 1
        sheet_path = os.path.join(sheet_folder, f"{marker_size_cm}cm_sheet_{current_page}.png")
        start_idx = i * markers_per_sheet
        generate_sheet_with_markers(debug, box_marker_paths, start_idx, paper_width_cm, paper_height_cm, box_size_cm, resolution_ppcm, sheet_path, current_page, sheet_count, margin_cm, marker_dic)
        
    # Add delete for extra files and folders

paper_size, marker_dic, marker_size_cm, selected_choice, selected_range = user_inputs()
margin_cm = 0.75
paper_margin_cm = 1
resolution_ppcm = 37.8
selected_width, selected_height = select_paper_size(paper_size, paper_margin_cm)

#---------------------------------------------
# try:
#     debug = get_valid_bool_input("Debug Print Yes or No (Yes = 1 or No = 0): ")
# except ValueError:
#     print("Invalid input! Please enter 'Yes' or 'No' (or '1' or '0').")
#---------------------------------------------

#if debug: print(paper_size, marker_dic, marker_size_cm, selected_choice, selected_range)

print(selected_range)

if selected_choice == '1':
    all_generate(marker_dic, marker_size_cm, selected_width, selected_height, resolution_ppcm, margin_cm, selected_range)   
    
elif selected_choice == '2':
    print("This is case 2")
    
elif selected_choice == '3':
    print("This is case 3")
    
elif selected_choice == '4':
    print("This is case 4")
   
print("\nAll tasks complete!\n")