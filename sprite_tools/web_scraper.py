import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
from monster import Monster, save_monster_to_file
from logging import getLogger

logger = getLogger(__name__)

URL = "https://www.spriters-resource.com/pc_computer/ragnarokonline/"
DOWNLOAD_URL = "https://www.spriters-resource.com/download/"


def save_image(image_url, filename):
    res = requests.get(image_url)

    # Check if the request was successful
    if res.status_code == 200:

        if not os.path.exists("images"):
            os.makedirs("images")
        # Open a file in binary write mode
        with open("images/" + filename, 'wb') as file:
            # Write the contents of the response to the file
            file.write(res.content)
        print(f"Image saved as {filename}")
    else:
        print(f"Failed to retrieve image. Status code: {res.status_code}")


def get_image(image_url):
    res = requests.get(image_url)
    if res.status_code == 200:
        return res.content
    else:
        print(f"Failed to retrieve image. Status code: {res.status_code}")
        return None


response = requests.get(URL)
html = response.text
soup = BeautifulSoup(html, "html.parser")
target_div = soup.find('div', class_='sect-name', title='Enemies')
print(target_div.prettify())

parent_div = target_div.find_parent('div')
next_sibling_div = parent_div.find_next_sibling('div') if parent_div else None
print(next_sibling_div.prettify())

a_tags = next_sibling_div.find_all('a')

for tag in tqdm(a_tags):
    if not os.path.exists("monster_raw_objects"):
        os.makedirs("monster_raw_objects")
    monster_id = tag.get('href').split('/')[-2]
    monster_url = DOWNLOAD_URL + monster_id + "/"
    monster_image = get_image(monster_url)
    if not monster_image:
        logger.warning(f"Failed to retrieve image for monster {monster_id}")
        continue
    monster_object = Monster(monster_id, monster_image)
    save_monster_to_file(monster_object, f"monster_raw_objects/monster_raw_{monster_id}.pkl")

logger.info("Finished scraping monster images")
