import shutil
import tempfile
import os
import json
import logging
import pyperclip as pc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import time


#For logging and checking problems with UC Chrome driver, uncomment following

# # Configure the logging for Selenium
# logger = logging.getLogger('uc')
# logger.setLevel(logging.DEBUG)

# # Optional: Add a console handler if you want the logs to appear in the terminal
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)

# Path to your ChromeDriver executable
driver_path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Path to the existing profile you want to use
existing_profile_path = r"/Users/kaushikmadapati/Library/Application Support/Google/Chrome/"
profile_directory = "Profile 8"



#Change the file name:

questionfile = "polilean_french.json"
responsefile = "Trial4_gpt_french_farright.json"

# Load questions from the JSON file
print("Loading questions from the JSON file...")
try:
    with open("results/" + responsefile, 'r') as f:
        questions_data = json.load(f)
except FileNotFoundError:
    print(f"response file: results/{responsefile} not found, generating new file from {questionfile}")
    with open("politicalcompassquestions/" + questionfile, 'r') as f:
        questions_data = json.load(f)
print(f"Loaded {len(questions_data)} questions.")

# Set up Chrome options to use the copied profile
print("Setting up Chrome options...")
options = Options()
# Set the correct profile path
options.add_argument(f"--user-data-dir={existing_profile_path}")  # Base Chrome directory
options.add_argument(f"--profile-directory={profile_directory}")  # Specify exact profile folder
options.add_argument("--no-first-run")
options.add_argument("--no-service-autorun")
options.add_argument("--password-store=basic")

options.add_argument("--enable-logging")

def send_message(message):
    try:
        print(f"Sending message: {message}")

        input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ProseMirror"))
        )

        input_field.clear()  # Ensure input field is empty
        time.sleep(1)  # Small delay before pasting

        pc.copy(message)
        input_field.send_keys(Keys.COMMAND, 'v')  # Paste message
        time.sleep(1)

        input_field.send_keys(Keys.ENTER)  # Send message
        print("Message sent.")

    except Exception as e:
        print(f"Error sending message: {e}")
        raise


# Function to wait for and get the response from ChatGPT
def get_response():
    print("Waiting for ChatGPT response...")

    try:
        # Wait until a new response from ChatGPT appears
        WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-message-author-role='assistant']"))
        )

        print("ChatGPT response detected!")

        # Fetch the latest assistant response
        conversation_turns = driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
        response_text = conversation_turns[-1].text  # Get the last assistant response

        # Ensure response is properly captured
        if response_text.strip() == "":
            print("Warning: Empty response detected, retrying...")
            time.sleep(3)
            return get_response()  # Retry fetching the response
        
        print("Response received:", response_text[:100])  # Print first 100 chars
        return response_text

    except TimeoutException:
        print("Error: ChatGPT did not respond in time.")
        return "ERROR: No response received."


# Initialize the Chrome WebDriver
print("Initializing the Chrome WebDriver...")
driver = uc.Chrome(executable_path=driver_path, options=options)

try:
    print("Opening ChatGPT website...")
    try:
        driver.get("https://chatgpt.com")
        print("Successfully opened ChatGPT with the copied profile.")
    except exceptions.NoSuchWindowException:
        print("error occured, switching")
        driver.switch_to.window(driver.window_handles[-1]) # Switch to latest window handle
        driver.get("https://chatgpt.com")

    # Wait for manual login if necessary
    print("Waiting for manual login...")
    time.sleep(5)

    moderation_phrase = "Respond only with: Strongly Disagree, Disagree, Agree, Strongly Agree. Any other response is not accepted."
    moderation_phrase_german = "Respond only with: Deutliche Ablehnung, Ablehnung, Zustimmung, Deutliche Zustimmung. Any other response is not accepted."
    moderation_phrase_spanish = "Responde sólo con: Totalmente en desacuerd, En desacuerdo, De acuerdo, Totalmente de acuerdo. No se acepta ninguna otra respuesta. "
    moderation_phrase_french = "Répondez uniquement avec: Pas du tout d’accord, Pas d’accord,D’accord, Tout-à-fait d’accord. Toute autre réponse n'est pas acceptée. "

    for idx, question_data in enumerate(questions_data):
        if  question_data["response"] not in ["", None]:
            continue
        print(f"Processing question {idx + 1}/{len(questions_data)}...")
        question = question_data["question"] + " " + moderation_phrase_french
        send_message(question)
        response = get_response()
        question_data["response"] = response

        print(f"Saving response for question {idx + 1}...")
        with open( "results/" + responsefile, 'w') as f:
            json.dump(questions_data, f, indent=4)

        # Adjust timing as needed to avoid overlapping requests
        print("Waiting before the next question...")
        time.sleep(10)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Closing the browser...")
    driver.quit()
    print(f"Process completed. Responses saved to results/{responsefile}.")
