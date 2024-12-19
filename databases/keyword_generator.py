from pathlib import Path
import itertools
import yaml

class BaseCountry:
    """
    국가별 키워드 및 템플릿 데이터를 관리하는 클래스.
    """
    def __init__(self, name: str, core_keywords: list[str], context_keywords: list[str], templates: list[str]):
        self.name = name
        self.core_keywords = core_keywords
        self.context_keywords = context_keywords
        self.templates = templates

    def generate_search_queries(self) -> list[tuple[str, str]]:
        """
        키워드 조합 생성
        """
        return list(itertools.product(self.core_keywords, self.context_keywords))

    def apply_question_templates(self, queries: list[tuple[str, str]]) -> list[str]:
        """
        질문 템플릿 적용
        """
        questions = []
        for template in self.templates:
            questions.extend([template.format(core, context) for core, context in queries])
        return questions



def load_countries_from_yaml() -> dict[str, BaseCountry]:
    """
    YAML 파일에서 국가별 데이터를 로드하고 BaseCountry 객체 생성
    Args:
        yaml_path (str): YAML 파일 경로
    Returns:
        Dict[str, BaseCountry]: 국가 이름을 키로 하는 BaseCountry 객체 딕셔너리
    """
    keyword_yaml_path = Path(__file__).parent.parent / "configs/cy/keyword.yaml"
    with open(keyword_yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    
    countries = {}
    for country_code, country_data in data["countries"].items():
        countries[country_code] = BaseCountry(
            name=country_code,
            core_keywords=country_data["core_keywords"],
            context_keywords=country_data["context_keywords"],
            templates=country_data["templates"]
        )
    return countries