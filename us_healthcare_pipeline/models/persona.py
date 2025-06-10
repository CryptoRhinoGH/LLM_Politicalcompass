from dataclasses import dataclass
from typing import List

@dataclass
class Persona:
    label: str
    search_queries: List[str]
    news_sites: List[str]
