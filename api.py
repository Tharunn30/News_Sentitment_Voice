import os
import asyncio
import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from utils import process_articles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NewsAPI")

# Define Pydantic models for request and response
class NewsRequest(BaseModel):
    company_name: str = Field(..., example="X")

class Article(BaseModel):
    title: str
    summary: str
    publication_date: Optional[str] = None
    sentiment: str
    sentiment_scores: Dict[str, float]
    url: str

class NewsResponse(BaseModel):
    company: str
    articles: List[Article]
    sentiment_counts: Dict[str, int]
    comparative_report: str
    tts_file: str

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Advanced News Summarization & Sentiment Analysis API",
    description="API that processes news articles, performs sentiment analysis, and generates a Hindi TTS audio report.",
    version="2.0.0"
)

# Enable CORS for all origins (customize for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="Health Check Endpoint")
async def health_check():
    """
    Simple endpoint to check if the API service is running.
    """
    return {"status": "ok", "message": "Service is healthy."}

@app.post("/api/process-news", response_model=NewsResponse, summary="Process news articles and generate a sentiment report")
async def process_news(request: NewsRequest):
    """
    Processes news articles by scraping, performing sentiment analysis, and generating a comparative report along with a Hindi TTS audio file.
    """
    try:
        # Offload the CPU-bound processing to a separate thread
        articles_data, sentiment_counts, comparative_report, tts_file = await asyncio.to_thread(process_articles)
        
        # Prepare the list of Article objects
        articles = [Article(**article) for article in articles_data]
        
        response = NewsResponse(
            company=request.company_name,
            articles=articles,
            sentiment_counts=sentiment_counts,
            comparative_report=comparative_report,
            tts_file=tts_file
        )
        logger.info(f"Processed news for company: {request.company_name}")
        return JSONResponse(content=response.dict())
    except Exception as e:
        logger.exception("Error processing news articles")
        raise HTTPException(status_code=500, detail=f"Error processing news: {str(e)}")

@app.get("/api/tts", summary="Download the generated Hindi TTS audio file")
async def get_tts():
    """
    Endpoint to download the Hindi TTS audio file generated from the comparative report.
    """
    tts_path = "sentiment_report_hi.mp3"
    if os.path.exists(tts_path):
        logger.info("Serving TTS audio file.")
        return FileResponse(
            path=tts_path,
            media_type="audio/mpeg",
            filename="sentiment_report_hi.mp3"
        )
    else:
        logger.error("TTS audio file not found.")
        raise HTTPException(status_code=404, detail="TTS audio file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
