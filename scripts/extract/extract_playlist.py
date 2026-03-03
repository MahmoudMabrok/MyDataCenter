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
    {"id": "PLnpYU8_AiEPeETAG37WSfH66g9drakaQ8",   "title": "محاضرات ودروس | باسل مؤنس - رحمه الله"},
    {"id": "PLnpYU8_AiEPf_Raw3VWCLu2NwIgivmnLf",   "title": "مجالس تدبر سورة القصص | باسل مؤنس - رحمه الله"},
    {"id": "PLnpYU8_AiEPewfBVzCnG4jNGMwzfuxfDd",   "title": "تأملات في سورة"},
    {"id": "PLnpYU8_AiEPc0V5b4ERUsW9LWGua8ZyPj",   "title": "العشر الأوائل من ذي الحجة | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPeeDJir91RzWtrC20sHCUZq",   "title": "رحلة التغيير | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPckxxAllceOU-63r1HboODw",   "title": "بصائر من أحداث غزة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPfn3UF-g0Yt0-pIjjoOnTAd",   "title": "نشر الأمل وبيان العمل في أزمنة الاستضعاف وأوقات الفتنة  | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPdjSiiifV0DG-GMStHOwOKr",   "title": "بصائر في أحداث غزة"},
    {"id": "PLnpYU8_AiEPca6B9kXuX44kPch0SysAC",   "title": "خطب الجمعة | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPdojYqbF0zQDYh3GjILvD4s",   "title": "مساق الارتباط بالقرآن ولقاءات الاستعداد لشهر رمضان"},
    {"id": "PLnpYU8_AiEPde-MdxdMv5KCbcF12c8jir",   "title": "مجالس الأدب المفرد | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeHheyGmYpwooB69lfbVtrU",   "title": "أمسيات رمضانية"},
    {"id": "PLnpYU8_AiEPev8cUALoZx3AkMsVDHfDfh",   "title": "تفسير سور من جزء (عم) | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPcFEe-xQ6oixXjhaSJh6DhN",   "title": "أمسيات تربوية"},
    {"id": "PLnpYU8_AiEPf4Krk5RXEVRGlQYx24wOZ-",   "title": "مجالس علوم القرآن وأصول التفسير | التعليق على التحرير في أصول التفسير | عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPeQRMu7ON4GnoPBkbgwkju6",   "title": "تفسير سورة البقرة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPfm_OivXkTXUrF8Pp7ptKEk",   "title": "خواطر رمضانية"},
    {"id": "PLnpYU8_AiEPfDgV7O_cvduDPZNH8pJb7n",   "title": "من هدايات القرآن في سوره وأجزائه | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPelFBxkokcbbN0547AGQwDK",   "title": "علمتني آية | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPeUBFZxtE8EU0lGcoj7x9Ab",   "title": "تفسير وتدبر سورة الغاشية | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPd1K4-8-4KgyYlJ6fHmdwqH",   "title": "تفسير وتدبر سورة الإنسان | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPfiT4onQS9D7r2YSeZrIbhI",   "title": "تفسير وتدبر سورة مريم | الشيخ عمرو الشرقاوي"},
    {"id": "PLnpYU8_AiEPf3f9WT_iUw0q21ZsoHgBY4",   "title": "بصائر قرآنية | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPcJH_-BGuDmgOPpQNv7HvaN",   "title": "تفسير سورة الأعلى | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeMqjtr8lviajdnGyiDUm00",   "title": "تفسير سورة الملك | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPfxj7mEab8AexFWz1spy2tt",   "title": "تفسير سورة المجادلة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPc951zPJy381bXXRX-5BwYO",   "title": "تفسير سورة البقرة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPcJZCTR_lkT6JY6q2o5b3Tv",   "title": "تفسير سورة المائدة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPcHm6EttOPkm2PeaymwP1N4",   "title": "تفسير سورة الفاتحة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPe-LWjIO3XFXbfQer-fNd8f",   "title": "أصول الانحراف | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeRNulHmpnXkQaNW6LmFnf4",   "title": "بصائر تربوية في طريق الالتزام | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPdZtOcZemEHETeOjWakJpKE",   "title": "تفسير جزء (عَمَّ) | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeRwRLwExs7WaNRt3Y5rn7b",   "title": "تفسير جزء (تبارك) | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPcrPemW7RJ-6f-GLp1SAyFV",   "title": "تفسير جزء (قد سمع) | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPe5-BUmdYIYB724L77utkjb",   "title": "تفسير سورة الفتح | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPd-Zf4C6zs6sIE-Kyv4Ub_X",   "title": "تفسير سورة محمد | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPfL3CJdG_lZTebJ54X30LfF",   "title": "تفسير سورة يس | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPehMkOYBQdM93-xE0lzdTco",   "title": "تفسيرسورة فاطر | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeCoT-XqrZyvVH9fqnZjza-",   "title": "تفسير سورة سبأ | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPcqWmYmvSKU8_EjFsBjgGpG",   "title": "تفسير سورة العنكبوت | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPc4fer95kdz3gdMolAmnb6M",   "title": "تفسير سورة إبراهيم | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPegC34BzlfEWoLDPvSNfYUJ",   "title": "تفسير سورة الكهف | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPdxrsqkjo8YxLPQtjRMfr3U",   "title": "تفسير سورة الرعد | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeN5vuGrOEsiZYE0jlCDSD2",   "title": "تفسير سورة يوسف | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPc2iOrUi2wv8GHhKaCuHPJd",   "title": "تربويات | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPduGfkp3hlGAt-3P40GI_eN",   "title": "تفسير سورة الأعراف | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPe0CdoAZhh03fpX7PEGIpMv",   "title": "تفسير سورة الأنعام | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPfvH4J5i52AjkIudjhOcTdL",   "title": "شهر رمضان | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPdIqNOKiWQ11wh-WB9HxqMh",   "title": "العشر الأوائل من ذي الحجة | د أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPds36lPJ0NuqCGI2g2zpevF",   "title": "منوعات | د أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPf3SauvyORAyFHCN79N9b8b",   "title": "مجالس السُنَّة | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPct7B-VmBrWJWifYEcb2TtC",   "title": "مجالس القرآن | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeOynF9Q35m_3QgRq-yFtaC",   "title": "سلسلة إشكاليات | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPewP5IKNKO2Wr8x_s6LG6b5",   "title": "عن القرآن | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPeloOLMJh0V90KzpTpoLSIe",   "title": "كيف نبصر المنافقين | د. أحمد عبد المنعم"},
    {"id": "PLnpYU8_AiEPfiGot0mRagoWYrQ55rwcac",   "title": "مميزات الخطاب القرآني وطريقته في تقرير العقائد"},
    {"id": "PLnpYU8_AiEPe3HVGx3Kp7o_gk2mMalh5M",   "title": "مساق (الدليل إلى القرآن)"},
    {"id": "PLnpYU8_AiEPeb8Sod6Ltr7mpawOnnQsWK",   "title": "خطب الجمعة | د أحمد عبد المنعم"},
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
import ast as _ast

_extra_raw = _os.environ.get('EXTRA_PLAYLISTS', '[]').strip()
try:
    _extra = json.loads(_extra_raw) if _extra_raw else []
    if not isinstance(_extra, list):
        raise ValueError('EXTRA_PLAYLISTS must be a JSON array')
except (json.JSONDecodeError, ValueError) as _e:
    print(f'Warning: Could not parse EXTRA_PLAYLISTS – {_e}. Ignoring.')
    _extra = []

# Validate entries: each item must have non-empty 'id' and 'title' strings
def _is_valid_playlist(p):
    return (
        isinstance(p, dict)
        and isinstance(p.get('id'), str) and p['id'].strip()
        and isinstance(p.get('title'), str) and p['title'].strip()
    )

_valid_extra = [p for p in _extra if _is_valid_playlist(p)]
if len(_valid_extra) != len(_extra):
    _invalid = [p for p in _extra if not _is_valid_playlist(p)]
    print(f'Warning: Skipping {len(_invalid)} invalid playlist entry/entries (missing or empty id/title): {_invalid}')

# Deduplicate: extra playlists with an id already in the static list are skipped
_existing_ids = {p['id'] for p in playlists}
_new = [p for p in _valid_extra if p['id'] not in _existing_ids]
if _new:
    print(f'Adding {len(_new)} extra playlist(s) from workflow input: {[p["id"] for p in _new]}')

    # ------------------------------------------------------------------
    # Persist: write the new entries back into the `playlists` list in
    # this script file so future runs include them without extra input.
    # ------------------------------------------------------------------
    _script_path = _os.path.abspath(__file__)
    with open(_script_path, 'r', encoding='utf-8') as _f:
        _source = _f.read()

    # Locate the closing bracket of the `playlists = [...]` literal and
    # insert the new entries just before it.
    import re as _re
    _new_entries = ''.join(
        f'    {{"id": "{p["id"]}",   "title": "{p["title"]}"}},\n'
        for p in _new
    )
    # Match the playlists list block: from `playlists = [` up to the closing `]`
    _pattern = r'(playlists\s*=\s*\[.*?)(\n\])'  # non-greedy, DOTALL
    _replacement = r'\1\n' + _new_entries.rstrip('\n') + r'\2'
    _updated_source = _re.sub(_pattern, _replacement, _source, count=1, flags=_re.DOTALL)

    if _updated_source == _source:
        print('Warning: Could not locate the playlists list in the script. New entries were NOT persisted.')
    else:
        with open(_script_path, 'w', encoding='utf-8') as _f:
            _f.write(_updated_source)
        print(f'Persisted {len(_new)} new playlist(s) into the static list in {_script_path}')

all_playlists = playlists + _new

for playlist in all_playlists:
    try:
        extract_playlist(playlist['id'], playlist['title'])
    except Exception as e:
        print(f'Error scraping playlist {playlist["id"]}: {str(e)}')

print('Successfully completed scraping process')
