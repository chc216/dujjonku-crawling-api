import re
from collections import Counter
from app.schemas.dto import WordDetail

class WordAnalyzer:
    def clean_text(self, text: str) -> str:
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
        return text.strip()
    
    def analyze_keywords(self, raw_data_by_platform: dict) -> list:
        """
        여기에 raw_data_by_platform 해야됨
            {
                "플랫폼" : ["예시"]
            }
        """
        all_words = []
        word_to_examples = {} # 단어 별로 예시 문장 모아놓는 딕셔너리
        word_platform_counts = {} # 단어 별로 플랫폼 빈도수 세는 딕셔너리
        
        for platform, sentences in raw_data_by_platform.items():
            for sentence in sentences:
                cleaned = self.clean_text(sentence)
                if not cleaned:
                    continue
                
                """ 여기에 soynlp 토크나이저 사용 """
                tokens = cleaned.split() # 임시임 (token 분류 기준 : 띄어쓰기)
                
                for token in tokens:
                    if len(token) < 2: # 한 글자 제외
                        continue
                    
                    all_words.append(token)
                    
                    if token not in word_to_examples:
                        word_to_examples[token] = []
                    if sentence not in word_to_examples[token] and len(word_to_examples[token]) < 3: # 예시 문장 3개 제한 뒀음
                        word_to_examples[token].append(sentence)
                        
                    if token not in word_platform_counts:
                        word_platform_counts[token] = {}
                    word_platform_counts[token][platform] = word_platform_counts[token].get(platform, 0)+1
                    
        # 많이 사용된 단어들 추출
        total_counter = Counter(all_words)
        final_words_list = []
        
        for word, _ in total_counter.most_common():
            if word in ["아니", "진짜"]: # 불용어 추가해야댐 (노션에 정리)
                continue
            
            word_detail = WordDetail(
                keyword=word,
                platform_frequencies=word_platform_counts[word],
                original_examples=word_to_examples[word]
            )
            final_words_list.append(word_detail)
            
            if len(final_words_list) == 30:
                break
        
        return final_words_list