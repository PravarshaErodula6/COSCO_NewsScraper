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

# ✅ Scrape latest news
if st.sidebar.button("🔁 Scrape Latest News"):
    with st.spinner("Scraping... please wait."):
        try:
            run_scraper()
            st.success("✅ Scraping complete! Dashboard refreshed.")
        except Exception as e:
            st.error(f"❌ Scraper failed: {e}")

# 🔍 Keyword filter
search_keyword = st.sidebar.text_input("Enter keyword to filter articles")

# -----------------------------------------------
# 📄 Load CSV
# -----------------------------------------------
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "all_sites_summaries3.csv")
    if not os.path.exists(csv_path):
        st.warning("⚠️ CSV not found. Click 'Scrape Latest News' to generate it.")
        return pd.DataFrame(columns=["Site", "Title", "URL", "Summary", "Scraped_At"])
    try:
        df = pd.read_csv(csv_path)
        df.dropna(subset=["Title", "URL"], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
        return pd.DataFrame(columns=["Site", "Title", "URL", "Summary", "Scraped_At"])

df = load_data()

# 🔍 Filter
if search_keyword:
    df = df[df["Title"].str.contains(search_keyword, case=False, na=False) |
            df["Summary"].str.contains(search_keyword, case=False, na=False)]

# ✅ Sort
df = df.sort_values(by="Scraped_At", ascending=False)

# -----------------------------------------------
# 📊 Visualization
# -----------------------------------------------
if not df.empty:
    st.subheader("📊 Article Count by Site")
    site_counts = df['Site'].value_counts().reset_index()
    site_counts.columns = ['Site', 'Article Count']
    fig = px.bar(site_counts, x='Site', y='Article Count')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("☁️ Word Cloud from Titles")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df['Title']))
    fig_wc, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig_wc)

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
        summary_text = row.Summary if isinstance(row.Summary, str) else "Summary not available."
        st.write(summary_text)
        st.markdown("---")

# -----------------------------------------------
# ⬇️ Download
# -----------------------------------------------
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "cosco_summaries.csv", "text/csv")

st.markdown("🛠️ Built by **Surya Sanjeeva Pravarsha Erodula**")
