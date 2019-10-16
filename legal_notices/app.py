import re, csv
from time import sleep, time
from random import uniform, randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException  
#import requests
from bs4 import BeautifulSoup


url = 'https://www.idahopublicnotices.com/'
query = "trustee's sale"

start = time()
driver = webdriver.Chrome()
driver.get(url)
elem = driver.find_element_by_css_selector('#ctl00_ContentPlaceHolder1_as1_txtSearch')
elem.clear()
elem.send_keys(query)

#****************** click on captcha ****************** 
driver.find_element_by_css_selector("#recaptcha > div > div > iframe").click()



