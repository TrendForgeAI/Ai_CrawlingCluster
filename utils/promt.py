import os
import openai
from pathlib import Path
from typing import Any
from dotenv import load_dotenv


# 데이터 로드
key_path = Path(__file__).parent.parent / "configs/.env"
load_dotenv(key_path)

openai.api_key = os.getenv("API_KEY")


def llm_weighted_evaluation(text: str, source: str, date: str, signature_keywords: list) -> str:
    """
    LLM에게 문서 가치를 평가하도록 요청.
    Args:
        text (str): 문서 본문
        source (str): 문서 출처
        date (str): 문서 작성 날짜
        signature_keywords (list): 시그니처 키워드 리스트
    Returns:
        str: LLM 평가 결과 (JSON 형식)
    """
    
    prompt = f"""
    다음은 뉴스 기사 문서입니다:
    출처: {source}
    날짜: {date}
    본문: "{text}"

    시그니처 키워드 목록: {', '.join(signature_keywords)}

    이 문서를 다음 기준으로 평가해주세요:
    1. 시그니처 키워드의 중요도 (0~5점)
    2. 문서가 최신 AI 트렌드와 얼마나 관련이 있는지 (0~5점)
    3. 출처의 신뢰도 점수 (0~5점)
    4. 종합 점수 (0~100점): 위 기준을 종합해서 부여

    출력 형식 (JSON):
    {{
        "키워드 중요도": [점수],
        "AI 트렌드 관련도": [점수],
        "출처 신뢰도": [점수],
        "종합 점수": [점수]
    }}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4o",  # 사용하려는 모델
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes data."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )
            
    return response.choices[0].message.content.strip()


