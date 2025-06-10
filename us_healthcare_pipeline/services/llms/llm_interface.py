# us_healthcare_pipeline/services/llms/llm_interface.py

from abc import ABC, abstractmethod
from typing import List
from selenium.webdriver.chrome.webdriver import WebDriver
from us_healthcare_pipeline.models.llm_response import LLMResponse

class LLMInterface(ABC):
    @abstractmethod
    def ask_question(self, browser: WebDriver, question: str, question_id: int) -> str:
        """Ask a question via browser and return the answer."""
        pass

    def ask_questions(self, browser: WebDriver, questions: List[dict]) -> List[LLMResponse]:
        """Ask multiple questions, returning a list of LLMResponse objects."""
        responses = []
        for q in questions:
            answer = self.ask_question(browser, q["full_prompt"], q["id"])
            responses.append(LLMResponse(id=q["id"], question=q["question"], answer=answer))
        return responses