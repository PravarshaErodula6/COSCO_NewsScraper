import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ✅ Load the scraped CSV
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("all_sites_summaries3.csv")
        df.dropna(subset=["Title", "URL", "Summary"], inplace=True)
        return df
    except FileNotFoundError:
        st.error("CSV file not found. Run the scraper first.")
        return pd.DataFrame(columns=["Title", "URL", "Summary", "Site"])

# ✅ Load and prepare data
df = load_data()

# Sidebar - Keyword filter
st.sidebar.title("🔍 Filter Options")
search_keyword = st.sidebar.text_input("Enter keyword to filter articles")

# Filter by keyword if entered
if search_keyword:
    df = df[df["Title"].str.contains(search_keyword, case=False) | df["Summary"].str.contains(search_keyword, case=False)]

# ✅ Sort by URL (to group by website)
df = df.sort_values(by="URL")

# App Header
st.title("🌐 COSCO News Dashboard")
st.caption(f"🗓️ Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ✅ Dashboard Visuals
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

# ✅ Show article results
if df.empty:
    st.warning("No articles found matching your filter.")
else:
    for row in df.itertuples():
        site_name = row.Site.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        st.markdown(f"🌐 **Source:** {site_name}")
        st.subheader(row.Title)
        st.markdown(f"[🔗 Read Full Article]({row.URL})", unsafe_allow_html=True)
        st.write(row.Summary)
        st.markdown("---")

# Footer
st.markdown("🛠️ Built by **Surya Sanjeeva Pravarsha Erodula** · Powered by Python & Streamlit")
