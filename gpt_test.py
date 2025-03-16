import time
import pyperclip as pc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from base_llm import BaseLLM
import config

class GPTTest(BaseLLM):
    def __init__(self, language, country, profile_name=None):
        super().__init__("gpt", language, country, profile_name)
        
    def navigate_to_chat(self):
        """Navigate to the ChatGPT interface."""
        try:
            self.driver.get("https://chatgpt.com")
            self.logger.info("Successfully opened ChatGPT with the specified profile.")
            time.sleep(15)  # Wait for page to load
            self.close_stay_logged_out_popup()
            time.sleep(5)  # Wait for page to load
        except Exception as e:
            self.logger.error(f"Error navigating to ChatGPT: {e}")
            raise
            

    def close_stay_logged_out_popup(self):
        """Check for and close the 'Stay logged out' popup if it appears."""
        try:
            # Wait for a short time to see if the popup appears
            self.logger.info("Checking for 'Stay logged out' popup...")
            
            # Use the specific selector provided
            try:
                # jsquery = input("Enter JS querySelector")
                self.driver.execute_script('document.querySelector("#radix-\\\\:r13\\\\: > div > div > a")')
                time.sleep(1)  # Wait for the popup to close
                self.logger.info("Closed 'Stay logged out' popup")
                return True
            except (TimeoutException, NoSuchElementException):
                self.logger.info("No 'Stay logged out' popup found or unable to close it")
                return False
                    
        except Exception as e:
            self.logger.warning(f"Error handling 'Stay logged out' popup: {e}")
            return False

    def send_message(self, message):
        """Send a message to ChatGPT."""
        try:
            self.logger.info(f"Sending message: {message[:50]}...")  # Log first 50 chars
            
            input_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ProseMirror"))
            )
            
            input_field.clear()  # Ensure input field is empty
            time.sleep(1)  # Small delay before pasting
            
            pc.copy(message)
            input_field.send_keys(Keys.COMMAND, 'v')  # Paste message
            time.sleep(1)
            
            input_field.send_keys(Keys.COMMAND + Keys.ENTER)  # Send message
            self.logger.info("Message sent.")
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise
            
    def get_response(self):
        """Get the response from ChatGPT."""
        self.logger.info("Waiting for ChatGPT response...")
        
        try:
            # Wait until a new response from ChatGPT appears
            WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-message-author-role='assistant']"))
            )
            
            self.logger.info("ChatGPT response detected!")
            
            # Fetch the latest assistant response
            conversation_turns = self.driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
            response_text = conversation_turns[-1].text  # Get the last assistant response
            
            # Ensure response is properly captured
            if response_text.strip() == "":
                self.logger.warning("Warning: Empty response detected, retrying...")
                time.sleep(3)
                return self.get_response()  # Retry fetching the response
            
            self.logger.info(f"Response received: {response_text[:50]}...")  # Print first 50 chars
            return response_text
            
        except TimeoutException:
            self.logger.error("Error: ChatGPT did not respond in time.")
            return "ERROR: No response received."

if __name__ == "__main__":
    import sys
    import os
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run GPT test for Political Compass')
    parser.add_argument('language', nargs='?', default=os.environ.get("LANGUAGE", "english"),
                        help='Language for the test (default: english)')
    parser.add_argument('country', nargs='?', default=os.environ.get("COUNTRY", "US"),
                        help='Country for the test (default: US)')
    parser.add_argument('--profile', '-p', dest='profile',
                        help=f'Chrome profile to use (default: {config.CURRENT_PROFILE})')
    
    args = parser.parse_args()
    
    # Create and run the test
    gpt_test = GPTTest(args.language, args.country, args.profile)
    gpt_test.run_test()