import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -----------------------------------------------
# 🔍 Debug Block: Torch and Import Check
# -----------------------------------------------
st.title("🌐 COSCO News Dashboard")

try:
    import torch
    st.success(f"✅ torch loaded: {torch.__version__}")
except Exception as e:
    st.error(f"❌ torch import failed: {e}")

try:
    from scraper import run_scraper
    st.success("✅ scraper.py imported successfully")
except Exception as e:
    st.error(f"❌ scraper import failed: {e}")

# -----------------------------------------------
# 🛠️ Sidebar Controls
# -----------------------------------------------
st.sidebar.title("🛠️ Options")

# ✅ Scrape latest news from all sites
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
# 🗂️ Load the scraped data
# -----------------------------------------------
@st.cache_data
def load_data():
    import os
    if not os.path.exists("all_sites_summaries3.csv"):
        st.warning("⚠️ CSV not found. Click 'Scrape Latest News' to generate it.")
        return pd.DataFrame(columns=["Title", "URL", "Summary", "Site"])
    
    try:
        df = pd.read_csv("all_sites_summaries3.csv")
        df.dropna(subset=["Title", "URL", "Summary"], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
        return pd.DataFrame(columns=["Title", "URL", "Summary", "Site"])

df = load_data()

# 🔍 Filter by keyword
if search_keyword:
    df = df[df["Title"].str.contains(search_keyword, case=False) | df["Summary"].str.contains(search_keyword, case=False)]

# ✅ Sort articles by URL
df = df.sort_values(by="URL")

# -----------------------------------------------
# 📊 Visualizations
# -----------------------------------------------
if not df.empty:
    st.subheader("📊 Article Count by Source Site")
    site_counts = df['Site'].value_counts().reset_index()
    site_counts.columns = ['Site', 'Article Count']
    fig = px.bar(site_counts, x='Site', y='Article Count', title="Number of Articles per Site")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("☁️ Word Cloud of Article Titles")
    title_text = ' '.join(df['Title'].dropna().tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(title_text)
    fig_wc, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig_wc)

# -----------------------------------------------
# 📄 Article Summaries
# -----------------------------------------------
if df.empty:
    st.warning("No articles found. Try changing the keyword or scraping again.")
else:
    for row in df.itertuples():
        site_name = row.Site.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        st.markdown(f"🌐 **Source:** {site_name}")
        st.subheader(row.Title)
        st.markdown(f"[🔗 Read Full Article]({row.URL})", unsafe_allow_html=True)
        st.write(row.Summary)
        st.markdown("---")

# -----------------------------------------------
# ⬇️ CSV Download Option
# -----------------------------------------------
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, "cosco_summaries.csv", "text/csv")

# -----------------------------------------------
# 🧾 Footer
# -----------------------------------------------
st.markdown("🛠️ Built by **Surya Sanjeeva Pravarsha Erodula** · Powered by Python & Streamlit")
