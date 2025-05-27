import datetime
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode
from time import sleep

import pandas as pd
import requests
import streamlit as st

# ======= Configuration =======
API_KEY = st.secrets["GOOGLE_API_KEY"]
CSE_ID = st.secrets["CUSTOM_SEARCH_ENGINE_ID"]
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# ======= Helper Function =======
@st.cache_data
def fetch_google_results(query: str, extra_params: Optional[Dict[str, str]] = None) -> Tuple[List[Dict], Optional[str]]:
    if not query:
        return [], "Search query cannot be empty"
    if not API_KEY:
        return [], "Missing API Key"
    if not CSE_ID:
        return [], "Missing CSE ID"

    all_results: List[Dict] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for start in range(1, 101, 10):
        params = {
            "key": API_KEY,
            "cx": CSE_ID,
            "q": query,
            "start": start,
            "num": 10,
            "gl": "th",
            "hl": "th",
        }
        if extra_params:
            params.update(extra_params)

        try:
            resp = requests.get(SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except requests.HTTPError as err:
            code = resp.status_code
            if code == 403:
                return [], "API quota exceeded or invalid key"
            return [], f"HTTP error: {err}"
        except Exception as err:
            return [], f"Request error: {err}"

        items = data.get("items")
        if not items:
            break

        for it in items:
            all_results.append({
                "title": it.get("title", ""),
                "link": it.get("link", ""),
                "date_scraped": now,
            })

    return all_results, None


def build_query_and_params(
    query: str,
    all_words: str,
    exact_phrase: str,
    any_words: str,
    none_words: str,
    num_from: str,
    num_to: str,
    site: str,
    filetype_ext: str,
    lr: str,
    cr: str,
    date_restrict: str,
    filter_facebook: bool,
    filter_x: bool
) -> Tuple[str, Dict[str, str]]:
    terms: List[str] = []
    if all_words:
        terms += all_words.split()
    if exact_phrase:
        terms.append(f'"{exact_phrase}"')
    if any_words:
        group = " OR ".join(any_words.split())
        terms.append(f'({group})')
    if none_words:
        terms += [f'-{w}' for w in none_words.split()]
    if num_from and num_to:
        terms.append(f'{num_from}..{num_to}')
    if site:
        terms.append(f'site:{site}')

    # ✅ เพิ่ม site filter สำหรับ Facebook / X
    site_filters = []
    if filter_facebook:
        site_filters.append("site:facebook.com")
    if filter_x:
        site_filters.append("site:x.com")
    if site_filters:
        terms.append("(" + " OR ".join(site_filters) + ")")

    q = query or " ".join(terms)
    if query and terms:
        q = f"{query} " + " ".join(terms)

    extras: Dict[str, str] = {}
    if filetype_ext:
        extras["fileType"] = filetype_ext
    if lr:
        extras["lr"] = lr
    if cr:
        extras["cr"] = cr
    if date_restrict:
        extras["dateRestrict"] = date_restrict

    return q, extras



# ======= Streamlit UI =======
def main():
    st.set_page_config(page_title="Google Multi-Keyword Scraper", layout="wide")
    st.title("🔎 Google Advanced Multi-Keyword Scraper")

# ✅ Checkbox กรองเฉพาะ Facebook หรือ X (ก่อนพิมพ์คำค้น)
    col_fb, col_x = st.columns(2)
    filter_facebook = col_fb.checkbox("🔵 เฉพาะ Facebook")
    filter_x = col_x.checkbox("⚫️ เฉพาะ X (Twitter)")

    st.markdown("💡 พิมพ์คำค้นหลายชุด คั่นด้วย `Enter` เช่น:\n```\nงาน\nที่เที่ยวในไทย\nChulaScaping\n```")

    keyword_input = st.text_area("📌 หลายคำค้น (ใส่ทีละบรรทัด)", height=150)
    queries = [line.strip() for line in keyword_input.splitlines() if line.strip()]

# Advanced filters (optional)
    with st.expander("🔧 ตัวเลือกขั้นสูง (Optional Filters)"):
        all_words = st.text_input("ทุกคำเหล่านี้ (All words)")
        exact_phrase = st.text_input("ตรงวลีนี้ (Exact phrase)")
        any_words = st.text_input("คำใดๆ เหล่านี้ (Any of these words)")
        none_words = st.text_input("ไม่รวมคำเหล่านี้ (None of these words)")
        col1, col2 = st.columns(2)
        num_from = col1.text_input("เลขตั้งแต่", key="num_from")
        num_to = col2.text_input("ถึง", key="num_to")
        site = st.text_input("ไซต์ (site:)")
        filetype = st.selectbox("File type", ["", "pdf", "doc", "xls", "ppt"])
        lr = st.selectbox("Language", ["", "lang_th", "lang_en"])
        cr = st.selectbox("Country", ["", "countryTH", "countryUS"])
        date_restrict = st.selectbox("Date limit", ["", "d1", "w1", "m1"])

    if st.button("🚀 ค้นหาทั้งหมด"):
        if not queries:
            st.warning("กรุณาใส่คำค้นอย่างน้อย 1 บรรทัด")
            return

        all_results = []
        with st.spinner(f"กำลังค้นหาทั้งหมด {len(queries)} คำค้น..."):
            for idx, base_query in enumerate(queries):
                q, extras = build_query_and_params(
                base_query, all_words, exact_phrase, any_words, none_words,
                num_from, num_to, site, filetype, lr, cr, date_restrict,
                filter_facebook, filter_x
            )
                st.info(f"🔍 ค้นหา ({idx+1}/{len(queries)}): `{q}`")
                results, error = fetch_google_results(q, extras)
                if error:
                    st.warning(f"❌ {error}")
                else:
                    all_results.extend(results)
                sleep(1)

        if not all_results:
            st.info("ไม่พบผลลัพธ์เลย")
            return

        df = pd.DataFrame(all_results).drop_duplicates(subset="link")
        st.success(f"🎉 รวมทั้งหมด {len(df)} รายการ (ไม่ซ้ำกัน)")
        st.dataframe(df)
        df_display = df.copy()
        df_display["link"] = df_display["link"].apply(lambda url: f'<a href="{url}" target="_blank">{url}</a>')
        st.markdown("### 🔗 ผลลัพธ์แบบคลิกได้")
        st.write("📌 คลิกลิงก์เพื่อเปิดหน้าเว็บ")
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 ดาวน์โหลด CSV", data=csv, file_name="results.csv", mime="text/csv")

        towrite = pd.io.common.BytesIO()
        with pd.ExcelWriter(towrite, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="results")
        towrite.seek(0)
        st.download_button("📥 ดาวน์โหลด Excel", data=towrite.read(), file_name="results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    main()
