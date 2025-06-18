from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# เข้าสู่ระบบ Facebook (ต้อง login ด้วยตัวเองก่อน หรือใช้ cookies)
driver.get("https://www.facebook.com")
input("👉 Login Facebook ให้เสร็จก่อน แล้วกด Enter เพื่อเริ่ม")

# ใส่คำค้นหาที่ต้องการ
search_term = "ChulaScaping"

# ไปที่ช่องค้นหา
search_box = driver.find_element(By.XPATH, '//input[@aria-label="Search Facebook"]')
search_box.send_keys(search_term)
search_box.send_keys(Keys.ENTER)

# รอโหลด
time.sleep(5)

# ไปที่แท็บ "Posts"
driver.get(driver.current_url + "&filters=eyJ0eXBlIjoiZ3JvdXBfcG9zdHMifQ%3D%3D")  # ฟิลเตอร์โพสต์
time.sleep(5)

# ดึงลิงก์โพสต์
posts = driver.find_elements(By.XPATH, '//a[contains(@href, "/posts/")]')
for post in posts:
    print(post.get_attribute("href"))

# ปิดเบราว์เซอร์เมื่อเสร็จ
# driver.quit()
