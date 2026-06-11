import requests
import os
from dotenv import load_dotenv

# .env 파일 읽어오기
load_dotenv()

class CommunityCrawler:
    def __init__(self):
        # 내가 apify 회원가입해서 받은 토큰임 (개인 API 토큰)
        # 수정 : os.getenv()를 통해 .env에서 토큰 값 가져옴 (.env 파일은 깃허브 대신 로컬에서 따로 관리)
        self.api_token = os.getenv("APIFY_TOKEN")
        
        if not self.api_token:
            print("APIFY_TOKEN 찾을 수 없음. .env 파일 확인 바람")
        
        # apify에서 actor로 제공받은 Scrapper 봇의 주소 (추가하려면 밑에 더 추가 가능 but, 함수는 주소마다 생성해야함)
        self.x_bot_url = f"https://api.apify.com/v2/actors/kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest/run-sync-get-dataset-items?token={self.api_token}"
        
        self.naver_bot_url = f"https://api.apify.com/v2/actors/oxygenated_quagmire~naver-blog-search/run-sync-get-dataset-items?token={self.api_token}"
        
    def collect_x_tweets(self, keyword: str, max_items: int=100) -> list:        
        print(f"[{keyword}] 트윗 {max_items}개 수집 시작...")
        
        # 해당 봇의 날짜 설정 방법
        # 끝나는 날짜 설정은
        # f"{keyword} since: 3030-30-30 until:3030-00-00"
        #search_query = f"{keyword} since: 2026-06-07"
        
        # 봇에게 요청할 입력값
        payload = {
            #"searchTerms": [search_query],
            "searchTerms": [keyword],
            "maxItems": max_items,
            "sort": "Latest",
            "tweetLanguage": "ko"
        }
        
        # 웹페이지 요청(POST)
        response = requests.post(self.x_bot_url, json=payload)
        
        # 결과 담을 리스트
        scraped_texts = []

        if response.status_code in [200,201]:
            # 봇에게 요청한 데이터 돌려받기
            dataset_items = response.json()
            
            print(f"========================")
            print(f"Debugging : 봇이 준 첫 번째 데이터 샘플 : {dataset_items[0] if dataset_items else '데이터 없음'}")
            print(f"========================")
            
            for item in dataset_items:
                # x에서 데이터를 제공하는 방식 "text"
                text = item.get("text") or item.get("full_text", "")
                
                if text:
                    clean_text = text.replace('\n', ' ').strip()
                    scraped_texts.append(clean_text)    
                            
            print(f"트위터에서 텍스트 가져오기 성공. 가져온 텍스트 개수: {len(scraped_texts)}")
            return scraped_texts
            
        else:
            print(f"error: Apify 요청 실패. {response.status_code} - {response.text}")
            return []
        
    def collect_naver_blog(self, keyword: str, max_items: int=100) -> list:
        print(f"[{keyword}] 네이버 블로그 {max_items}개 수집 시작...")
                
        # 봇에게 요청할 입력값
        payload = {
            "queries": [keyword],
            "maxResults": max_items,
            "includeFullContent": False,
            "sortBy": "date"
        }
        
        # 웹페이지 요청(POST)
        response = requests.post(self.naver_bot_url, json=payload)
        
        # 결과 담을 리스트
        scraped_texts = []

        if response.status_code in [200,201]:
            # 봇에게 요청한 데이터 돌려받기
            dataset_items = response.json()
            
            print(f"========================")
            print(f"Debugging : 봇이 준 첫 번째 데이터 샘플 : {dataset_items[0] if dataset_items else '데이터 없음'}")
            print(f"========================")
            
            for item in dataset_items:
                # fullContent로 데이터 긁어왔더니 쓰레기 값들이 너무 많이 들어와서 제목이랑 요약문 데이터만 가져오는 방식으로 변경
                title = item.get("title", "")
                desc = item.get("ogDescription", "")
                text = f"{title} {desc}"
                
                if text.strip():
                    clean_text = text.replace('\n', ' ').strip()
                    scraped_texts.append(clean_text)    
                            
            print(f"네이버 블로그에서 텍스트 가져오기 성공. 가져온 텍스트 개수: {len(scraped_texts)}")
            return scraped_texts
            
        else:
            print(f"error: Apify 요청 실패. {response.status_code} - {response.text}")
            return []