import requests
import bs4

# 웹페이지 요청
url = ""
response = requests.get(url)

if response.status_code== 200:
    # BeautifulSoup 객체 생성 (가져온 소스를 html 형식으로 정리)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    # 검색하고 싶은 내용 find_all로 찾기 (tag는 bs4의 클래스 객체 타입)
    tag = soup.find_all("")
    
    target = str(tag[1])
    target = target.replace('tag내용','')
    target = target.replace('tag내용','')
    target = target.replace('tag내용','')
    
    
    
    for title in titles:
        print(title.select_one('span.news_txt').get_text())
        
else:
    print('error')