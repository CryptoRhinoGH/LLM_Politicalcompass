from dataclasses import dataclass
from typing import List

@dataclass
class BrowserSessionResult:
    visited_urls: List[str]
    ip_address: str
    profile_dir: str
    session_dir: str
    persona_label: str
    city_name: str
