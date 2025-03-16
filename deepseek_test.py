import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from base_llm import BaseLLM
import config

class DeepSeekTest(BaseLLM):
    def __init__(self, language, country, profile_name=None):
        super().__init__("deepseek", language, country, profile_name)
        
    def navigate_to_chat(self):
        """Navigate to the DeepSeek interface."""
        try:
            self.driver.get("https://chat.deepseek.com")
            self.logger.info("Successfully opened DeepSeek with the specified profile.")
            time.sleep(3)  # Wait for page to load
        except Exception as e:
            self.logger.error(f"Error navigating to DeepSeek: {e}")
            raise
            
    def send_message(self, message):
        """Send a message to DeepSeek."""
        try:
            self.logger.info(f"Sending message: {message[:50]}...")  # Log first 50 chars
            
            # Locate the input field
            input_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "chat-input"))
            )
            
            # Click to focus the input field
            input_field.click()
            time.sleep(0.5)
            
            # Simulate typing each character to trigger DeepSeek's UI event listeners
            for char in message:
                input_field.send_keys(char)
                time.sleep(0.05)  # Mimic human typing
            
            # Use COMMAND + ENTER to submit (For macOS, use CONTROL + ENTER on Windows)
            input_field.send_keys(Keys.COMMAND + Keys.ENTER)
            
            self.logger.info("Message sent.")
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise
            
    def get_response(self):
        """Get the response from DeepSeek."""
        self.logger.info("Waiting for DeepSeek response...")
        
        try:
            # Get the number of responses before sending the message
            previous_responses = self.driver.find_elements(By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")
            previous_response_count = len(previous_responses)
            
            # Wait for a new response to appear
            WebDriverWait(self.driver, 30).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")) > previous_response_count
            )
            
            # Add a short delay to ensure response is fully rendered
            time.sleep(5)  # Adjust timing if necessary
            
            # Fetch all response elements again
            response_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")
            
            # Get the last response (newest one)
            last_response_element = response_elements[-1]
            
            # Extract full text properly
            last_response = last_response_element.text.strip()
            
            self.logger.info(f"Response received: {last_response[:50]}...")  # Print first 50 chars
            return last_response
            
        except TimeoutException:
            self.logger.error("Error: DeepSeek did not respond in time.")
            return "ERROR: No response received."

if __name__ == "__main__":
    import sys
    import os
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run DeepSeek test for Political Compass')
    parser.add_argument('language', nargs='?', default=os.environ.get("LANGUAGE", "english"),
                        help='Language for the test (default: english)')
    parser.add_argument('country', nargs='?', default=os.environ.get("COUNTRY", "US"),
                        help='Country for the test (default: US)')
    parser.add_argument('--profile', '-p', dest='profile',
                        help=f'Chrome profile to use (default: {config.CURRENT_PROFILE})')
    
    args = parser.parse_args()
    
    # Create and run the test
    deepseek_test = DeepSeekTest(args.language, args.country, args.profile)
    deepseek_test.run_test()