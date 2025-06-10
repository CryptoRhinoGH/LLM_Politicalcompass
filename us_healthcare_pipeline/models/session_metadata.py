from dataclasses import dataclass, asdict
from us_healthcare_pipeline.models.browser_session_result import BrowserSessionResult
from typing import List, Optional
import json
import os


@dataclass
class ChromeProfileQuality:
    cookies_present: bool


@dataclass
class SessionMetadata:
    timestamp: str
    city: str
    persona: str
    session_id: str
    ip_address: str
    visited_urls: List[str]
    status: str
    chrome_profile_quality: ChromeProfileQuality
    failure_reason: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def to_json(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def from_browser_session(result, timestamp: str, session_id: str, cookies_present: bool, status: str = "success", failure_reason: Optional[str] = None):
        return SessionMetadata(
            timestamp=timestamp,
            city=result.city_name,
            persona=result.persona_label,
            session_id=session_id,
            ip_address=result.ip_address,
            visited_urls=result.visited_urls,
            status=status,
            chrome_profile_quality=ChromeProfileQuality(cookies_present=cookies_present),
            failure_reason=failure_reason
        )
    
    def to_browser_session_result(self, base_results_dir: str = "results") -> BrowserSessionResult:
        session_dir = os.path.join(base_results_dir, self.city, self.persona)
        profile_dir = os.path.join(session_dir, "profile")
        return BrowserSessionResult(
            visited_urls=self.visited_urls,
            ip_address=self.ip_address,
            profile_dir=profile_dir,
            session_dir=session_dir,
            persona_label=self.persona,
            city_name=self.city
        )