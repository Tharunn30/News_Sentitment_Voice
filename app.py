import gradio as gr
from utils import process_articles

def generate_report(company_name: str):
    """
    This function processes the news articles and generates:
      - A comparative report,
      - Sentiment distribution,
      - Formatted article details,
      - And the TTS audio file path.
    The input company_name is not used in processing (as URLs are predefined)
    but is displayed in the output.
    """
    articles, sentiment_counts, comparative_report, tts_file = process_articles()
    
    # Format articles for display
    articles_formatted = ""
    for article in articles:
        articles_formatted += f"Title: {article['title']}\n"
        articles_formatted += f"Summary: {article['summary']}\n"
        articles_formatted += f"Publication Date: {article['publication_date']}\n"
        articles_formatted += f"Sentiment: {article['sentiment']}\n"
        articles_formatted += f"URL: {article['url']}\n"
        articles_formatted += "-------------------------------\n"
    
    # Format sentiment counts as a string
    sentiment_text = "Sentiment Distribution:\n"
    for sentiment, count in sentiment_counts.items():
        sentiment_text += f"{sentiment}: {count}\n"
    
    return comparative_report, sentiment_text, articles_formatted, tts_file

# Define Gradio Interface
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
    description="Extracts news articles, performs sentiment analysis, and generates a Hindi TTS audio report."
)

if __name__ == "__main__":
    iface.launch()
