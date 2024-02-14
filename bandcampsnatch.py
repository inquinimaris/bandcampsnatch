import wget
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
s = Service(CHROMEDRIVER_PATH)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--mute-audio")
driver = webdriver.Chrome(service=s, options=chrome_options)

linkToSnatchFrom = input('Paste link to album (ex.: https:artist.bandcamp.com/album/my-preciousss-album): \n')
data = driver.get(linkToSnatchFrom)
album_title = driver.title.split('|')[0].strip()
artist_name = driver.title.split('|')[1].strip()
print(f'Album: {album_title} \n Artist: {artist_name}')
album_cover = driver.find_elements(By.ID, 'tralbumArt')[0].find_elements(By.TAG_NAME, 'img')[0].get_attribute('src')
track_table = driver.find_elements(By.ID, 'track_table')[0]
track_list = track_table.find_elements(By.TAG_NAME, 'tr')
album_size = len(track_list)
print(f'Tracks in album: {album_size}')
print('===============================')
for index, track in enumerate(track_list):
	human_index = index+1
	play_button = track.find_elements(By.CSS_SELECTOR, 'a[role="button"]')[0]
	track_title = track.find_elements(By.CLASS_NAME, 'track-title')[0].text
	print(f'Getting: {track_title}')
	play_button.click()
	WebDriverWait(driver, 3)
	audio_tags = driver.find_elements(By.CSS_SELECTOR, 'audio[src]')

	for audio_tag in audio_tags:
		src_value = audio_tag.get_attribute('src')
		print(src_value)
		filename = f"{str(human_index)}. {track_title}.mp3"
		directory_path = Path(f"/home/amarisq/{album_title}")
		directory_path.mkdir(parents=True, exist_ok=True)
		wget.download(src_value, out=f"/home/amarisq/{album_title}/{filename}")
		print(f"\n{track_title} downloaded")
		if album_size - human_index != 0:
			print(f'Downloaded {human_index} out of {album_size}, {album_size - human_index} tracks remains')
		else:
			print(f'Album downloaded')
	print('===============================')
print("Finishing touch, getting album cover...")
wget.download(album_cover, out=f"/home/amarisq/{album_title}/cover.jpg")
print("\n Done. \n Happy vibing~")
driver.quit()