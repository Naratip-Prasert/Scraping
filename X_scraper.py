from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import toml
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import streamlit as st

config = toml.load("secrets.toml")
username = config["twitter"]["username"]
password = config["twitter"]["password"]
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    driver.get("https://x.com/login")
    wait = WebDriverWait(driver, 60)

    # 🔑 รอให้ช่องใส่ username ปรากฏ แล้วกรอก
    username_input = wait.until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    username_input.send_keys(username)
    username_input.send_keys(Keys.ENTER)
    time.sleep(2)

    # 🔐 รอให้ช่อง password โผล่แล้วกรอก
    password_input = wait.until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(5)  # รอให้ redirect เข้าหน้า home

    # ✨ พอ login แล้วก็เหมือนโค้ดเดิมเลย
    search_box = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"] | //input[@data-testid="SearchBox_Search_Input"]'))
    )
    search_box.clear()
    search_box.send_keys("เที่ยวเชียงใหม่")
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')[:30]
    
    for t in tweets:
        try:
            text_el = t.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            text = text_el.text
        except:
            text = "(no text found)"

        try:
            link_el = t.find_element(By.XPATH, './/a[contains(@href,"/status/")]')
            url = link_el.get_attribute("href")
        except:
            url = "(no link found)"

        print("—"*30)
        print(text[:150].replace("\n", " "))
        print(url)

finally:
    driver.quit()
