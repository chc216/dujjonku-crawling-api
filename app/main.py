from fastapi import FastAPI
import requests
from datetime import datetime
from app.schemas.dto import CrawlResult
from app.services.analyzer import WordAnalyzer
from app.services.crawler import CommunityCrawler
import time

app = FastAPI(title="Trendy Word Crawling")
analyzer = WordAnalyzer()
crawler = CommunityCrawler()

SPRING_BOOT_URL = "http://localhost:8080/crawling"

# 전체 파이프라인을 돌리는 API
@app.get("/run-pipeline")
def run_pipeline():
    target_keyword = "유행어"
    
    # 나중에 keyword(수집을 위해 검색할 데이터)를 추가해야 할 듯. (크롤러 두 번 호출)
    tweets = crawler.collect_x_tweets(keyword=target_keyword, max_items=200)
    naver_blogs = crawler.collect_naver_blog(keyword=target_keyword, max_items=200)
    
    if not tweets:# and not naver_blogs:
        return {"status" : "error", "message" : "크롤링된 데이터 없음"}
    
    # analyzer.py에 전달할 구조 (데이터 두 개 묶어서 전달)
    raw_data_by_platform = {
        "twitter" : tweets,
        "naver_blog" : naver_blogs
    }
    print(f"🚀 [디버깅] 크롤러 봇이 찾은 유행어 후보 개수: {len(tweets)}개")    
    analyzed_words = analyzer.analyze_keywords(raw_data_by_platform)
    print(f"🚀 [디버깅] 분석기가 찾은 유행어 후보 개수: {len(analyzed_words)}개")
    
    # 스프링에게 전달할 구조
    spring_payload = []
    for word_data in analyzed_words:
        # 빈 배열이 중간에 섞여서 스프링 서버가 400을 뱉어냄 -> 빈배열 버리기
        if word_data.platform_frequencies and word_data.original_examples:
            
            # 예시 문장 중 첫 번째 예시 문장만 가져와서 최대 200자까지만 자르기 (데이터 양 너무 많아서 DB에 안들어가는 문제)
            safe_example = word_data.original_examples[0][:200]
            
            spring_payload.append({
                "keyword": word_data.keyword,
                "platformFrequencies": word_data.platform_frequencies,
                "originalExamples": [safe_example]
            })
    print(f"🚀 [디버깅] 스프링으로 쏠 최종 데이터 개수: {len(spring_payload)}개")
    
    if not SPRING_BOOT_URL:
        return {"status": "local_success", "message": "스프링 서버 URL 없음. 브라우저에만 출력.", "sent_data": spring_payload}
        
    CHUNK_SIZE = 500
    total_sent = 0
    
    for i in range(0, len(spring_payload), CHUNK_SIZE):
        chunk = spring_payload[i : i + CHUNK_SIZE]
        
        try:
            print(f"[{i+1} ~ {i+len(chunk)}] 번째 데이터 전송 중...")
            response = requests.post(SPRING_BOOT_URL, json=chunk)
            print(f"전송 완료. (스프링 응답 코드 : {response.status_code})")
            total_sent += len(chunk)
        
        except requests.exceptions.ConnectionError:
            print("스프링 서버가 꺼져있어 전송 중단")
            break
        
        if i+CHUNK_SIZE < len(spring_payload):
            print("제미나이 API 한도 보호 : 60초 대기 중... \n")
            time.sleep(60)
            
    return {
        "status": "success",
        "message": f"총 {total_sent}개 데이터 분할 전송 완료",
        "total_sent": total_sent
    }
        
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