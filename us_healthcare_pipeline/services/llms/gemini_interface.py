import time
import platform
import pyperclip as pc
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)

from us_healthcare_pipeline.services.llms.llm_interface import LLMInterface
from us_healthcare_pipeline.models.llm_response import LLMResponse


class GeminiInterface(LLMInterface):
    def __init__(self):
        super().__init__()
        self.cmd_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

    def ask_question(self, browser, question: str, question_id: int, tries: int = 0) -> str:
        try:
            self._navigate_to_chat(browser)
            input_field = self._wait_for_input_field(browser)
            if not input_field:
                raise Exception("Could not locate Gemini input field.")
            self._send_clipboard_message(input_field, question)
            return self._get_response(browser)
        except Exception as e:
            if tries < 2:
                print(f"[!] Retry {tries + 1} sending question due to: {e}")
                time.sleep(1)
                return self.ask_question(browser, question, question_id, tries + 1)
            print(f"[!] Failed to send question after retries: {e}")
            return ""

    def ask_questions(self, browser, questions: List[dict]) -> List[LLMResponse]:
        browser.get("https://gemini.google.com/app")
        try:
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(5)
        except TimeoutException:
            print("[!] Timeout while loading Gemini.")
            return []

        responses = []
        for q in questions:
            answer = self.ask_question(browser, q["full_prompt"], q["id"])
            responses.append(LLMResponse(id=q["id"], question=q["question"], answer=answer))
        return responses

    def _navigate_to_chat(self, browser):
        try:
            browser.get("https://gemini.google.com/app")
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
        except TimeoutException:
            print("[!] Timeout while loading Gemini.")

    def _wait_for_input_field(self, browser):
        try:
            return WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "rich-textarea div[contenteditable='true']"))
            )
        except TimeoutException:
            print("[!] Gemini input field not found.")
            return None

    def _send_clipboard_message(self, input_field, message):
        input_field.click()
        time.sleep(0.3)
        input_field.send_keys(self.cmd_key, "a")
        input_field.send_keys(Keys.DELETE)
        pc.copy(message)
        input_field.send_keys(self.cmd_key, "v")
        time.sleep(0.4)
        input_field.send_keys(Keys.ENTER)

    def _get_response(self, browser, tries=0, max_tries=5) -> str:
        try:
            WebDriverWait(browser, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.send-button-container.disabled"))
            )
            conversation_containers = WebDriverWait(browser, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.conversation-container"))
            )
            latest = conversation_containers[-1]
            response_el = latest.find_element(By.CSS_SELECTOR, "model-response .model-response-text")
            response_text = response_el.text.strip()

            if response_text:
                return response_text
            elif tries < max_tries:
                time.sleep(1.5)
                return self._get_response(browser, tries + 1)
            else:
                print("[!] Response retry limit reached.")
                return ""
        except Exception as e:
            print(f"[!] Failed to get Gemini response: {e}")
            try:
                browser.refresh()
            except:
                pass
            if tries < max_tries:
                time.sleep(2)
                return self._get_response(browser, tries + 1)
            return ""