from pydantic import BaseModel
from typing import List, Dict

class WordDetail(BaseModel):
    keyword: str
    platform_frequencies: Dict[str, int]
    original_examples: List[str]
    
class CrawlResult(BaseModel):
    crawled_date: str
    words: List[WordDetail]