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

st.set_page_config(page_title="X Scraper", page_icon="🔎", layout="wide")
st.markdown("<h1 style='text-align: center;'>🚀 X Scraper</h1>", unsafe_allow_html=True)
st.markdown("### 🔐 ล็อกอินและค้นหาข้อมูลจากเว็บไซต์ [X](https://x.com) แบบอัตโนมัติ")

with st.form("login_and_search"):
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("👤 Username หรือ Email", placeholder="กรอกชื่อผู้ใช้")
    with col2:
        password = st.text_input("🔒 Password", type="password", placeholder="กรอกรหัสผ่าน")

    search_term = st.text_input("🔍 คำที่ต้องการค้นหาใน X", placeholder="เช่น เที่ยวเชียงใหม่")

    num_pages = st.slider("📄 จำนวนหน้าที่ต้องการสแครป (scroll)", min_value=1, max_value=50, value=3)

    submitted = st.form_submit_button("🎯 เริ่มค้นหาเลย!")

if submitted:
    st.info("⏳ กำลังเข้าสู่ระบบและค้นหา โปรดรอสักครู่...")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://x.com/login")
        wait = WebDriverWait(driver, 20)

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
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        driver.get(driver.current_url + "&f=live")
        time.sleep(5)

        for _ in range(num_pages):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')[:30]
        data = []

        for t in tweets:
            try:
                text_el = t.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                text = text_el.text
            except:
                text = "(ไม่เจอข้อความ)"
            try:
                name_el = t.find_element(By.XPATH, './/div[@data-testid="User-Name"]//span')
                user_name = name_el.text
            except:
                user_name = "(ไม่เจอชื่อ)"

            try:
                id_el = t.find_element(By.XPATH, './/div[@data-testid="User-Name"]//a[contains(@href, "/")]')
                user_id = id_el.get_attribute("href").split("/")[-1]
            except:
                user_id = "(ไม่เจอ @id)"

            try:
                link_el = t.find_element(By.XPATH, './/a[contains(@href,"/status/")]')
                url = link_el.get_attribute("href")
            except:
                url = "(ไม่เจอลิงก์)"

            try:
                time_el = t.find_element(By.TAG_NAME, 'time')
                post_time = time_el.get_attribute("datetime")
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

        st.success(f"🎉 พบทั้งหมด {len(df)} โพสต์จากคำค้น: `{search_term}`")
        st.dataframe(df.drop(columns=["ลิงก์"]))  # ซ่อนลิงก์คลิกไว้จาก DataFrame ปกติ

        st.markdown("### 🔗 ลิงก์ทั้งหมด (กดเพื่อเปิดดูโพสต์)")
        st.write(df[["ชื่อบนโปรไฟล์", "User ID (@...)", "ข้อความ", "ลิงก์"]].to_html(escape=False), unsafe_allow_html=True)

        # 🎁 ปุ่มดาวน์โหลด
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
