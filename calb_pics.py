import cv2
import os

def get_next_attempt_folder(base_directory="Calibration\\Pics"):
    attempt_number = 1
    while True:
        attempt_folder = os.path.join(base_directory, f"attempt_{attempt_number}")
        if not os.path.exists(attempt_folder):
            os.makedirs(attempt_folder)
            return attempt_folder
        attempt_number += 1

def capture_images(num_images_per_press=5, resolution=(1280, 720), downsample_resolution=(640, 480)):
    base_directory = get_next_attempt_folder()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Couldn't open the webcam.")
        return

    # Set the camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    folder_index = 0
    count = 0

    print(f"Press 'c' to capture a set of images. Number of images per press: {num_images_per_press}.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        cv2.imshow('Camera Feed', frame)

        key = cv2.waitKey(1)
        if key == ord('c'):
            current_folder = os.path.join(base_directory, f"set_{folder_index}")
            if not os.path.exists(current_folder):
                os.makedirs(current_folder)
            count = 0
            while count < num_images_per_press:
                ret, frame = cap.read()
                if not ret:
                    break
                # Downsample the image if necessary
                if resolution != downsample_resolution:
                    frame = cv2.resize(frame, downsample_resolution)
                filename = os.path.join(current_folder, f"image_{count:02}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Saved {filename}")
                count += 1
                folder_index += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_images()