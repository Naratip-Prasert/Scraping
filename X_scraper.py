import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import io
from datetime import date

st.set_page_config(page_title="X Scraper", page_icon="🔎", layout="wide")
st.markdown("<h1 style='text-align: center;'>🚀 X Scraper</h1>", unsafe_allow_html=True)
st.markdown("### 🔐 Login and Advanced Search on [X](https://x.com) Automatically")

with st.form("login_and_search"):
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("👤 Username or Email", placeholder="กรอกชื่อผู้ใช้")
    with col2:
        password = st.text_input("🔒 Password", type="password", placeholder="กรอกรหัสผ่าน")

    search_term = st.text_input("🔍 คำที่ต้องการค้นหาใน X", placeholder="เช่น Chula")

    with st.expander("⚙️ ตั้งค่าการค้นขั้นสูง (Advanced Search)"):
        from_user = st.text_input("📌 ค้นหาจากผู้ใช้ (เช่น @chulatalk)")
        since_date = st.date_input("📅 เริ่มตั้งแต่", value=None)
        until_date = st.date_input("📅 ถึงวันที่", value=None)
        st.markdown("### 🧠 คำค้นขั้นสูง (Advanced Words)")
        all_words = st.text_input("📘 มีคำเหล่านี้ทุกคำ (เช่น: cat dog)")
        exact_phrase = st.text_input("🔍 วลีตรงกันเป๊ะ (เช่น: happy hour)")
        any_words = st.text_input("📗 มีคำใดคำหนึ่ง (เช่น: cat OR dog)")
        none_words = st.text_input("📕 ห้ามมีคำเหล่านี้ (เช่น: scam spam)")
        hashtags = st.text_input("🏷️ Hashtag (เช่น: #TCAS)")

        only_images = st.checkbox("🖼️ เฉพาะโพสต์ที่มีรูปภาพ")
        only_videos = st.checkbox("🎥 เฉพาะโพสต์ที่มีวิดีโอ")
        only_links = st.checkbox("🔗 เฉพาะโพสต์ที่มีลิงก์")

    num_pages = st.slider("📄 จำนวนหน้าที่ต้องการสแครป", min_value=1, max_value=50, value=3)

    submitted = st.form_submit_button("🎯 เริ่มค้นหาเลย!")

if submitted:
    st.info("⏳ กำลังเข้าสู่ระบบและค้นหา โปรดรอสักครู่...")

    search_query = search_term

    search_query = ""

    if all_words:
        search_query += f"{all_words} "
    if exact_phrase:
        search_query += f'"{exact_phrase}" '
    if any_words:
        search_query += ' OR '.join(any_words.split()) + " "
    if none_words:
        search_query += ' '.join(f"-{word}" for word in none_words.split()) + " "
    if hashtags:
        search_query += f"{hashtags} "

    if from_user:
        search_query += f" from:{from_user.replace('@', '')}"
    if since_date:
        search_query += f" since:{since_date.strftime('%Y-%m-%d')}"
    if until_date:
        search_query += f" until:{until_date.strftime('%Y-%m-%d')}"
    if only_images:
        search_query += " filter:images"
    if only_videos:
        search_query += " filter:videos"
    if only_links:
        search_query += " filter:links"

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://x.com/login")
        wait = WebDriverWait(driver, 60)

        username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(username)
        username_input.send_keys(Keys.ENTER)
        time.sleep(2)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

        search_box = wait.until(EC.presence_of_element_located((
            By.XPATH, '//input[@aria-label="Search"] | //input[@data-testid="SearchBox_Search_Input"]')))
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        driver.get(driver.current_url + "&f=live")
        time.sleep(5)

        last_count = 0
        for _ in range(num_pages):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            if len(tweets) == last_count:
                break
            last_count = len(tweets)

        data = []
        for t in tweets:
            try:
                text = t.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
            except:
                text = "(ไม่เจอข้อความ)"
            try:
                user_name = t.find_element(By.XPATH, './/div[@data-testid="User-Name"]//span').text
            except:
                user_name = "(ไม่เจอชื่อ)"
            try:
                user_id = t.find_element(By.XPATH, './/div[@data-testid="User-Name"]//a[contains(@href, "/")]').get_attribute("href").split("/")[-1]
            except:
                user_id = "(ไม่เจอ @id)"
            try:
                url = t.find_element(By.XPATH, './/a[contains(@href,"/status/")]').get_attribute("href")
            except:
                url = "(ไม่เจอลิงก์)"
            try:
                post_time = t.find_element(By.TAG_NAME, 'time').get_attribute("datetime")
            except:
                post_time = "(ไม่เจอเวลาโพสต์)"

            data.append({
                "ชื่อบนโปรไฟล์": user_name,
                "User ID (@...)": user_id,
                "ข้อความ": text[:150],
                "ลิงก์": url,
                "เวลาที่โพสต์": post_time,
                "เวลาที่ scraping": time.strftime("%Y-%m-%d %H:%M:%S")
            })

        df = pd.DataFrame(data)
        st.markdown("---")
        st.markdown("## 📊 ผลลัพธ์จากการค้นหา")

        st.success(f"🎉 พบทั้งหมด {len(df)} โพสต์จากคำค้น: `{search_query}`")
        st.dataframe(df.drop(columns=["ลิงก์"]))

        st.markdown("### 🔗 ลิงก์ทั้งหมด (กดเพื่อเปิดดูโพสต์)")
        st.write(df[["ชื่อบนโปรไฟล์", "User ID (@...)", "ข้อความ", "ลิงก์"]].to_html(escape=False), unsafe_allow_html=True)

        col_dl1, col_dl2 = st.columns(2)
        csv_data = df.to_csv(index=False).encode('utf-8')

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
        output.seek(0)
        excel_data = output.read()

        with col_dl1:
            st.download_button("📥 ดาวน์โหลด CSV", data=csv_data, file_name="x_scraped_results.csv", mime="text/csv")
        with col_dl2:
            st.download_button("📥 ดาวน์โหลด Excel (.xlsx)", data=excel_data, file_name="x_scraped_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    finally:
        driver.quit()
