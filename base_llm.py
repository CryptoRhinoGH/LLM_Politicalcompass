import json
import time
import os
import re
import glob
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config

class BaseLLM:
    def __init__(self, model_name, language, country, profile_name=None):
        self.model_name = model_name
        self.language = language
        self.country = country
        # Use the provided profile_name or fall back to the config default
        self.profile_name = profile_name if profile_name else config.CURRENT_PROFILE
        self.driver = None
        self.question_file = f"polilean_{language.lower()}.json"
        
        # Set up logger for this instance
        self.logger = config.setup_logger(
            f'{model_name}_{language}_{country}',
            f'{model_name}_{language}_{country}.log'
        )
        
        # Determine the next trial number and set the response file name
        self.trial_number = self.get_next_trial_number()
        self.response_file = f"Trial{self.trial_number}_{model_name.lower()}_{language.lower()}_{country}.json"
        self.logger.info(f"Using trial number {self.trial_number} for this test")
        
        self.setup_driver()
        
    def get_next_trial_number(self):
        """Determine the next trial number based on existing files."""
        pattern = f"Trial*_{self.model_name.lower()}_{self.language.lower()}_{self.country}.json"
        search_path = os.path.join(config.RESULTS_DIR, pattern)
        
        existing_files = glob.glob(search_path)
        self.logger.info(f"Found {len(existing_files)} existing trial files matching {pattern}")
        
        if not existing_files:
            return 1
            
        trial_numbers = []
        for file_path in existing_files:
            file_name = os.path.basename(file_path)
            match = re.match(r"Trial(\d+)_", file_name)
            if match:
                trial_numbers.append(int(match.group(1)))
                
        if not trial_numbers:
            return 1
            
        return max(trial_numbers) + 1
        
    def setup_driver(self):
        """Set up the Chrome driver with the specified profile."""
        options = Options()
        profile_config = config.CHROME_PROFILES.get(self.profile_name, config.CHROME_PROFILES["default"])
        options.add_argument(f"--user-data-dir={profile_config['path']}")
        options.add_argument(f"--profile-directory={profile_config['profile']}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--password-store=basic")
        options.add_argument("--enable-logging")
        
        self.logger.info(f"Initializing Chrome driver for {self.model_name} using profile {self.profile_name}")
        self.driver = uc.Chrome(options=options)
        
    def load_questions(self):
        """Load questions from the JSON file."""
        self.logger.info(f"Loading questions for {self.model_name} in {self.language} from {self.country}")
        try:
            results_path = os.path.join(config.RESULTS_DIR, self.response_file)
            if os.path.exists(results_path):
                with open(results_path, 'r') as f:
                    return json.load(f)
            else:
                questions_path = os.path.join(config.QUESTION_DIR, self.question_file)
                self.logger.info(f"Response file not found, generating new file from {questions_path}")
                with open(questions_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading questions: {e}")
            raise
            
    def save_response(self, questions_data):
        """Save responses to the JSON file."""
        results_path = os.path.join(config.RESULTS_DIR, self.response_file)
        with open(results_path, 'w') as f:
            json.dump(questions_data, f, indent=4)
        self.logger.info(f"Saved responses to {results_path}")
            
    def navigate_to_chat(self):
        """Navigate to the chat interface. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement navigate_to_chat()")
        
    def send_message(self, message):
        """Send a message to the LLM. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement send_message()")
        
    def get_response(self):
        """Get the response from the LLM. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_response()")
        
    def run_test(self):
        """Run the test for all questions."""
        try:
            questions_data = self.load_questions()
            self.navigate_to_chat()
            
            moderation_phrase = config.MODERATION_PHRASES.get(self.language.lower(), 
                                                            config.MODERATION_PHRASES["english"])
            
            for idx, question_data in enumerate(questions_data):
                if question_data["response"] not in ["", None]:
                    continue
                    
                self.logger.info(f"Processing question {idx + 1}/{len(questions_data)}...")
                question = question_data["question"] + " " + moderation_phrase
                
                self.send_message(question)
                response = self.get_response()
                question_data["response"] = response
                
                self.logger.info(f"Saving response for question {idx + 1}...")
                self.save_response(questions_data)
                
                self.logger.info("Waiting before the next question...")
                time.sleep(3)
                
        except Exception as e:
            self.logger.error(f"Error running test: {e}", exc_info=True)
            raise
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed.")