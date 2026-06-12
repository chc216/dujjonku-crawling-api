from fastapi import FastAPI
import requests
from datetime import datetime
from app.schemas.dto import CrawlResult
from app.services.analyzer import WordAnalyzer
from app.services.crawler import CommunityCrawler

app = FastAPI(title="Trendy Word Crawling")
analyzer = WordAnalyzer()
crawler = CommunityCrawler()

SPRING_BOOT_URL = "http://localhost:8080/crawling"

# 전체 파이프라인을 돌리는 API
@app.get("/run-pipeline")
def run_pipeline():
    target_keyword = "유행어"
    
    # 나중에 keyword(수집을 위해 검색할 데이터)를 추가해야 할 듯. (크롤러 두 번 호출)
    tweets = crawler.collect_x_tweets(keyword=target_keyword, max_items=3000)
    naver_blogs = crawler.collect_naver_blog(keyword=target_keyword, max_items=3000)
    
    if not tweets and not naver_blogs:
        return {"status" : "error", "message" : "크롤링된 데이터 없음"}
    
    # analyzer.py에 전달할 구조 (데이터 두 개 묶어서 전달)
    raw_data_by_platform = {
        "twitter" : tweets,
        "naver_blog" : naver_blogs
    }
        
    analyzed_words = analyzer.analyze_keywords(raw_data_by_platform)
    
    # 스프링에게 전달할 구조
    spring_payload = []
    for word_data in analyzed_words:
        # 빈 배열이 중간에 섞여서 스프링 서버가 400을 뱉어냄 -> 빈배열 버리기
        if word_data.platform_frequencies and word_data.original_examples:
            spring_payload.append({
                "keyword": word_data.keyword,
                "platformFrequencies": word_data.platform_frequencies,
                "originalExamples": word_data.original_examples
            })
    
    try:
        # 스프링 서버 URL 넣고 나서 해당 라인 삭제
        if not SPRING_BOOT_URL:
            return {"status": "local_success", "message": "스프링 서버 URL 없음. 브라우저에만 출력.", "sent_data": spring_payload}
        
        response = requests.post(SPRING_BOOT_URL, json=spring_payload)
        return {
            "status": "success",
            "spring_response_code": response.status_code,
            "sent_data": spring_payload
        }
    
    except requests.exceptions.ConnectionError:
        return {"status": "local_success", "message": "스프링 서버가 꺼져있어 전송 생략", "sent_data": spring_payload}
    
# 테스트 API (디버깅)
@app.get("/test-crawl-x")
def test_crawl_x(keyword: str = "유행어"):
    tweets = crawler.collect_x_tweets(keyword=keyword, max_items=5)
    
    return {
        "status": "success",
        "search_keyword": keyword,
        "scraped_count": len(tweets),
        "results": tweets
    }
    
@app.get("/test-crawl-naver")
def test_crawl_naver(keyword: str = "유행어"):
    blogs = crawler.collect_naver_blog(keyword=keyword, max_items=5)
    
    return {
        "status": "success",
        "search_keyword": keyword,
        "scraped_count": len(blogs),
        "results": blogs
    }