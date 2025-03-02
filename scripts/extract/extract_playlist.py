from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import re


# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Specify the path to the Chromium binary
chrome_options.binary_location = "/usr/bin/chromium-browser"

# Set up ChromeDriver service
service = Service("/usr/lib/chromium-browser/chromedriver")

# Remove the global WebDriver initialization

playlists = [
    'PLx8eSI7UgsiGA9f1ztAHoemtDlfJUd5a3',
    'PLlXQj2VGUTmfOrpzgytlcIlu38pQWh4UJ',
    'PL7PzPXcv-qiwgoGrHFK_yISXKt-vDaD1C',
    'PLukAHj56HNKZN-7qGg2tsY5-txmFts1bg',
]

output_dir = 'playlists'
os.makedirs(output_dir, exist_ok=True)


def extract_playlist(playlist_id):
    # Initialize the WebDriver within the function
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("start loading")
        # Open the YouTube playlist URL
        playlist_url= f'https://www.youtube.com/playlist?list={playlist_id}'
        driver.get(playlist_url)

        output_file = f'{output_dir}/{playlist_id}.json'

        print("Page loaded successfully")
        # Wait for the page to load

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer"))
        )

        print("WebDriverWait")
       
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        # Scroll to load all videos in the playlist
        last_height = driver.execute_script("return document.documentElement.scrollHeight")

        print("last_height")
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.documentElement.scrollHeight") > last_height
        )
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            print("in loop")
            time.sleep(2)  # Adjust the sleep time as needed
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print("All videos loaded")  

        # Extract video titles and links
        video_elements = driver.find_elements(By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer")

        print("All videos loaded 2")  
        videos = []

        for video in video_elements:
            title = video.get_attribute("title")
            link = video.get_attribute("href")
            
            video_id_match = re.search(r'v=([\w-]+)', link)
            if not video_id_match:
                print(f'Could not extract video ID from {link}')
                continue
                
            video_id = video_id_match.group(1)

            videos.append(
                {
            'title': title,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
            'video_id': video_id,
            'playlist_id': playlist_id
              }
            )

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)    
            

    except Exception as e:
        print(f"## Error scraping playlist {playlist_id}: {str(e)}")
    finally:
        # Close the browser
        if driver is not None:
            driver.quit()


for playlist_id in playlists:
    try:
        extract_playlist(playlist_id)
    except Exception as e:
        print(f'Error scraping playlist {playlist_id}: {str(e)}')

# Create an index file with all playlist IDs and titles
print(f'Successfully completed scraping process')        