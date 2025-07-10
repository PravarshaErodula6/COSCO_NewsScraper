from scraper import run_scraper  # ✅ Must be first

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="COSCO News Dashboard", layout="wide")
st.title("🌐 COSCO News Dashboard")

# -----------------------------------------------
# 🛠️ Sidebar Controls
# -----------------------------------------------
st.sidebar.title("🛠️ Options")

if st.sidebar.button("🔁 Scrape Latest News"):
    with st.spinner("Scraping... please wait."):
        try:
            run_scraper()
            st.success("✅ Scraping complete! Dashboard refreshed.")
        except Exception as e:
            st.error(f"❌ Scraper failed: {e}")
            st.sidebar.text(f"Debug: {e}")

search_keyword = st.sidebar.text_input("Enter keyword to filter articles")

# -----------------------------------------------
# 📄 Load CSV
# -----------------------------------------------
@st.cache_data
def load_data():
    csv_file = os.path.join(os.path.dirname(__file__), "all_sites_summaries3.csv")
    if not os.path.exists(csv_file):
        st.warning("⚠️ CSV not found. Click 'Scrape Latest News' to generate it.")
        return pd.DataFrame(columns=["Site", "Title", "URL", "Summary", "Scraped_At"])
    try:
        df = pd.read_csv(csv_file)
        df.dropna(subset=["Title", "URL"], inplace=True)
        df["Summary"] = df["Summary"].fillna("Summary not available.")
        return df
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
        return pd.DataFrame(columns=["Site", "Title", "URL", "Summary", "Scraped_At"])

df = load_data()

# 🔍 Filter
if search_keyword:
    try:
        df = df[
            df["Title"].str.contains(search_keyword, case=False, na=False) |
            df["Summary"].str.contains(search_keyword, case=False, na=False)
        ]
    except Exception as e:
        st.sidebar.error(f"❌ Filter error: {e}")

# ✅ Sort
df = df.sort_values(by="Scraped_At", ascending=False)

# -----------------------------------------------
# 📊 Visualization
# -----------------------------------------------
if not df.empty:
    try:
        st.subheader("📊 Article Count by Site")
        site_counts = df['Site'].value_counts().reset_index()
        site_counts.columns = ['Site', 'Article Count']
        fig = px.bar(site_counts, x='Site', y='Article Count')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Chart error: {e}")

    try:
        st.subheader("☁️ Word Cloud from Titles")
        text = ' '.join(df['Title'].dropna().astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig_wc, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig_wc)
    except Exception as e:
        st.warning(f"⚠️ WordCloud error: {e}")

# -----------------------------------------------
# 📋 Show Articles
# -----------------------------------------------
if df.empty:
    st.warning("No articles found.")
else:
    st.subheader("📰 Articles")
    for row in df.itertuples():
        st.markdown(f"🌐 **{row.Site}** · 🕒 _{row.Scraped_At}_")
        st.subheader(row.Title)
        st.markdown(f"[🔗 Read Article]({row.URL})", unsafe_allow_html=True)
        st.write(row.Summary if isinstance(row.Summary, str) else "Summary not available.")
        st.markdown("---")

# -----------------------------------------------
# ⬇️ Download
# -----------------------------------------------
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "cosco_summaries.csv", "text/csv")

st.markdown("🛠️ Built by **Surya Sanjeeva Pravarsha Erodula**")
