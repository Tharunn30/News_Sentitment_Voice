import os
import logging
from typing import Optional, Dict, Any, List, Tuple

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gtts import gTTS

# Ensure necessary NLTK data is downloaded
nltk.download('vader_lexicon')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a persistent session with retries and custom headers
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/90.0.4430.93 Safari/537.36"
}
session.headers.update(headers)
retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)


def extract_publication_date(soup: BeautifulSoup) -> str:
    """
    Attempts to extract the publication date from common meta tags or time elements.
    
    Args:
        soup (BeautifulSoup): Parsed HTML of the article.
        
    Returns:
        str: Publication date string if found; otherwise, an empty string.
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
    
    Args:
        url (str): The URL of the news article.
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing title, summary,
                                  publication_date, and url if successful;
                                  otherwise, None.
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully fetched URL: {url}")
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title
    title = soup.title.text.strip() if soup.title else "No Title Found"
    
    # Extract summary: use meta description or first paragraph as fallback
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
    
    Args:
        text (str): Text to analyze.
        
    Returns:
        Tuple[str, Dict[str, float]]: A tuple containing the sentiment label
                                       (Positive/Negative/Neutral) and the raw scores.
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
    Converts the given text into a TTS audio file.
    
    Args:
        text (str): Text to convert to speech.
        lang (str): Language code for the TTS (default is Hindi "hi").
        filename (str): Output filename for the generated audio.
        
    Returns:
        str: Filename of the generated audio file.
    """
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        logger.info(f"TTS audio generated and saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise e


def process_articles() -> Tuple[List[Dict[str, Any]], Dict[str, int], str, str]:
    """
    Processes a list of predefined news article URLs:
    - Scrapes each article,
    - Performs sentiment analysis on its summary,
    - Aggregates sentiment counts,
    - Generates a comparative sentiment report,
    - Generates a Hindi TTS audio report.
    
    Returns:
        Tuple containing:
            - List of article data dictionaries,
            - Dictionary of sentiment counts,
            - Comparative report as a string,
            - Filename of the generated TTS audio file.
    """
    # Predefined list of news article URLs
    news_urls = [
        "https://indianexpress.com/article/india/it-ministry-grok-using-hindi-slang-abuses-x-9895705/",
        "https://indianexpress.com/article/world/trump-musk-french-scientist-denied-us-entry-9896678/",
        "https://indianexpress.com/article/sports/ipl/ipl-18-franchises-fan-promos-reels-movie-bgm-videos-csk-rcb-mi-kkr-9895794/",
        "https://indianexpress.com/article/sports/ipl/thanks-to-ipl-new-zealand-cleared-the-final-frontier-9893966/",
        "https://indianexpress.com/article/sports/chess/vidit-gujrathi-wins-freestyle-chess-where-preparations-seldom-matter-9893401/",
        "https://www.thehindu.com/news/national/indian-student-at-georgetown-university-detained-over-hamas-links-amid-trumps-crackdown-on-pro-palestinian-protests/article69351904.ece",
        "https://www.timesnownews.com/chennai/chennai-water-cut-temporary-disruption-from-march-21-26-check-list-of-affected-areas-article-119252341",
        "https://timesofindia.indiatimes.com/sports/formula-one/news/f1-pandit-eddie-jordan-who-managed-adrian-neweys-move-to-aston-martin-dies-of-cancer/articleshow/119251176.cms",
        "https://www.dtnext.in/news/business/cognizant-to-establish-14-acre-immersive-learning-center-at-siruseri-campus-chennai-827024",
        "https://www.dtnext.in/news/chennai/four-flights-cancelled-at-chennai-airport-due-to-passenger-shortage-826702"
    ]
    
    articles = []
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
    
    for url in news_urls:
        article_data = scrape_news(url)
        if article_data is None:
            continue
        # Ensure there is sufficient text to analyze
        if not article_data["summary"] or len(article_data["summary"]) < 20:
            logger.warning(f"Article summary too short or missing for URL: {url}")
            continue

        sentiment, scores = analyze_sentiment(article_data["summary"])
        article_data["sentiment"] = sentiment
        article_data["sentiment_scores"] = scores
        sentiment_counts[sentiment] += 1
        articles.append(article_data)
    
    # Create a comparative report
    comparative_report = (
        "Comparative Analysis:\n"
        f"Total Articles: {len(articles)}\n"
        f"Positive: {sentiment_counts['Positive']}, "
        f"Negative: {sentiment_counts['Negative']}, "
        f"Neutral: {sentiment_counts['Neutral']}\n"
    )
    logger.info("Comparative report generated.")

    # Generate Hindi TTS audio report
    tts_file = generate_tts(comparative_report, lang="hi", filename="sentiment_report_hi.mp3")
    
    return articles, sentiment_counts, comparative_report, tts_file
