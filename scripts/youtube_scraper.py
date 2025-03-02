import json
import os
import re
import time
from pytube import Playlist, YouTube

from yt_dlp import YoutubeDL

def get_youtube_title(url):
    try:
        # Create a YoutubeDL object
        ydl = YoutubeDL()
        
        # Extract video info
        info_dict = ydl.extract_info(url, download=False)
        
        # Return the title
        return info_dict.get('title', None)
    except Exception as e:
        print(f"Error fetching title: {e}")
        return None

# Function to extract video information manually to avoid pytube's title issues
def get_video_info(video_id, playlist_id, title):
    try:
        return {
            'title': title,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'video_id': video_id,
            'playlist_id': playlist_id
        }
    except Exception as e:
        print(f"Error getting info for video {video_id}: {str(e)}")
        return {
            'title': f"Video {video_id}",
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'video_id': video_id,
            'playlist_id': playlist_id
        }
# List of playlist URLs to scrape
playlists = [
    'PLx8eSI7UgsiGA9f1ztAHoemtDlfJUd5a3',
    'PLlXQj2VGUTmfOrpzgytlcIlu38pQWh4UJ',
    'PL7PzPXcv-qiwgoGrHFK_yISXKt-vDaD1C',
    'PLukAHj56HNKZN-7qGg2tsY5-txmFts1bg',
]

# Create output directory if it doesn't exist
output_dir = 'playlists'
os.makedirs(output_dir, exist_ok=True)

for playlist_id in playlists:
    try:
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

                title = get_youtube_title(video_url)

                print(f'Processing video: {title} {video_id}')
                
                # Get video info
                video_data = get_video_info(video_id, playlist_id, title)
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
            json.dump(videos, f, ensure_ascii=False, indent=2)
            
        print(f'Completed playlist: {playlist_title} with {len(videos)} videos')
        
    except Exception as e:
        print(f'Error scraping playlist {playlist_url}: {str(e)}')

# Create an index file with all playlist IDs and titles
print(f'Successfully completed scraping process')
