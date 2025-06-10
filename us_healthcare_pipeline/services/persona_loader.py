from typing import List
from us_healthcare_pipeline.models.persona import Persona
from us_healthcare_pipeline.config.persona_queries import persona_search_queries
from us_healthcare_pipeline.config.persona_sites import persona_news_sites

class PersonaLoader:
    @staticmethod
    def load_persona(label: str) -> Persona:
        queries = PersonaLoader._get_queries(label)
        sites = PersonaLoader._get_sites(label)
        return Persona(label=label, search_queries=queries, news_sites=sites)

    @staticmethod
    def _get_queries(label: str) -> List[str]:
        for entry in persona_search_queries:
            if entry["persona"] == label:
                return entry["search_queries"]
        raise ValueError(f"No queries found for persona: {label}")

    @staticmethod
    def _get_sites(label: str) -> List[str]:
        for entry in persona_news_sites:
            if entry["persona"] == label:
                return entry["news_sites"]
        raise ValueError(f"No news sites found for persona: {label}")