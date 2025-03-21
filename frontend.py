import gradio as gr
from utils import process_articles

def generate_report(company_name: str):
    """
    Processes news articles based on the provided company name and returns:
      - A comparative sentiment report,
      - A sentiment distribution summary,
      - Detailed article information,
      - And the file path to the generated Hindi TTS audio.
    Articles are sorted by relevance using fuzzy matching with the company name.
    """
    articles, sentiment_counts, comparative_report, tts_file = process_articles(company_name)
    
    # Format articles for display
    articles_text = ""
    for article in articles:
        articles_text += f"Title: {article['title']}\n"
        articles_text += f"Summary: {article['summary']}\n"
        articles_text += f"Publication Date: {article['publication_date']}\n"
        articles_text += f"Sentiment: {article['sentiment']}\n"
        articles_text += f"Relevance Score: {article['relevance']}\n"
        articles_text += f"URL: {article['url']}\n"
        articles_text += "-------------------------\n"
    
    sentiment_text = "Sentiment Distribution:\n"
    for sentiment, count in sentiment_counts.items():
        sentiment_text += f"{sentiment}: {count}\n"
    
    return comparative_report, sentiment_text, articles_text, tts_file

iface = gr.Interface(
    fn=generate_report,
    inputs=gr.Textbox(label="Company Name", placeholder="Enter Company Name (e.g., Tesla)"),
    outputs=[
        gr.Textbox(label="Comparative Report"),
        gr.Textbox(label="Sentiment Distribution"),
        gr.Textbox(label="Articles"),
        gr.Audio(label="Hindi TTS Audio", type="filepath")
    ],
    title="NewsSentimentVoice",
    description="Extracts news articles, performs sentiment analysis, and generates a Hindi TTS audio report. Articles are sorted by relevance to the searched company."
)

if __name__ == "__main__":
    iface.launch()
