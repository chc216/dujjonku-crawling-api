from fastapi import FastAPI
import requests
from datetime import datetime
from app.schemas.dto import CrawlResult
from app.services.analyzer import WordAnalyzer

app = FastAPI(title="Trendy Word Crawling")
analyzer = WordAnalyzer()

SPRING_BOOT_URL = ""

@app.get("/test-run")
def test_run():
    mock_scraped_data = {
        
    }
    
    analyzed_words = analyzer.analyze_keywords(mock_scraped_data)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    payload = CrawlResult(
        crawled_date=today_str,
        words=analyzed_words
    )
    
    try:
        response = requests.post(SPRING_BOOT_URL, json=payload.model_dump())
        return {"status": "success", "spring_response_code": response.status_code, "sent_data": payload}
    except requests.exceptions.ConnectionError:
        return {"status": "local_success", "message": "스프링 서버가 꺼져있어 전송 생략", "sent_data": payload}