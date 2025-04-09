import streamlit as st
import pandas as pd
import datetime

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
st.title("🌐 Offshore & Energy News Dashboard")
st.caption(f"🗓️ Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

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
