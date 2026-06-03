import schedule
import time
from datetime import datetime
from app.main import run_pipeline

def run_daily_job():
    print(f"\n[{datetime.now()}] 데이터 크롤링 및 분석 파이프라인 가동")
    
    try:
        result = run_pipeline()
        
        status = result.get("status", "unknown")
        print(f"[{datetime.now()}] 실행 완료. 결과 상태: {status}")
        
    except Exception as e:
        print(f"[{datetime.now()}] 파이프라인 실행 중 에러 발생: {e}")

schedule.every().day.at("02:00").do(run_daily_job)

print("파이썬 크롤러 스케줄러 상태: 대기 중")

# Polling 방식으로 주기적으로 상태 체크 (sleep(1))
while True:
    schedule.run_pending()
    time.sleep(1)