import json
import os
import re
import time
from pytube import Playlist

# List of playlist URLs to scrape
playlists = [
    'https://www.youtube.com/playlist?list=PLx8eSI7UgsiGA9f1ztAHoemtDlfJUd5a3',
    # Add more playlists as needed
]

# Create output directory if it doesn't exist
output_dir = 'playlists'
os.makedirs(output_dir, exist_ok=True)

for playlist_url in playlists:
    try:
        # Extract playlist ID from URL
        playlist_id_match = re.search(r'list=([\w-]+)', playlist_url)
        if not playlist_id_match:
            print(f'Could not extract playlist ID from {playlist_url}')
            continue
            
        playlist_id = playlist_id_match.group(1)
        output_file = f'{output_dir}/{playlist_id}.json'
        
        playlist = Playlist(playlist_url)
        playlist_title = playlist.title
        print(f'Scraping playlist: {playlist_title} (ID: {playlist_id})')
        
        videos = []
        for video in playlist.videos:
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
            video_data = {
                'title': video.title,
                'url': f'https://www.youtube.com/watch?v={video.video_id}',
                'thumbnail': f'https://i.ytimg.com/vi/{video.video_id}/maxresdefault.jpg'
            }
            videos.append(video_data)
            print(f'Added video: {video.title}')
        
        playlist_data = {
            'playlist_title': playlist_title,
            'playlist_id': playlist_id,
            'playlist_url': playlist_url,
            'video_count': len(videos),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'videos': videos
        }
            
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, ensure_ascii=False, indent=2)
            
        print(f'Completed playlist: {playlist_title} with {len(videos)} videos')
        
    except Exception as e:
        print(f'Error scraping playlist {playlist_url}: {str(e)}')

# Create an index file with all playlist IDs and titles
try:
    playlist_index = []
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            with open(os.path.join(output_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                playlist_index.append({
                    'playlist_id': data.get('playlist_id', ''),
                    'playlist_title': data.get('playlist_title', ''),
                    'video_count': data.get('video_count', 0),
                    'filename': filename
                })
    
    # Save index file
    with open(f'{output_dir}/index.json', 'w', encoding='utf-8') as f:
        json.dump(playlist_index, f, ensure_ascii=False, indent=2)
    
    print(f'Created index file with {len(playlist_index)} playlists')
except Exception as e:
    print(f'Error creating index file: {str(e)}')

print(f'Successfully completed scraping process')
