import asyncio
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils import process_articles

# Setup logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Advanced News Summarization & Sentiment Analysis API",
    description="An advanced API that processes news articles, performs sentiment analysis, and generates a Hindi TTS audio report.",
    version="2.0.0"
)

# Enable CORS for all origins (customize as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this list to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a Pydantic model for the incoming request payload
class NewsRequest(BaseModel):
    company_name: str

# Health check endpoint
@app.get("/health", summary="Health Check Endpoint")
async def health_check():
    return {"status": "ok", "message": "Service is healthy."}

# Endpoint to process news articles and generate the sentiment report
@app.post("/api/process-news", summary="Process news articles and generate sentiment report")
async def process_news(request: NewsRequest):
    try:
        # Run the blocking process_articles function asynchronously
        articles, sentiment_counts, comparative_report, tts_file = await asyncio.to_thread(process_articles)
        response = {
            "company": request.company_name,
            "articles": articles,
            "sentiment_counts": sentiment_counts,
            "comparative_report": comparative_report,
            "tts_file": tts_file
        }
        return JSONResponse(content=response)
    except Exception as e:
        logger.exception("Error processing news articles")
        raise HTTPException(status_code=500, detail=f"Error processing news: {str(e)}")

# Endpoint to download the generated Hindi TTS audio file
@app.get("/api/tts", summary="Download the generated Hindi TTS audio file")
async def get_tts():
    tts_path = "sentiment_report_hi.mp3"
    if os.path.exists(tts_path):
        return FileResponse(
            path=tts_path,
            media_type="audio/mpeg",
            filename="sentiment_report_hi.mp3"
        )
    else:
        raise HTTPException(status_code=404, detail="TTS audio file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
