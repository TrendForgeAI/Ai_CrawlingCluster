from databases.keyword_generator import BaseCountry, load_countries_from_yaml


def generate_questions_for_country(country: BaseCountry) -> None:
    """
    특정 국가에 대한 질문 생성 및 출력
    """
    queries = country.generate_search_queries()
    questions = country.apply_question_templates(queries)

    return questions


# 실행
countries: dict[str, BaseCountry] = load_countries_from_yaml()

# 대한민국 질문 생성
korea = generate_questions_for_country(countries["KR"])

# 미국 질문 생성
us = generate_questions_for_country(countries["US"])

print(korea)
