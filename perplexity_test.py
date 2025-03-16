import time
import pyperclip as pc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from base_llm import BaseLLM
import config

class PerplexityTest(BaseLLM):
    def __init__(self, language, country, profile_name=None):
        super().__init__("perplexity", language, country, profile_name)
        self.first_message_sent = False
        
    def navigate_to_chat(self):
        """Navigate to the Perplexity interface."""
        try:
            self.driver.get("https://www.perplexity.ai/")
            self.logger.info("Successfully opened Perplexity with the specified profile.")
            time.sleep(5)  # Wait for page to load
        except Exception as e:
            self.logger.error(f"Error navigating to Perplexity: {e}")
            raise
            
    def send_first_message(self):
        """Send the first message to Perplexity."""
        try:
            self.logger.info("Sending first message to initialize chat")
            
            # Locate the input field for Perplexity
            input_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Ask anything...']"))
            )
            
            # Focus on the text area
            input_field.click()
            
            # Clear any existing text in the input field
            input_field.send_keys(Keys.COMMAND, "a")  # Select all text
            input_field.send_keys(Keys.DELETE)        # Delete the selected text
            
            # Type the message into the text area
            pc.copy("Polilean test")
            input_field.send_keys(Keys.COMMAND, 'v')
            
            time.sleep(1)  # Sleep to mimic typing delay
            
            # Send the message
            input_field.send_keys(Keys.COMMAND + Keys.ENTER)
            
            self.logger.info("First message sent")
            self.first_message_sent = True
            
            # Wait for response
            self.get_response()
            
        except Exception as e:
            self.logger.error(f"Error sending first message: {e}")
            raise
            
    def send_message(self, message):
        """Send a message to Perplexity."""
        try:
            if not self.first_message_sent:
                self.send_first_message()
                
            self.logger.info(f"Sending message: {message[:50]}...")  # Log first 50 chars
            
            # Locate the input field for Perplexity
            input_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Ask follow-up']"))
            )
            
            # Focus on the text area
            input_field.click()
            
            # Clear any existing text in the input field
            input_field.send_keys(Keys.COMMAND, "a")  # Select all text
            input_field.send_keys(Keys.DELETE)        # Delete the selected text
            
            # Type the message into the text area
            time.sleep(0.7)
            pc.copy(message)
            input_field.send_keys(Keys.COMMAND, 'v')
            
            time.sleep(0.5)  # Sleep to mimic typing delay
            
            # Send the message
            input_field.send_keys(Keys.COMMAND + Keys.ENTER)
            
            self.logger.info("Message sent.")
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise
            
    def get_response(self):
        """Get the response from Perplexity."""
        self.logger.info("Waiting for Perplexity response...")
        
        try:
            # Locate the input field for Perplexity
            input_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Ask follow-up']"))
            )
            
            # Focus on the text area and send dummy text to make button clickable
            input_field.click()
            input_field.send_keys("a")
            
            # Wait for the submit button to be clickable
            submit_button = WebDriverWait(self.driver, 40).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit']"))
            )
            
            # Wait until all divs with the class 'mb-md' are present in the DOM
            all_response_divs = WebDriverWait(self.driver, 180).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.mb-md"))
            )
            
            # Get the last div with class 'mb-md'
            response_div = all_response_divs[-1]
            
            # Clear any existing text in the input field
            input_field.send_keys(Keys.COMMAND, "a")  # Select all text
            input_field.send_keys(Keys.DELETE)        # Delete the selected text
            
            # Extract the text from the last 'div.mb-md'
            response_text = response_div.text
            
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
    parser = argparse.ArgumentParser(description='Run Perplexity test for Political Compass')
    parser.add_argument('language', nargs='?', default=os.environ.get("LANGUAGE", "english"),
                        help='Language for the test (default: english)')
    parser.add_argument('country', nargs='?', default=os.environ.get("COUNTRY", "US"),
                        help='Country for the test (default: US)')
    parser.add_argument('--profile', '-p', dest='profile',
                        help=f'Chrome profile to use (default: {config.CURRENT_PROFILE})')
    
    args = parser.parse_args()
    
    # Create and run the test
    perplexity_test = PerplexityTest(args.language, args.country, args.profile)
    perplexity_test.run_test()