import ast
from bs4 import BeautifulSoup as bs 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib

with open('../trends-data/processed_trends.json', 'r') as file:
     trends = file.readline()

trends = ast.literal_eval(trends)

# Web Scrapping para Pinterest
PATH = 'chromedriver_win32\chromedriver.exe'
driver = webdriver.Chrome(PATH)
driver.maximize_window()

for key in trends.keys():
    i = 0
    print(key)
    if key.startswith("#"):
        key = key.replace("#", "%23")
        print(key)
        driver.get(url=f'https://www.pinterest.com/search/pins/?q={key}')
    else:
        driver.get(url=f'https://www.pinterest.com/search/pins/?q={key}')
    time.sleep(15)
    myDiv = driver.find_element(By.CSS_SELECTOR, '#mweb-unauth-container > div > div.zI7.iyn.Hsu > div.F6l.ZZS.k1A.zI7.iyn.Hsu > div > div > div > div:nth-child(1)')
    myDiv = myDiv.get_attribute('innerHTML')
    soup = bs(str([myDiv]), "html.parser")
    imagens = soup.find_all("img")
    for image in imagens:
        # Print image source
        print(image['src'])
        urllib.request.urlretrieve(image['src'], f"imgs/{key}-{i}.jpg")
        i += 1