import math

def calculate_fov(object_width, distance):
    # Calculate the FOV angle in radians
    fov_rad = 2 * math.atan((object_width / 2) / distance)
    return fov_rad

def radians_to_degrees(radians):
    # Convert radians to degrees
    return radians * 180 / math.pi

def main():
    print("Camera FOV Measurement Tool")
    print("============================")
    
    # Input object dimensions and distances
    object_width = float(input("Enter the width of the object (in meters): "))
    distance = float(input("Enter the distance from the camera to the object (in meters): "))

    # Calculate the FOV angles
    horizontal_fov_rad = calculate_fov(object_width, distance)
    vertical_fov_rad = 2 * math.atan((object_width / 2) / distance)

    # Convert FOV angles to degrees
    horizontal_fov_deg = radians_to_degrees(horizontal_fov_rad)
    vertical_fov_deg = radians_to_degrees(vertical_fov_rad)

    # Print the results
    print("\nCamera FOV Measurement Results")
    print("===============================")
    print(f"Horizontal FOV Angle: {horizontal_fov_deg} degrees")
    print(f"Vertical FOV Angle: {vertical_fov_deg} degrees")

if __name__ == "__main__":
    main()
