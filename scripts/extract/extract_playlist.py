from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

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

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open the YouTube playlist URL
    playlist_url = "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
    driver.get(playlist_url)

    # Wait for the page to load
    time.sleep(5)  # Adjust the sleep time as needed

    # Scroll to load all videos in the playlist
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time as needed
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Extract video titles and links
    video_elements = driver.find_elements(By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.ytd-playlist-video-renderer")
    for video in video_elements:
        title = video.get_attribute("title")
        link = video.get_attribute("href")
        print(f"Title: {title}")
        print(f"Link: {link}")
        print("-" * 40)

finally:
    # Close the browser
    driver.quit()