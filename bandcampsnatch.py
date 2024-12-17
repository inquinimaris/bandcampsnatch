import sys
from msilib.schema import Patch

import wget
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

dirToSave = Path(input('Location to save the album (tracks will be saved in a folder with album name):'
				  '\n(n.b.: you can hardcode directory path to avoid this prompt in the script on line 12)\n'))

# It might be a good idea to set the default location if input is left empty
# dirToSave = '/home/amarisq/Music/Faded Flowers'

linkToSnatchFromInput = input('Paste link to album (ex.: https:artist.bandcamp.com/album/my-preciousss-album): \n')
linkToSnatchFrom = linkToSnatchFromInput.split('?')[0].strip()

# я хз зачем здесь это если честно
# CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
# s = Service(CHROMEDRIVER_PATH)

chrome_options = Options()
chrome_options.add_argument("--mute-audio")
driver = webdriver.Chrome(options=chrome_options)
driver.get(linkToSnatchFrom)

album_title = driver.title[:driver.title.find('|')-1]
artist_name = driver.title[driver.title.find('|')+1:]
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
	play_button = track.find_elements(By.CSS_SELECTOR, 'a[role="button"]')[0]
	track_title = track.find_elements(By.CLASS_NAME, 'track-title')[0].text
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
	track_title = (track[0].replace('/', '_').replace('\\', '_').replace(':', '_')
				   .replace('*', '_').replace('?', '_').replace('"', '_')
				   .replace('<', '_').replace('>', '_').replace('|', '_'))
	track_link = track[1]
	completion = round((100 - ((album_size - human_index)/album_size)*100), 2)
	print(f'Downloading: {track_title} ({human_index}/{album_size})')
	filename = f"{human_index}. {track_title}.mp3"
	directory_path = Path(dirToSave) / album_title
	directory_path.mkdir(parents=True, exist_ok=True)


	output_path = directory_path / filename
	wget.download(track_link, out=str(output_path))

	if album_size - human_index != 0:
		print(
			f'\nDownloaded {human_index}/{album_size} ({completion}%) \n{album_size - human_index} track(s) remaining')
	else:
		print(f'Album downloaded')
	print('===============================')
print("Finishing touch, downloading album cover")

# Загрузка обложки альбома
cover_path = dirToSave / "cover.jpg"
wget.download(album_cover, out=str(cover_path))

print("\nDone.\nEnjoy the vibes~")