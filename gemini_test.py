import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from base_llm import BaseLLM
import config

class GeminiTest(BaseLLM):
    def __init__(self, language, country, profile_name=None):
        super().__init__("gemini", language, country, profile_name)
        
    def navigate_to_chat(self):
        """Navigate to the Gemini interface."""
        try:
            self.driver.get("https://gemini.google.com/app")
            self.logger.info("Successfully opened Gemini with the specified profile.")
            time.sleep(20)  # Wait for page to load and potential login
        except Exception as e:
            self.logger.error(f"Error navigating to Gemini: {e}")
            raise
            
    def send_message(self, message):
        """Send a message to Gemini."""
        try:
            self.logger.info(f"Sending message: {message[:50]}...")  # Log first 50 chars
            
            # Locate the contenteditable div inside the rich-textarea
            input_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "rich-textarea div[contenteditable='true']"))
            )
            
            # Focus on the text area
            input_field.click()
            
            # Clear the current content
            input_field.send_keys(Keys.CONTROL + "a")  # Select all text
            input_field.send_keys(Keys.DELETE)  # Delete the selected text
            
            # Send the message by typing it
            input_field.send_keys(message)
            
            time.sleep(1)  # Sleep to mimic typing delay
            
            # Find and click the send button
            send_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.send-button-container.visible"))
            )
            send_button.click()
            
            self.logger.info("Message sent.")
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise
            
    def get_response(self):
        """Get the response from Gemini."""
        self.logger.info("Waiting for Gemini response...")
        
        try:
            # Wait until the send button returns to the "no text in the box" state
            WebDriverWait(self.driver, 180).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.send-button-container.disabled"))
            )
            
            # Find the latest conversation container
            latest_conversation = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.conversation-container"))
            )[-1]  # Get the last conversation container
            
            # Extract the model response within the latest conversation container
            response_element = latest_conversation.find_element(By.CSS_SELECTOR, "model-response .model-response-text")
            response_text = response_element.text
            
            self.logger.info(f"Response received: {response_text[:50]}...")  # Print first 50 chars
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error getting response: {e}")
            return "ERROR: No response received."

if __name__ == "__main__":
    import sys
    import os
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run Gemini test for Political Compass')
    parser.add_argument('language', nargs='?', default=os.environ.get("LANGUAGE", "english"),
                        help='Language for the test (default: english)')
    parser.add_argument('country', nargs='?', default=os.environ.get("COUNTRY", "US"),
                        help='Country for the test (default: US)')
    parser.add_argument('--profile', '-p', dest='profile',
                        help=f'Chrome profile to use (default: {config.CURRENT_PROFILE})')
    
    args = parser.parse_args()
    
    # Create and run the test
    gemini_test = GeminiTest(args.language, args.country, args.profile)
    gemini_test.run_test()