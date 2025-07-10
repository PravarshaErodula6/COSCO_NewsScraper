import requests
import pandas as pd
from bs4 import BeautifulSoup
from transformers import pipeline
from urllib.parse import urljoin, urlparse
from datetime import datetime
import torch
import os
import time

# 🔧 Summarizer with retry handling
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    tokenizer="sshleifer/distilbart-cnn-12-6",
    framework="pt",
    device=-1
)

# 🌍 Websites to scrape
urls_to_scrape = [
    "https://www.offshorewind.biz/",
    "https://www.upstreamonline.com/",
    "https://www.rechargenews.com/",
    "https://www.offshore-energy.biz/",
    "https://gcaptain.com/",
    "https://www.oedigital.com/",
    "https://maritime-executive.com/",
    "https://www.marinelink.com/",
    "https://www.tradewindsnews.com/"
]

# 🔍 Keywords of interest
keywords = [
    "FID", "LNG", "Offshore", "Drilling", "Shell", "Transocean",
    "Floating Wind", "Pipelay Vessel"
]

# ❌ Words to avoid
skip_words = [
    "about", "privacy", "cookie", "contact", "events", "magazine", "tag", "topic",
    "category", "terms", ".pdf", "advertise", "media", "jobs", "newsletter", "feedback"
]

# 📰 Common article content containers
article_classes = [
    "article__body", "entry-content", "article-body", "post-content", "main-content",
    "td-post-content", "article-content", "single-content", "c-article-body"
]

def get_base_domain(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def extract_article_links(site_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(site_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a")
        article_links = set()

        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href")
            if not title or not href:
                continue
            if any(x in href.lower() for x in skip_words):
                continue
            if href.rstrip("/").endswith(".biz"):
                continue
            full_url = urljoin(site_url, href)
            if any(k.lower() in title.lower() for k in keywords):
                article_links.add((title, full_url))
        return list(article_links)
    except Exception as e:
        print(f"❌ Error loading {site_url}: {e}")
        return []

def extract_content(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        for class_name in article_classes:
            container = soup.find("div", class_=class_name)
            if container:
                text = " ".join(p.get_text() for p in container.find_all("p"))
                if len(text) > 100:
                    return text.strip()[:3000]

        # Fallback: extract all <p> tags
        text = " ".join(p.get_text() for p in soup.find_all("p"))
        return text.strip()[:3000] if len(text) > 100 else None
    except Exception as e:
        print(f"⚠️ Error extracting from {url}: {e}")
        return None

def summarize(text, retries=2):
    for attempt in range(retries):
        try:
            if not text or len(text.split()) < 50:
                return "Summary not available."
            summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
            return summary[0]["summary_text"]
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1}: Summarization error: {e}")
            time.sleep(2)
    return "Summary failed after retries."

def run_scraper():
    all_results = []

    for site in urls_to_scrape:
        print(f"\n🌐 Scraping: {site}")
        articles = extract_article_links(site)
        print(f"✅ Found {len(articles)} keyword-matching articles.")

        for title, url in articles:
            print(f"\n🔎 {title}\n🔗 {url}")
            content = extract_content(url)
            summary = summarize(content)
            all_results.append({
                "Site": get_base_domain(url),
                "Title": title,
                "URL": url,
                "Summary": summary,
                "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            print(f"✅ Summary: {summary[:90]}...\n{'-'*60}")

    df = pd.DataFrame(all_results)

    # 💾 Save to CSV beside app.py
    csv_path = os.path.join(os.path.dirname(__file__), "all_sites_summaries3.csv")
    df.to_csv(csv_path, index=False)

    print(f"\n📦 CSV updated at: {csv_path}")
    print(f"📝 Total Articles Saved: {len(df)}")

# Run directly from CLI
if __name__ == "__main__":
    run_scraper()
