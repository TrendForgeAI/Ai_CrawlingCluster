from databases.keyword_generator import BaseCountry, load_countries_from_yaml


def generate_questions_for_country(country: BaseCountry) -> None:
    """
    특정 국가에 대한 질문 생성 및 출력
    """
    print(f"🌍 {country.name} 질문 생성:")
    queries = country.generate_search_queries()
    questions = country.apply_question_templates(queries)
    for question in questions[:5]:
        print(f"- {question}")
    print("\n")


# 실행
countries = load_countries_from_yaml()

# 대한민국 질문 생성
generate_questions_for_country(countries["KR"])

# 미국 질문 생성
generate_questions_for_country(countries["US"])