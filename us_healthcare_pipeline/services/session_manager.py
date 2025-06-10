import os
import uuid
from typing import List, Tuple

from us_healthcare_pipeline.services.proxy_service import ProxyService
from us_healthcare_pipeline.services.browser_service import BrowserService, BrowserSessionResult
from us_healthcare_pipeline.services.persona_loader import PersonaLoader
from us_healthcare_pipeline.models.city_proxy_list import CityProxyList
from us_healthcare_pipeline.services.llms.llm_interface import LLMInterface
from us_healthcare_pipeline.models.llm_response import LLMResponse

class SessionManager:
    def __init__(self, city_name: str, persona_label: str, base_results_dir: str):
        self.city_name = city_name
        self.persona_label = persona_label
        self.session_id = str(uuid.uuid4())
        self.base_results_dir = base_results_dir

        self.persona = PersonaLoader.load_persona(self.persona_label)
        self.city = CityProxyList().get_by_name(self.city_name)

        self.proxy_service = ProxyService(city=self.city, session_id=self.session_id)

        self.browser_service = BrowserService(
            proxy_service=self.proxy_service,
            persona=self.persona,
            city_name=self.city_name,
            base_results_dir=self.base_results_dir
        )

    def run_session(self, llm: LLMInterface, questions: List[dict]) -> Tuple[BrowserSessionResult, List[LLMResponse]]:
        return self.browser_service.run_full_session(llm, questions)
