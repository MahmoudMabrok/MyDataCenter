import json
import os
import re
import time
import requests
from pytube import Playlist, YouTube

# Function to extract video information manually to avoid pytube's title issues
def get_video_info(video_id, playlist_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        # Use requests to get the video page
        response = requests.get(f"https://www.youtube.com/watch?v={video_id}", headers=headers)
        
        # Extract title from response (simplified approach)
        title_match = re.search(r'<title>(.*?) - YouTube</title>', response.text)
        print(f"get_video_info {video_id}: {title_match}")
        title = title_match.group(1) if title_match else f"Video {video_id}"
        
        return {
            'title': title,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'video_id': video_id
        }
    except Exception as e:
        print(f"Error getting info for video {video_id}: {str(e)}")
        return {
            'title': f"Video {video_id}",
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'video_id': video_id,
            'playlistId': playlist_id
        }

# List of playlist URLs to scrape
playlists = [
    'PLx8eSI7UgsiGA9f1ztAHoemtDlfJUd5a3',
    # 'PLlXQj2VGUTmfOrpzgytlcIlu38pQWh4UJ',
    # 'PL7PzPXcv-qiwgoGrHFK_yISXKt-vDaD1C',
    # 'PLukAHj56HNKZN-7qGg2tsY5-txmFts1bg',
    # # Add more playlists as needed
    # 'PLnV8MkoYSPJDmJqmDAxfjd0Vqo7OnvztU',
    # 'PLq2oPZxNIlYSlxJ6eklTzCkvhdhyQKPBU',
    # 'PLx8eSI7UgsiGA9f1ztAHoemtDlfJUd5a3',
    # 'PLQR5pAkesbk50lGsy6qv-_1uHtr_gSEeG',
    # 'PLnpYU8_AiEPfvH4J5i52AjkIudjhOcTdL',
    # 'PLnpYU8_AiEPfDgV7O_cvduDPZNH8pJb7n',
    # 'PLnpYU8_AiEPfm_OivXkTXUrF8Pp7ptKEk',
    # 'PL7ML83_VFX3-piHq33v-f_OLwNBiCspbd',
    # 'PLq2oPZxNIlYR3ZE8BDgGhL9nzU7SHUVcP',
    # 'PLFkuO76ICjPmXSX0AOmy60e39KmeRD2Rt',
    # 'PLnpYU8_AiEPeQRMu7ON4GnoPBkbgwkju6'
]

# Create output directory if it doesn't exist
output_dir = 'playlists'
os.makedirs(output_dir, exist_ok=True)

for playlist_id in playlists:
    try:
        # Extract playlist ID from URL
        # playlist_id_match = re.search(r'list=([\w-]+)', playlist_url)
        # if not playlist_id_match:
        #     print(f'Could not extract playlist ID from {playlist_url}')
        #     continue
            
        # playlist_id = playlist_id_match.group(1)
        playlist_url= f'https://www.youtube.com/playlist?list={playlist_id}'
        output_file = f'{output_dir}/{playlist_id}.json'
        
        # Get playlist and its videos
        try:
            playlist = Playlist(playlist_url)
            playlist_title = playlist.title
        except Exception as e:
            print(f"Error getting playlist title: {str(e)}")
            playlist_title = f"Playlist {playlist_id}"
            
        print(f'Scraping playlist: {playlist_title} (ID: {playlist_id})')
        
        # Get video URLs instead of video objects to avoid pytube title issues
        video_urls = []
        try:
            video_urls = list(playlist.video_urls)
        except Exception as e:
            print(f"Error getting video URLs: {str(e)}")
            
        videos = []
        for video_url in video_urls:
            try:
                # Extract video ID from URL
                vi = YouTube(video_url) 
                video_id_match = re.search(r'v=([\w-]+)', video_url)
                if not video_id_match:
                    print(f'Could not extract video ID from {video_url}')
                    continue
                    
                video_id = video_id_match.group(1)
                
                # Get video info
                video_data = get_video_info(video_id, playlist_id)
                videos.append(video_data)
                print(f'Added video: {video_data["title"]}')
                
                # Add a small delay to avoid rate limiting
                time.sleep(1)
            except Exception as e:
                print(f"Error processing video {video_url}: {str(e)}")
        
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
        if filename.endswith('.json') and filename != "index.json":
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
