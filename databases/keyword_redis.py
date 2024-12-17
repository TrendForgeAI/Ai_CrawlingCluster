import redis


world_keywords: list[str] = [
    'AI', 'LLM', 'GPT', 'Deep Learning', 'Machine Learning', 
    'Neural Networks', 'Natural Language Processing', 
    'Transformer', 'Reinforcement Learning', 'Generative AI', 
    'AI Ethics', 'AI Research', 
    'AutoML', 'Self-Supervised Learning', 'Zero-Shot Learning',
    'Few-Shot Learning', 'Fine-Tuning', 'AI Regulation', 'Responsible AI', 
    'AI Model Compression', 'Foundation Models', 'Large Scale AI', 'AI Scaling Laws',
    'Multimodal AI', 'AI Trends 2024', 'AGI', 'Artificial General Intelligence'
]

korea_keywords: list[str] = [
    "인공지능", "생성형 인공지능", "생성망 인공지능", "자연어 처리",
    "컴퓨터 비전", "지피티", "강화 학습", "딥러닝", "기계 학습", 
    "초거대 AI", "초거대 언어 모델", "인공지능 규제", "책임 있는 AI",
    "자동 머신러닝", "제로샷 학습", "퓨샷 학습", "파인튜닝", "기반 모델", 
    "다중모달 AI", "생성형 AI 윤리", "AI 트렌드 2024", "인공지능 연구"
]


redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
def store_keywords_to_redis(key: str, keywords: list[str]) -> None:
    """
    Args:
        key(str): Redis 키 이름 
        keywords(list): 저장할 키워드 리스트
    """    
    redis_client.delete(key)
    redis_client.rpush(key, *keywords)
    
store_keywords_to_redis("keywords:global", world_keywords)
store_keywords_to_redis("keywords:korea", korea_keywords)