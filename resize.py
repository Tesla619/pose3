import cv2
import os

def resize_images(folder_path, target_size):
    
    output_folder = "G:\\My Drive\\customTF2\\image2"
    #output_folder = folder_path    
    target_width, target_height = target_size
    
    os.makedirs(output_folder, exist_ok=True)
    for filename in os.listdir(folder_path):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            try:
                # Open the image file
                image_path = os.path.join(folder_path, filename)
                image = cv2.imread(image_path)

                # Get the original image dimensions
                original_height, original_width = image.shape[:2]

                # Calculate the aspect ratio
                aspect_ratio = original_width / original_height

                # Calculate the new dimensions based on the target width
                new_width = target_width
                new_height = int(new_width / aspect_ratio)

                # Check if the image is portrait or landscape
                if original_height > original_width:
                    # Portrait image, resize based on height instead
                    new_height = target_width
                    new_width = int(new_height * aspect_ratio)

                # Resize the image while maintaining the aspect ratio
                resized_image = cv2.resize(image, (new_width, new_height))

                # Save the resized image
                output_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_path, resized_image)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    print("Image resizing complete.")

# Specify the folder containing the images
folder_path = "G:\\My Drive\\customTF2\\images"
target_size = (1280, None)

# Call the function to resize images
resize_images(folder_path, target_size)
