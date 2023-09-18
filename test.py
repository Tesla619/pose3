marker_sizes = {}

# Set the size values for the specified ID ranges
for id_range, size in [(range(0, 4), 0.05), (range(12, 17), 0.05), (range(5, 12, 2), 0.065), (range(4, 7, 2), 0.08), (range(8, 11, 2), 0.125)]:
    for marker_id in id_range:
        marker_sizes[marker_id] = size
        
for i in range(17):
    print(f"{i}: {marker_sizes[i]}")