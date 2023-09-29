############################## ArUco Detection #########################################
            # 
            # gray = cv2.cvtColor(
            #     frame, cv2.COLOR_BGR2GRAY
            # )  # Convert frame to grayscale for ArUco detection
            #
            # # Detect the markers in the frame
            # corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            #     gray, dictionary, parameters=parameters
            # )
            #
            # # If markers are detected, estimate their pose
            # if ids is not None:  # and len(ids) >= 2: 
            #     for desired_id in desired_marker_order:
            #         for i in range(len(ids)):
            #             marker_id = ids[i][0]
            #             marker_size = marker_sizes.get(marker_id, None)
            #
            #             if marker_size is not None and marker_id == desired_id:
            #             #if marker_size is not None:
            #                 rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            #                 [corners[i]], marker_size, camera_matrix, distortion_coefficients
            #             )
            #                 # Draw the axes of the markers
            #                 cv2.aruco.drawDetectedMarkers(frame, [corners[i]], np.array([marker_id]))
            #                 cv2.aruco.drawAxis(
            #                     frame,
            #                     camera_matrix,
            #                     distortion_coefficients,
            #                     rvecs[0], # was rvecs[i]
            #                     tvecs[0], # was tvecs[i]
            #                     marker_size,
            #                 )      
            #               
            #                 # Estimate the current orientation angle
            #                 angle = rvecs[0][0][0] * (180 / np.pi) - 167   
            #                 buffer = angle * angle     
            #                 filtered_angle = math.sqrt(buffer)
            #               
            #                 if (0 <= marker_id <= 3):
            #                     cv2.putText(
            #                         frame,                            
            #                         f"{0}",
            #                         (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
            #                         cv2.FONT_HERSHEY_SIMPLEX,
            #                         1.5,
            #                         (255, 255, 255),
            #                         2,
            #                     )        
            #                 # elif (4 <= marker_id <= 7):
            #                 #     cv2.putText(
            #                 #         frame,                            
            #                 #         f"{int(filtered_angle) + 90}",
            #                 #         (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
            #                 #         cv2.FONT_HERSHEY_SIMPLEX,
            #                 #         1.5,
            #                 #         (255, 255, 255),
            #                 #         2,
            #                 #     )
            #                 elif (12 <= marker_id <= 17):
            #                     cv2.putText(
            #                         frame,                            
            #                         #f"{int(filtered_angle) + 90}",
            #                         "90",
            #                         (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
            #                         cv2.FONT_HERSHEY_SIMPLEX,
            #                         1.5,
            #                         (255, 255, 255),
            #                         2,
            #                     )
            #                 else:                                
            #                     cv2.putText(
            #                         frame,                            
            #                         #f"{round(filtered_angle, 2)}",
            #                         f"{int(filtered_angle)}",
            #                         (int(corners[i][0][0][0]), int(corners[i][0][0][1])),
            #                         cv2.FONT_HERSHEY_SIMPLEX,
            #                         1.5,
            #                         (255, 255, 255),
            #                         2,
            #                     )
            #
            #                 # Interpolate the joint movment on each marker
            #                 # Logic of combination of markers to determine the robot's pose
            #                 # Send the robot's pose to matlab via websocket
            #               
            #                 if fps_count >= 20:                                
            #                     if not (0 <= marker_id <= 3):                                    
            #                       
            #                         # if (4 <= marker_id <= 7):
            #                         #     numbers.append(int(filtered_angle) + 90)
            #                         # else:
            #                         #   numbers.append(int(filtered_angle))                                        
            #                         numbers.append(int(filtered_angle))
            #                         # Increment the counter                                      
            #                         counter += 1     
            #
            #                     # Check if we have added 4 values, then add a fixed 0 and send to MATLAB
            #                         if counter == 2:
            #                             numbers.append(0)
            #                             numbers.append(0)
            #                             send_to_matlab(numbers)  # Assuming you have a function send_to_matlab                                    
            #                             numbers = []  # Reset the list
            #                             counter = 0  # Reset the counter
            #                             numbers.append(int(0))
            #                             fps_count = 0
            #
            #                 # Check if there are remaining values in the list (less than 4)
            #                 # if numbers:
            #                 #     # Add 0 to complete the list
            #                 #     while len(numbers) < 4:
            #                 #         numbers.append(0)
            #                 #     send_to_matlab(numbers)  # Send the remaining values to MATLAB
            #
            #                 # # Just to Generate movment for testing                    
            #                 # result = ",".join(map(str, filtered_angle))
            #                 # send_to_matlab(result)           # Send the robot's pose to matlab via websocket as one string to be parsed
            #
            # ############################## Output Overlays #########################################