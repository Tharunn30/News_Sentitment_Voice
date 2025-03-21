import os
import logging
from typing import Optional, Dict, Any, List, Tuple

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gtts import gTTS
from deep_translator import GoogleTranslator
from rapidfuzz import fuzz  # For fuzzy matching

# Ensure necessary NLTK data is downloaded
nltk.download('vader_lexicon')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a persistent session with retries and custom headers
session = requests.Session()
headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/90.0.4430.93 Safari/537.36")
}
session.headers.update(headers)
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

def extract_publication_date(soup: BeautifulSoup) -> str:
    """
    Attempts to extract the publication date from common meta tags or time elements.
    """
    date = ""
    meta_props = [
        {"property": "article:published_time"},
        {"name": "pubdate"},
        {"property": "og:updated_time"}
    ]
    for attr in meta_props:
        meta_tag = soup.find("meta", attr)
        if meta_tag and meta_tag.get("content"):
            date = meta_tag.get("content").strip()
            logger.debug(f"Publication date found using {attr}: {date}")
            break

    if not date:
        time_tag = soup.find("time")
        if time_tag:
            date = time_tag.get("datetime", "").strip() or time_tag.get_text().strip()
            logger.debug(f"Publication date found in <time> tag: {date}")
    return date

def scrape_news(url: str) -> Optional[Dict[str, Any]]:
    """
    Scrapes a news article from a given URL and extracts key details.
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully fetched URL: {url}")
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.text.strip() if soup.title else "No Title Found"
    
    summary = ""
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc and meta_desc.get("content"):
        summary = meta_desc.get("content").strip()
    else:
        first_paragraph = soup.find("p")
        if first_paragraph:
            summary = first_paragraph.get_text().strip()

    publication_date = extract_publication_date(soup)
    article_data = {
        "title": title,
        "summary": summary,
        "publication_date": publication_date,
        "url": url
    }
    logger.debug(f"Scraped article data: {article_data}")
    return article_data

def analyze_sentiment(text: str) -> Tuple[str, Dict[str, float]]:
    """
    Analyzes sentiment of the provided text using NLTK's VADER.
    """
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    if scores['compound'] >= 0.05:
        sentiment = "Positive"
    elif scores['compound'] <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    logger.debug(f"Analyzed sentiment for text. Scores: {scores}, Label: {sentiment}")
    return sentiment, scores

def generate_tts(text: str, lang: str = "hi", filename: str = "sentiment_report_hi.mp3") -> str:
    """
    Translates the given text to Hindi and converts it into a TTS audio file.
    """
    try:
        hindi_text = GoogleTranslator(source='auto', target='hi').translate(text)
        logger.info(f"Translated text to Hindi: {hindi_text}")
        tts = gTTS(text=hindi_text, lang=lang)
        tts.save(filename)
        logger.info(f"TTS audio generated and saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise e

def process_articles(company_name: str) -> Tuple[List[Dict[str, Any]], Dict[str, int], str, str]:
    """
    Processes a list of predefined news article URLs:
    - Scrapes each article,
    - Performs sentiment analysis on its summary,
    - Aggregates sentiment counts,
    - Sorts articles by relevance using fuzzy matching with the provided company name,
    - Generates a comparative sentiment report,
    - Generates a Hindi TTS audio report.
    """
    news_urls = [
        "https://www.livemint.com/companies/start-ups/googles-cybersecurity-deal-spins-tiny-investment-into-4-billion-windfall-11742533799922.html",
        "https://www.cnbc.com/2025/03/19/nvidia-ceo-jensen-huang-why-deepseek-model-needs-100-times-more-computing.html",
        "https://www.news18.com/tech/nothing-phone-3a-tells-us-why-the-pro-doesnt-need-to-have-all-the-fun-9268839.html",
        "https://www.businesstoday.in/markets/stocks/story/ola-electric-shares-climb-8-today-is-this-ev-stock-a-short-term-buy-468771-2025-03-21",
        "https://www.businesstoday.in/markets/stocks/story/hindustan-construction-company-shares-zoomed-13-today-heres-why-468759-2025-03-21",
        "https://economictimes.indiatimes.com/industry/renewables/tata-group-partners-with-tesla-a-new-era-for-indian-electric-vehicle-supply-chains/articleshow/119270573.cms?from=mdr",
        "https://www.thehindu.com/sci-tech/technology/gadgets/lenovo-idea-tab-pro-with-144-hz-refresh-rate-panel-bundled-stylus-launched-in-india/article69343365.ece",
        "https://news.adobe.com/news/2025/03/adobe-and-microsoft-empower-marketers-with-ai-agents-in-microsoft-365-copilot",
        "https://www.newsbytesapp.com/news/science/musks-xai-joins-microsoft-backed-ai-consortium-deepening-rivalry-with-openai/story",
        "https://indianexpress.com/article/technology/tech-news-technology/what-is-wiz-why-is-google-acquiring-for-32-billion-9895135/"
    ]
    
    articles = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    
    for url in news_urls:
        article_data = scrape_news(url)
        if article_data is None:
            continue
        if not article_data["summary"] or len(article_data["summary"]) < 20:
            logger.warning(f"Article summary too short or missing for URL: {url}")
            continue

        sentiment, scores = analyze_sentiment(article_data["summary"])
        article_data["sentiment"] = sentiment
        article_data["sentiment_scores"] = scores
        sentiment_counts[sentiment] += 1
        articles.append(article_data)
    
    # Compute a relevance score using fuzzy matching.
    # We use token_set_ratio to measure similarity between the company name and article content.
    for article in articles:
        combined_text = article["title"] + " " + article["summary"]
        article["relevance"] = fuzz.token_set_ratio(company_name.lower(), combined_text.lower())
    
    # Sort articles in descending order of relevance (i.e. higher score means more relevant)
    articles = sorted(articles, key=lambda x: x["relevance"], reverse=True)
    
    comparative_report = (
        "Comparative Analysis:\n"
        f"Total Articles: {len(articles)}\n"
        f"Positive: {sentiment_counts['Positive']}, "
        f"Negative: {sentiment_counts['Negative']}, "
        f"Neutral: {sentiment_counts['Neutral']}\n"
    )
    logger.info("Comparative report generated.")
    tts_file = generate_tts(comparative_report, lang="hi", filename="sentiment_report_hi.mp3")
    
    return articles, sentiment_counts, comparative_report, tts_file
