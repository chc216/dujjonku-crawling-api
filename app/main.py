from fastapi import FastAPI
import requests
from datetime import datetime
from app.schemas.dto import CrawlResult
from app.services.analyzer import WordAnalyzer
from app.services.crawler import CommunityCrawler

app = FastAPI(title="Trendy Word Crawling")
analyzer = WordAnalyzer()
crawler = CommunityCrawler()

SPRING_BOOT_URL = ""

# 전체 파이프라인을 돌리는 API
@app.get("/run-pipeline")
def run_pipeline():
    # 나중에 keyword(수집을 위해 검색할 데이터)를 추가해야 할 듯. (크롤러 두 번 호출)
    tweets = crawler.collect_x_tweets(keyword="진짜", max_items=100)
    
    if not tweets:
        return {"status" : "error", "message" : "크롤링된 데이터 없음"}
    
    raw_data_by_platform = {
        "twitter" : tweets
    }
        
    analyzed_words = analyzer.analyze_keywords(raw_data_by_platform)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    payload = CrawlResult(
        crawled_date=today_str,
        words=analyzed_words
    )
    
    try:
        # 스프링 서버 URL 넣고 나서 해당 라인 삭제
        if not SPRING_BOOT_URL:
            return {"status": "local_success", "message": "스프링 서버 URL 없음. 브라우저에만 출력.", "sent_data": payload}
        
        response = requests.post(SPRING_BOOT_URL, json=payload.model_dump())
        return {"status": "success", "spring_response_code": response.status_code, "sent_data": payload}
    
    except requests.exceptions.ConnectionError:
        return {"status": "local_success", "message": "스프링 서버가 꺼져있어 전송 생략", "sent_data": payload}
    
# 테스트 API (디버깅)
@app.get("/test-crawl")
def test_crawl(keyword: str = "두쫀쿠"):
    tweets = crawler.collect_x_tweets(keyword=keyword, max_items=100)
    
    return {
        "status": "success",
        "search_keyword": keyword,
        "scraped_count": len(tweets),
        "results": tweets
    }