import time
import platform
import pyperclip as pc
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from us_healthcare_pipeline.services.llms.llm_interface import LLMInterface
from us_healthcare_pipeline.models.llm_response import LLMResponse


class PerplexityInterface(LLMInterface):
    def __init__(self):
        super().__init__()
        self.cmd_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        self.first_message_sent = False

    def ask_question(self, browser, question: str, question_id: int, tries: int = 0) -> str:
        try:
            if not self.first_message_sent:
                self._send_first_message(browser)

            input_field = self._wait_for_input_field(browser)
            if not input_field:
                raise Exception("Could not locate Perplexity input field.")

            self._send_clipboard_message(browser, input_field, question)
            return self._get_response(browser)

        except Exception as e:
            if tries < 2:
                print(f"[!] Retry {tries + 1} sending question due to: {e}")
                time.sleep(1)
                return self.ask_question(browser, question, question_id, tries + 1)
            print(f"[!] Failed to send question after retries: {e}")
            return ""

    def ask_questions(self, browser, questions: List[dict]) -> List[LLMResponse]:
        try:
            if not browser.window_handles:
                raise Exception("[!] Browser window is closed.")
            browser.get("https://www.perplexity.ai/")
            time.sleep(5)
        except Exception as e:
            print(f"[!] Could not load Perplexity.ai: {e}")
            return []

        self._dismiss_login_popup(browser)

        responses = []
        for q in questions:
            answer = self.ask_question(browser, q["full_prompt"], q["id"])
            responses.append(LLMResponse(id=q["id"], question=q["question"], answer=answer))
        return responses

    def _send_first_message(self, browser):
        try:
            input_field = self._wait_for_input_field(browser)
            if input_field:
                self._send_clipboard_message(browser, input_field, "Where am I?")
                self._get_response(browser)
                self.first_message_sent = True
        except Exception as e:
            print(f"[!] Error sending first message: {e}")

    def _wait_for_input_field(self, browser):
        print("[DEBUG] Waiting for input field (textarea)...")
        try:
            field = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            print("[DEBUG] Input field located and clickable.")
            return field
        except TimeoutException:
            print("[!] Perplexity input field not found.")
            return None

    def _dismiss_login_popup(self, browser):
        try:
            close_icon = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "svg.tabler-icon.tabler-icon-x"))
            )
            close_icon.click()
            print("[INFO] Dismissed login modal.")
            time.sleep(0.5)
        except TimeoutException:
            print("[INFO] No login modal found to dismiss.")
        except Exception as e:
            print(f"[!] Failed to dismiss modal via click: {e}")
            try:
                print("[INFO] Trying ESC fallback...")
                browser.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(0.5)
            except Exception as esc_err:
                print(f"[!] ESC fallback also failed: {esc_err}")

    def _send_clipboard_message(self, browser, input_field, message):
        try:
            try:
                input_field.click()
            except Exception as click_err:
                print(f"[WARN] Input field not clickable: {click_err}, using JS focus()")
                browser.execute_script("arguments[0].focus();", input_field)

            time.sleep(0.3)
            input_field.send_keys(self.cmd_key, "a")
            input_field.send_keys(Keys.DELETE)
            pc.copy(message)
            input_field.send_keys(self.cmd_key, "v")
            time.sleep(0.4)
            input_field.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"[!] Failed to send message: {e}")

    def _get_response(self, browser, tries=0, max_tries=5) -> str:
        try:
            WebDriverWait(browser, 180).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='markdown-content']"))
            )
            response_divs = browser.find_elements(By.CSS_SELECTOR, "[id^='markdown-content']")
            if not response_divs:
                raise Exception("No response divs found.")
            return response_divs[-1].text.strip()
        except Exception as e:
            print(f"[!] Failed to get Perplexity response: {e}")
            if tries < max_tries:
                time.sleep(2)
                return self._get_response(browser, tries + 1)
            return ""