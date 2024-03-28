import requests
from bs4 import BeautifulSoup

URL = "https://www.spriters-resource.com/pc_computer/ragnarokonline/"
DOWNLOAD_URL = "https://www.spriters-resource.com/download/"
response = requests.get(URL)
html = response.text
soup = BeautifulSoup(html, "html.parser")
target_div = soup.find('div', class_='sect-name', title='Enemies')
print(target_div.prettify())

parent_div = target_div.find_parent('div')
next_sibling_div = parent_div.find_next_sibling('div') if parent_div else None
print(next_sibling_div.prettify())

a_tags = next_sibling_div.find_all('a')
for tag in a_tags:
    print(tag.get('href').split('/')[-2])
