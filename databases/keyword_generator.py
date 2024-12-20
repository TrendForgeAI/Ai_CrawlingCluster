from pathlib import Path
from dataclasses import dataclass, asdict
import itertools
import yaml


@dataclass(frozen=True)
class CrawlingCustomSearchTemplate:
    """템플릿 데이터를 관리하는 클래스."""

    core_keywords: list[str]
    context_keywords: list[str]
    templates: list[str]

    def generate_search_queries(self) -> list[tuple[str, str]]:
        """
        키워드 조합 생성
        """
        return list(itertools.product(self.core_keywords, self.context_keywords))

    def apply_question_templates(self, queries: list[tuple[str, str]]) -> set[str]:
        """
        질문 템플릿 적용
        """
        questions = []
        for template in self.templates:
            questions.extend(
                [template.format(core, context) for core, context in queries]
            )
        return set(questions)


def load_keyword_from_yaml() -> dict[str, CrawlingCustomSearchTemplate]:
    """
    YAML 파일에서 국가별 데이터를 로드하고 BaseCountry 객체 생성
    Args:
        yaml_path (str): YAML 파일 경로
    Returns:
        Dict[str, CrawlingCustomSearchTemplate]: 검색어 질의 템플릿
    """
    keyword_yaml_path = Path(__file__).parent.parent / "configs/cy/keyword.yaml"
    with open(keyword_yaml_path, "r", encoding="utf-8") as file:
        data: dict = yaml.safe_load(file)

    template = CrawlingCustomSearchTemplate(
        core_keywords=data["keywords"]["core_keywords"],
        context_keywords=data["keywords"]["context_keywords"],
        templates=data["keywords"]["templates"],
    )

    return asdict(template)
