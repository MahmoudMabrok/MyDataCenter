from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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

# ---------------------------------------------------------------------------
# Input: list of playlists to extract, each with an 'id' and a 'title'.
# Add new playlists here. Already-extracted files are skipped automatically.
# ---------------------------------------------------------------------------
playlists = [
    {"id": "PLj-c0x-mEc3teWsA0IX4LPtGfJ6y27-A-",   "title": "فهد الكندري | برنامج علمني القرآن"},
    {"id": "PLj-c0x-mEc3v0uD4N-fIBHO8Mhqqy2KOV",   "title": "استراحة مع وجدان العلي - تزكية النفس"},
    {"id": "PLj-c0x-mEc3vhkJ-d1d1QDgn27Tx8niSc",   "title": "سواعد الإخاء"},
    {"id": "PLj-c0x-mEc3seVyQE6Swp6Svh6Hg3FiOr",   "title": "رحلة الآخرة"},
    {"id": "PLS4AHyAvpjOqVlkpVY4h_ETN7tGYIlLAQ",   "title": "الا من اتى الله بقلب سليم | سامح حسين"},
    {"id": "PLx8eSI7UgsiGA9f1ztAHoemtDlfJUd5a3",   "title": "برنامج هدى للناس"},
    {"id": "PLlXQj2VGUTmfOrpzgytlcIlu38pQWh4UJ",   "title": "عالمغرب الموسم ٢"},
    {"id": "PL7PzPXcv-qiwgoGrHFK_yISXKt-vDaD1C",   "title": "برنامج لا إله إلا الله"},
    {"id": "PLukAHj56HNKZN-7qGg2tsY5-txmFts1bg",   "title": "تدبر قرآن التراويح"},
    {"id": "PLQVX7_Rc0v0sxfB-H-RhYZOdhFVyzbbvI",   "title": "أمداد قرآنية - سورة المؤمنون"},
    {"id": "PLPq7duxpJ2hQiI1ys24jgWjsY0heuuchY",   "title": "سلسلة حول آي القرآن | سؤال ثم أجب"},
    {"id": "PLPq7duxpJ2hRdlpEvpp2nt3uTLU6fArFN",   "title": "مبادرة هو الله | الشيخ محمد خيري"},
    {"id": "PLPq7duxpJ2hQjF2EhnRQ92dvz-7yOGf4h",   "title": "سلسلة الليل الساجي | الشيخ محمد خيري"},
    {"id": "PLPq7duxpJ2hTJKUQv4UUcgkKNE8KtQjLB",   "title": "سلسلة نقُص عليك | الشيخ محمد خيري"},
    {"id": "PLPq7duxpJ2hRtvHQWRLjZRKQvMa0I07KV",   "title": "سلسلة يتدارسونه 2 | الشيخ محمد خيري"},
    {"id": "PLPq7duxpJ2hTlRudRjHtG7F7wCHeBhh8U",   "title": "برنامج السراج المنير | الشيخ محمد خيري"},
]

output_dir = 'playlists'
os.makedirs(output_dir, exist_ok=True)


def extract_playlist(playlist_id, playlist_title):
    """Extract all videos from a YouTube playlist and save them to a JSON file.

    Each video entry will contain a ``playlist_title`` field so consumers
    know which playlist the video belongs to without having to look it up.

    Args:
        playlist_id: The YouTube playlist ID string.
        playlist_title: The human-readable title of the playlist.
    """
    output_file = f'{output_dir}/{playlist_id}.json'

    # Skip if already extracted
    if os.path.exists(output_file):
        print(f'Skipping {playlist_id} – output file already exists.')
        return

    print(f'Extracting playlist: {playlist_title} ({playlist_id})')
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Open the YouTube playlist URL
        playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
        driver.get(playlist_url)
        print('Page loaded, waiting for videos…')

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer"))
        )

        # Scroll to load all lazy-loaded videos
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract video titles and links
        video_elements = driver.find_elements(By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer")

        videos = []
        for video in video_elements:
            title = video.get_attribute("title")
            link = video.get_attribute("href")
            print(f'  Extracted: {title}')

            video_id_match = re.search(r'v=([\w-]+)', link)
            if not video_id_match:
                print(f'  Could not extract video ID from {link}')
                continue

            video_id = video_id_match.group(1)
            videos.append({
                'title': title,
                'playlist_title': playlist_title,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'thumbnail': f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg',
                'video_id': video_id,
                'playlist_id': playlist_id,
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)

        print(f'Saved {len(videos)} videos → {output_file}')

    except Exception as e:
        print(f'## Error scraping playlist {playlist_id}: {str(e)}')
    finally:
        if driver is not None:
            driver.quit()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
# Merge any extra playlists passed in via the EXTRA_PLAYLISTS env variable.
# The GitHub workflow sets this from the `extra_playlists` workflow_dispatch
# input, which is a JSON array of {"id": "...", "title": "..."} objects.
import os as _os

_extra_raw = _os.environ.get('EXTRA_PLAYLISTS', '[]').strip()
try:
    _extra = json.loads(_extra_raw) if _extra_raw else []
    if not isinstance(_extra, list):
        raise ValueError('EXTRA_PLAYLISTS must be a JSON array')
except (json.JSONDecodeError, ValueError) as _e:
    print(f'Warning: Could not parse EXTRA_PLAYLISTS – {_e}. Ignoring.')
    _extra = []

# Deduplicate: extra playlists with an id already in the static list are skipped
_existing_ids = {p['id'] for p in playlists}
_new = [p for p in _extra if p.get('id') and p['id'] not in _existing_ids]
if _new:
    print(f'Adding {len(_new)} extra playlist(s) from workflow input: {[p["id"] for p in _new]}')
all_playlists = playlists + _new

for playlist in all_playlists:
    try:
        extract_playlist(playlist['id'], playlist['title'])
    except Exception as e:
        print(f'Error scraping playlist {playlist["id"]}: {str(e)}')

print('Successfully completed scraping process')
