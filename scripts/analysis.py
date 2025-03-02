# wrtie pyhton script to aalyis all files in playlist folder and display total number of videos in all playlists and count of playlist
# Hint: You can use the os module to list all files in a directory and then read each file to extract the video count and playlist information.
# You can use the json module to read the contents of each file and extract the video count and playlist information.
# You can use a loop to iterate over all files in the directory and sum the video counts and count the playlists.
# You can use variables to store the total video count and playlist count.
# You can print the total video count and playlist count after processing all files in the directory.

import os
import json

# Path to the directory containing playlist files
playlist_dir = 'playlists'

# Initialize variables to store total video count and playlist count
total_video_count = 0
playlist_count = 0

# List all files in the directory
playlist_files = os.listdir(playlist_dir)

# Iterate over each file in the directory
for playlist_file in playlist_files:
    # Construct the full path to the file
    file_path = os.path.join(playlist_dir, playlist_file)
    
    # Read the contents of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        playlist_data = json.load(file)
        
        # Extract video count and playlist information
        video_count = len(playlist_data)
        # playlist_id = playlist_data['playlist_id']
        
        # Update total video count and playlist count
        total_video_count += video_count
        playlist_count += 1

# Display the total video count and playlist count
print(f'Total video count: {total_video_count}')
print(f'Playlist count: {len(playlist_files)}')

# Read the contents of the file
if os.path.exists('data.json'):
    with open('data.json', 'r', encoding='utf-8') as file:
        new_Data = json.load(file)
        new_Data['total_video_count'] = total_video_count
        new_Data['playlist_count'] = playlist_count
        with open('data.json', 'w', encoding='utf-8') as output_file:
          json.dump(new_Data, output_file, ensure_ascii=False, indent=4)
else:
    new_Data = {}

# Update the total video count and playlist count in the data


# Write the updated data back to the file
