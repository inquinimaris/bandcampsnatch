import os
import sys
import wget
import requests
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# now it's just goes into `home/user/Music`. It's for my own convenience more than anything.
dirToSave = Path.home() / "Music/"
linkToSnatchFromInput = input('Paste link to album (ex.: https:artist.bandcamp.com/album/my-preciousss-album): \n')
linkToSnatchFrom = linkToSnatchFromInput.split('?')[0].strip()
CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
s = Service(CHROMEDRIVER_PATH)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--mute-audio")
driver = webdriver.Chrome(service=s, options=chrome_options)
data = driver.get(linkToSnatchFrom)

# prevent cookie banner from interfering
footer = driver.find_element(By.CSS_SELECTOR, "page-footer")
driver.execute_script("arguments[0].style.display = 'none'", footer)

album_title = driver.title.split('|')[0].strip()
artist_name = driver.title.split('|')[1].strip()
print(f' -- Artist:          {artist_name}')
print(f' -- Album:           {album_title}')
album_cover = driver.find_elements(By.ID, 'tralbumArt')[0].find_elements(By.TAG_NAME, 'img')[0].get_attribute('src')
track_table = driver.find_elements(By.ID, 'track_table')[0]
# track_list = track_table.find_elements(By.TAG_NAME, 'tr')
# // If there's lyrics available, it's placement in <tr> tags too,
# // and it happens there's no a[role="button"] in there, breaks the code
# // Neat idea for a feature though
track_list = track_table.find_elements(By.CSS_SELECTOR, 'tr.track_row_view')

album_size = len(track_list)
print(f' -- Tracks in album: {album_size}')
print('===============================')
album_list = []

for index, track in enumerate(track_list):
	human_index = index+1
	play_button = track.find_elements(By.CSS_SELECTOR, 'td.play-col a[role="button"]')[0]
	track_title = track.find_elements(By.CSS_SELECTOR, 'td.title-col .track-title')[0].text
	completion = round((100 - ((album_size - human_index)/album_size)*100), 2)
	sys.stdout.write('\033[K')
	print(f'Getting link for: {track_title}', end='\r')
	play_button.click()
	WebDriverWait(driver, 1)
	play_button.click()
	WebDriverWait(driver, 2)

	audio_tags = driver.find_elements(By.CSS_SELECTOR, 'audio[src]')

	src_value = audio_tags[0].get_attribute('src')
	album_list.append([track_title, src_value])
	sys.stdout.write('\033[K')
	print(f'{completion}% collected', end='\r')
print('\n')
print('Tracks\' links collected, closing Selenium and downloading tracks')
print('===============================')
driver.quit()
for index, track in enumerate(album_list):
	human_index = index+1
	track_title = track[0]
	track_link = track[1]
	completion = round((100 - ((album_size - human_index)/album_size)*100), 2)
	print(f'Downloading: {track_title} ({human_index}/{album_size})')
	sanitized_title = track_title.strip().replace("/", "_").replace("\\", "_")  # handle both / and \
	filename = f"{str(human_index)}. {sanitized_title}.mp3"
	directory_path = Path(f"{dirToSave}/{artist_name}/{album_title}")
	directory_path.mkdir(parents=True, exist_ok=True)
	output_path = os.path.join(dirToSave, album_title, filename)
	wget.download(track_link, out=output_path)
	if album_size - human_index != 0:
		print(f'\nDownloaded {human_index}/{album_size} ({completion}%) \n{album_size - human_index} track(s) remaining')
	else:
		print(f'Album downloaded')
	print('===============================')
print("Finishing touch, downloading album cover")
wget.download(album_cover, out=f"{dirToSave}/{album_title}/cover.jpg")
print("\nDone.\nEnjoy the vibes~")
