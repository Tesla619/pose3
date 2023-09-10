import os
import shutil

def extract_first_image_from_subfolders(base_path="Calibration\\Pics\\Final"):
    total_images = 0
    sub_folders = [f.path for f in os.scandir(base_path) if f.is_dir()]

    # Count total images across all sub-folders
    for folder in sub_folders:
        for filename in os.listdir(folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                total_images += 1

    avg_images_per_folder = total_images / len(sub_folders)

    print(f"Total Images: {total_images}")
    print(f"Total Folders: {len(sub_folders)}")
    print(f"Average images per folder: {avg_images_per_folder}")

    image_count = 0
    for folder in sub_folders:
        for filename in sorted(os.listdir(folder)):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                # Take the first image
                img_path = os.path.join(folder, filename)
                new_name = os.path.join(base_path, f"image{image_count:02}.jpg")  # Modified here
                shutil.move(img_path, new_name)
                image_count += 1
                break
        
        # Delete the sub-folder after extracting the first image
        shutil.rmtree(folder)

    print(f"Processed {image_count} images.")

if __name__ == "__main__":
    extract_first_image_from_subfolders()
