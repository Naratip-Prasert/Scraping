import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

st.title("🔍 X (Twitter) Scraper")

query = st.text_input("ใส่คำค้นหา", "Chula")

if st.button("เริ่มค้นหา"):

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://x.com/login")
        wait = WebDriverWait(driver, 60)

        st.info("⏳ กรุณา login ด้วยตัวเองในหน้าที่เปิดขึ้นมา...")

        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search"] | //input[@data-testid="SearchBox_Search_Input"]'))
        )
        st.success("✅ Login สำเร็จ!")

        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')[:30]
        results = []

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

            results.append((text, url))

        if results:
            for i, (text, url) in enumerate(results, start=1):
                st.markdown(f"**{i}.** {text[:150].replace(chr(10), ' ')}")
                st.markdown(f"[🔗 ไปที่โพสต์]({url})")
                st.markdown("---")
        else:
            st.warning("ไม่พบโพสต์เลย")

    finally:
        driver.quit()
