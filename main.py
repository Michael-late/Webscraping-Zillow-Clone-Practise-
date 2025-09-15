from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import requests
import time
import os
from html import unescape

class Scraper:
    def __init__(self):
        self.zillow_url = "https://appbrewery.github.io/Zillow-Clone/"
        self.response = requests.get(self.zillow_url)
        self.soup = BeautifulSoup(self.response.text,"html.parser")
        
        self.properties = self.soup.select(".ListItem-c11n-8-84-3-StyledListCardWrapper")
        self.properties_links = [property.find("a" , attrs={"data-test":"property-card-link"}).get("href") for property in self.properties]
        
        self.properties_price_raw = [property.find("span" , attrs={"data-test":"property-card-price"}).text for property in self.properties]
        self.properties_price = [price.split("+")[0].replace("/mo","") for price in self.properties_price_raw]
        # print(self.properties_price)
        
        self.properties_address = [property.find("address" , attrs={"data-test":"property-card-addr"}).get_text().replace(" |", " ").strip() for property in self.properties]
        self.properties_length = len(self.properties)
        
class Form:
    def __init__(self, Scrappy: Scraper):
        self.scrappy = Scrappy
        load_dotenv()
        self.url = os.getenv("google_form")
        print(self.url)
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option("detach", True)
        load_dotenv()
        
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        self.chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        self.driver = webdriver.Chrome(options=self.chrome_options)

        for num in range(self.scrappy.properties_length):
            self.fill_data(num)
        
        
    def fill_data(self,num):
        self.driver.get(self.url)
        self.addr, self.price, self.link = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='text']")))        
        self.addr.send_keys(self.scrappy.properties_address[num])
        self.price.send_keys(self.scrappy.properties_price[num])
        self.link.send_keys(self.scrappy.properties_links[num])
        self.btn = self.driver.find_element(By.CSS_SELECTOR,"div[role='button']")
        self.btn.click()


Scrappy = Scraper()
Filling = Form(Scrappy)