import re
from collections import Counter
from soynlp.word import WordExtractor
from app.schemas.dto import WordDetail

class WordAnalyzer:
    def __init__(self):
        # 불용어 리스트 : 더 넣을거 있으면 노션에 추가하기
        self.stopwords = ["아니", "진짜", "오늘", "오키", "사랑", "요즘", "너무", "그냥", "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "이거", "내가", "있는", "하는", "근데", "이런", "저런"]
    
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
        all_sentences = []
        for sentences in raw_data_by_platform.values():
            for sentence in sentences:
                cleaned = self.clean_text(sentence)
                if cleaned:
                    all_sentences.append(cleaned)
        
        if not all_sentences:
            return []
        
        print(f"총 {len(all_sentences)}개의 문장에서 신조어 발굴 시작...")
        
        # soynlp 단어 추출기 시작 및 학습
        word_extractor = WordExtractor(min_frequency=2, min_cohesion_forward=0.05, min_right_branching_entropy=0.0)
        word_extractor.train(all_sentences)
        words = word_extractor.extract()
        
        # 필터링 작업, 점수 매기기
        analyzed_words = {}
        for word, score in words.items():
            if len(word) > 1 and word not in self.stopwords:
                final_score = int(score.cohesion_forward * 100)
                if final_score > 0:
                    analyzed_words[word] = final_score
        
        top_trendy_words = sorted(analyzed_words.keys(), key=lambda w: analyzed_words[w], reverse=True)[:30]
        
        final_words_list = []
        for word in top_trendy_words:
            word_to_examples = [] # 단어 별로 예시 문장 모아놓는 리스트 (유행어 별로 문장 선별하기 때문에 딕셔너리 -> 리스트로 변경)
            platform_counts = {}
            
            for platform, sentences in raw_data_by_platform.items():
                for sentence in sentences:
                    if word in sentence:
                        platform_counts[platform] = platform_counts.get(platform, 0) + 1
                        # 예시 문장은 최대 3개로 제한
                        if len(word_to_examples) < 3 and sentence not in word_to_examples:
                            word_to_examples.append(sentence)
            
            word_detail = WordDetail(
                    keyword=word,
                    platform_frequencies=platform_counts,
                    original_examples=word_to_examples
                )
            final_words_list.append(word_detail)
        
        print(f"데이터 1차 가공 : 상위 유행어 {len(final_words_list)}개 추출 완료")
        return final_words_list