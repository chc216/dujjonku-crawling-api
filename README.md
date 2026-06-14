# 🍪 두쫀쿠 (Dujjonku) - Crawler & AI Pipeline

> **숨어있는 진짜 유행어를 발굴하는 자동화 파이프라인**<br/>
> 세대 간 언어 장벽을 허물기 위한 유행어 사전 서비스 '두쫀쿠'의 실시간 SNS 데이터 크롤링 및 형태소 분석(AI) 레포지토리입니다.

---

⚡ 실행 순서 요약 (Quick Start)
처음 세팅하시는 분은 아래 순서대로 진행하면 됩니다.

1. **사전 준비** — Python 3.9 이상 설치, 백엔드 서버(Spring Boot) 구동 확인
2. **레포지토리 클론** — `git clone` 후 프로젝트 폴더로 이동
3. **가상환경 세팅** — `python -m venv venv` 및 활성화 (`source venv/bin/activate`)
4. **패키지 설치** — `pip install -r requirements.txt`
5. **.env 파일 생성** — 최상단에 `APIFY_TOKEN` 설정 (Apify 홈페이지 발급)
6. **파이썬 서버 실행** — `uvicorn app.main:app --reload`
7. **파이프라인 가동** — 브라우저에서 `http://localhost:8000/run-pipeline` 접속

💡 각 단계의 상세 내용은 아래 섹션을 참고하세요.

---

## 사전 준비 사항 (Prerequisites)

로컬에서 서버를 실행하기 전에 아래 항목이 준비되어 있어야 합니다.

* **Python 3.9 이상** : 패키지 호환성 및 비동기(FastAPI) 처리를 위해 필요합니다.
* **Spring Boot 백엔드 서버** : 분석된 데이터를 최종 적재할 메인 서버(`localhost:8080`)가 반드시 실행되어 있어야 합니다.

> ⚠️ 백엔드 서버가 켜져 있지 않으면, 크롤링 및 분석이 완료되더라도 최종 데이터 전송(POST) 단계에서 에러가 발생합니다.

---

## 환경 변수(.env) 설정

프로젝트 최상단 경로에 `.env` 파일을 생성하고 아래 내용을 입력합니다.

**🔑 Apify API 토큰 발급 방법:**

1. [Apify 공식 홈페이지](https://apify.com/) 접속 및 로그인
2. 좌측 하단 **[Settings]** ➜ 상단 **[Integrations]** 탭 클릭
3. **Personal API token** 값을 복사하여 아래에 붙여넣기

```
APIFY_TOKEN={Apify 홈페이지에서 발급받은 개인 토큰 작성}

```

> 💡 **VS Code 사용자 필수 설정:**
> VS Code 터미널에서 `.env` 파일을 자동으로 읽지 못할 경우, 설정(`Cmd + ,`)에서 `python.terminal.useEnvFile`을 검색하여 **체크(Enable)** 처리 후 터미널을 재시작해 주세요.

---

## 로컬 서버 실행 방법 (How to Run)

### 1. 레포지토리 클론 및 폴더 이동

```bash
git clone https://github.com/chc216/dujjonku-crawling-api.git

cd dujjonku-crawling-api

```

### 2. 가상환경(venv) 생성 및 패키지 설치

파이썬 패키지 충돌을 방지하기 위해 가상환경을 생성하고 의존성을 설치합니다.

```bash
python -m venv venv

# Mac/Linux 기준 가상환경 활성화
source venv/bin/activate
# Windows 기준: .\venv\Scripts\activate

pip install -r requirements.txt

```

### 3. 파이썬 크롤링 서버 실행

```bash
uvicorn app.main:app --reload

```

서버는 기본적으로 http://localhost:8000 포트에서 실행됩니다.

## 파이프라인 가동 및 주의사항 안내

본 파이썬 서버는 프론트엔드/백엔드의 서비스 운영을 위해 실시간 트위터 데이터를 수집하고, `soynlp`를 통해 유행어 후보를 추출한 뒤 AI(Gemini) 분석을 거쳐 메인 DB에 데이터를 주입합니다.

로컬 환경에서 전체 파이프라인을 가동하려면, 웹 브라우저 주소창에 `http://localhost:8000/run-pipeline`을 입력하여 수동으로 트리거해 주시기 바랍니다.

> 💡 **참고 (빠른 테스트 방법):**  수천 개의 데이터를 크롤링할 경우 10분 이상 소요될 수 있습니다. 전체 로직이 정상 작동하는지 빠르게 확인하고 싶다면, `app/main.py` 파일 내의 `target_keyword`값을 **“유행어”**로 수정하고,  `max_items` 값을 5000에서 **50~100** 정도로 임의 수정하여 실행해 보세요.

**1. 안정적인 네트워크 환경 필수 (크롤링 강제 종료 위험)**
대규모 데이터 크롤링 시 Apify 서버와 지속적으로 상태 확인 통신을 진행합니다. 작업 도중 **노트북 덮개를 닫거나 와이파이 연결이 끊어지면 네트워크 에러로 인해 크롤링이 강제 중단**됩니다. 반드시 안정적인 환경에서 진행해 주세요.

**2. 브라우저 무한 로딩 (데이터 분할 전송 대기 현상)**
수집된 데이터를 백엔드로 보낼 때, 메인 서버의 AI API 토큰 한도 초과(429 Quota Exceeded)를 막기 위해 데이터를 500개씩 묶어 보내고 **60초 대기**하는 분할 전송(Throttling) 로직이 작동합니다.

* **브라우저 화면이 하얗게 멈춰도 정상입니다.** 응답을 기다리던 브라우저가 타임아웃 될 수 있습니다.
* 브라우저를 닫아도 파이썬 터미널 창(백그라운드)에서는 분할 전송이 계속 진행 중이므로, 강제 종료하지 말고 터미널 로그를 끝까지 확인해 주세요.