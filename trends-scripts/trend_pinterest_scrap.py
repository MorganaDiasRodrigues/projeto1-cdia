import ast
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib
import json
import requests
from selenium.common.exceptions import NoSuchElementException

with open('../trends-data/processed_trends.json', 'r') as file:
    trends = file.readline()

trends = ast.literal_eval(trends)

# Web Scraping for Pinterest
PATH = 'chromedriver_win32\chromedriver.exe'
driver = webdriver.Chrome(PATH)
# driver.maximize_window()

image_paths = {}  # Dictionary to store image paths for each key

for key in trends.keys():
    try:
        i = 0  # Counter variable for number of images saved
        if key.startswith("#"):
            key = key.replace("#", "")
            driver.get(url=f'https://www.pinterest.com/search/pins/?q={key}')
        else:
            driver.get(url=f'https://www.pinterest.com/search/pins/?q={key}')
        time.sleep(15)
        myDiv = driver.find_element(By.CSS_SELECTOR, '#mweb-unauth-container > div > div.zI7.iyn.Hsu > div.F6l.ZZS.k1A.zI7.iyn.Hsu > div > div > div > div:nth-child(1)')
        myDiv = myDiv.get_attribute('innerHTML')
        soup = bs(str([myDiv]), "html.parser")
        imagens = soup.find_all("img")
        image_paths[key] = {"images": []}  # Initialize the images list for the key
        for image in imagens:
            try:
                urllib.request.urlretrieve(image['src'], f"img/{key}-{i}.jpg")
                image_paths[key]["images"].append({"path": f"assets/{key}-{i}.jpg"})  # Add the image path to the list
                i += 1  # Increment the counter
                if i == 3:  # Save only three images for each key
                    print(f"Consegui baixar 3 imagens de: {key}")
                    break

            except (urllib.error.HTTPError, requests.exceptions.RequestException, Exception) as e:
                print(f"An exception occurred while downloading the image: {e}")
                print(f"The trend was: {key}")
                continue
    except NoSuchElementException:
        print(f"No such element found for the key: {key}. Skipping to the next key.")
        continue

driver.quit()  # Close the browser after scraping

# Save the image paths dictionary as JSON
with open("image_paths.json", "w") as json_file:
    json.dump(image_paths, json_file, indent=4)
