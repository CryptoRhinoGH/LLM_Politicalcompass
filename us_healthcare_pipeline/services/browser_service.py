import json
import os
import time
import random
from typing import List, Tuple

import undetected_chromedriver as uc

from us_healthcare_pipeline.models.browser_session_result import BrowserSessionResult
from us_healthcare_pipeline.models.session_metadata import SessionMetadata
from us_healthcare_pipeline.models.persona import Persona
from us_healthcare_pipeline.services.proxy_service import ProxyService
from us_healthcare_pipeline.models.llm_response import LLMResponse
from us_healthcare_pipeline.services.llms.llm_interface import LLMInterface


class BrowserService:
    def __init__(
        self,
        proxy_service: ProxyService,
        persona: Persona,
        city_name: str,
        base_results_dir: str = "results"
    ):
        self.proxy_service = proxy_service
        self.persona = persona
        self.city_name = city_name.lower().replace(" ", "_")
        self.session_id = proxy_service.session_id
        self.base_results_dir = base_results_dir

        self.session_dir = os.path.join(base_results_dir, self.city_name, persona.label)
        self.profile_dir = os.path.join(self.session_dir, "profile")
        os.makedirs(self.profile_dir, exist_ok=True)

        self.visited_urls: List[str] = []
        self.browser = None  # Persistent browser instance

    def _init_browser(self):
        proxy_extension = self.proxy_service.create_proxy_extension()
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={os.path.abspath(self.profile_dir)}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_extension(proxy_extension)

        self.browser = uc.Chrome(
            options=options,
            headless=False,
            service_log_path=os.path.join(self.session_dir, "chrome.log")
        )

    def run_full_session(self, llm: LLMInterface, questions: List[str]) -> Tuple[BrowserSessionResult, List[LLMResponse]]:
        self._init_browser()
        ip = self._get_ip_via_browser(self.browser)

        try:
            # Browsing phase
            for query in self.persona.search_queries:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                self._visit_url(self.browser, url, wait_range=(3, 6))

            for site in self.persona.news_sites:
                self._visit_url(self.browser, site, wait_range=(5, 10))

            # LLM interaction phase
            responses = llm.ask_questions(self.browser, questions)
            self._write_llm_responses(responses)

        finally:
            if self.browser:
                self.browser.quit()

        # Metadata recording
        cookie_path = os.path.join(self.profile_dir, "Default", "Cookies")
        cookies_present = os.path.exists(cookie_path) and os.path.getsize(cookie_path) > 0

        metadata = SessionMetadata.from_browser_session(
            result=BrowserSessionResult(
                visited_urls=self.visited_urls,
                ip_address=ip,
                profile_dir=self.profile_dir,
                session_dir=self.session_dir,
                persona_label=self.persona.label,
                city_name=self.city_name
            ),
            timestamp=time.strftime("%Y-%m-%d_%H-%M-%S"),
            session_id=self.session_id,
            cookies_present=cookies_present,
            status="success"
        )

        meta_path = os.path.join(self.session_dir, "..", "session_meta.json")
        metadata.to_json(os.path.abspath(meta_path))

        return metadata.to_browser_session_result(), responses

    def _get_ip_via_browser(self, browser):
        try:
            browser.get("https://api.ipify.org")
            ip = browser.find_element("tag name", "body").text.strip()
            return ip
        except Exception as e:
            print(f"[!] Could not fetch IP in browser: {e}")
            return "unknown"

    def _visit_url(self, browser, url: str, wait_range=(3, 7)):
        try:
            browser.get(url)
            self.visited_urls.append(url)
            time.sleep(random.uniform(*wait_range))
        except Exception as e:
            print(f"[!] Failed to visit {url}: {e}")

    def _write_llm_responses(self, responses: List[LLMResponse]):
        output_path = os.path.join(self.session_dir, "llm_responses.json")
        with open(output_path, "w") as f:
            json.dump([r.to_dict() for r in responses], f, indent=2)