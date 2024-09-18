import json
import time
import pyperclip as pc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

# Path to your ChromeDriver executable
driver_path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Path to the existing profile you want to use
#existing_profile_path = r"/Users/abhisareen/Library/Application Support/Google/Chrome/"
existing_profile_path = r"/Users/aryanmehta/Library/Application Support/Google/Chrome/"


#Change the file name:

questionfile = "polilean_german.json"
responsefile = "german_gemini_farright.json"


# Load questions from the JSON file
print("Loading questions from the JSON file...")
with open(questionfile, 'r') as f:
    questions_data = json.load(f)
print(f"Loaded {len(questions_data)} questions.")

# Set up Chrome options to use the copied profile
print("Setting up Chrome options...")
options = uc.ChromeOptions()
options.add_argument(f"--user-data-dir={existing_profile_path}")
options.add_argument("--no-first-run")
options.add_argument("--no-service-autorun")
options.add_argument("--password-store=basic")
options.add_argument("--profile-directory=Default")
options.add_argument("--enable-logging")

def send_message_first(message):
    print("send_message")

    # Locate the input field for Perplexity
    input_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Ask anything...']"))
    )

    # Focus on the text area
    input_field.click()

    # Clear any existing text in the input field (if necessary)
    input_field.send_keys(Keys.COMMAND, "a")  # Select all text (use COMMAND on Mac if needed)
    input_field.send_keys(Keys.DELETE)        # Delete the selected text

    # Type the message into the text area
    pc.copy(message)
    input_field.send_keys(Keys.COMMAND, 'v')

    time.sleep(1)  # Sleep to mimic typing delay

    # Find and click the send button (after the message is entered)

    input_field.send_keys(Keys.COMMAND + Keys.ENTER)

    print("send_message_first [DONE]")

def send_message(message):
    print("send_message")

    # Locate the input field for Perplexity
    input_field = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Ask follow-up']"))
    )

    # Focus on the text area
    input_field.click()

    # Clear any existing text in the input field (if necessary)
    input_field.send_keys(Keys.COMMAND, "a")  # Select all text (use COMMAND on Mac if needed)
    input_field.send_keys(Keys.DELETE)        # Delete the selected text

    # Type the message into the text area
    time.sleep(0.7)
    pc.copy(message)
    input_field.send_keys(Keys.COMMAND, 'v')

    time.sleep(0.5)  # Sleep to mimic typing delay

    # Find and click the send button (after the message is entered)

    input_field.send_keys(Keys.COMMAND + Keys.ENTER)

    print("send_message [DONE]")

def get_response():
    print("get_response")
    # time.sleep(100)
    # print("\n")
    try:
        # Locate the input field for Perplexity
        input_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='Ask follow-up']"))
        )
        # print("Entering in input field")
        # Focus on the text area and send dummy text to make button clickable after so we know when response is done
        input_field.click()
        input_field.send_keys("a")
        # print("Waiting for button to be enabled")
        submit_button = WebDriverWait(driver, 40).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit']"))
        )
        # print("Getting the latest response")
        # Wait until all divs with the class 'mb-md' are present in the DOM
        all_response_divs = WebDriverWait(driver, 180).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.mb-md"))
        )

        # Get the last div with class 'mb-md'
        response_div = all_response_divs[-1]

        # Clear any existing text in the input field
        input_field.send_keys(Keys.COMMAND, "a")  # Select all text (use COMMAND on Mac if needed)
        input_field.send_keys(Keys.DELETE)        # Delete the selected text


        # Extract the text from the last 'div.mb-md'
        response_text = response_div.text
        # print()
        # print("Latest response: ")
        print(response_text)
        # print("\n")
        print("get_response [DONE]")
        return response_text

    except Exception as e:
        print(f"An error occurred while getting the response: {e}")
        return None

# Initialize the Chrome WebDriver
print("Initializing the Chrome WebDriver...")
driver = uc.Chrome(options=options)
time.sleep(5)
try:
    print("Opening Perplexity website...")
    driver.get("https://www.perplexity.ai/")
    print("Successfully opened Perplexity with the copied profile.")

    # Wait for manual login if necessary
    print("Waiting for manual login...")
    time.sleep(5)

    moderation_phrase = "Respond only with: Strongly Disagree, Disagree, Agree, Strongly Agree. Any other response is not accepted."
    moderation_phrase_german = "Respond only with: Deutliche Ablehnung, Ablehnung, Zustimmung, Deutliche Zustimmung. Any other response is not accepted."
    moderation_phrase_spanish = "Responde sólo con: Totalmente en desacuerd, En desacuerdo, De acuerdo, Totalmente de acuerdo. No se acepta ninguna otra respuesta. "
    moderation_phrase_french = "Répondez uniquement avec: Pas du tout d’accord, Pas d’accord,D’accord, Tout-à-fait d’accord. Toute autre réponse n'est pas acceptée. "

    send_message_first("Polilean test")
    get_response()
    for idx, question_data in enumerate(questions_data):
        if question_data["response"] not in ["", None]:
            continue
        print(f"Processing question {idx + 1}/{len(questions_data)}...")
        question = question_data["question"] + " " + moderation_phrase
        send_message(question)
        response = get_response()

        question_data["response"] = response

        print(f"Saving response for question {idx + 1}...")
        with open(responsefile, 'w') as f:
            json.dump(questions_data, f, indent=4)

        # Adjust timing as needed to avoid overlapping requests
        print("Waiting before the next question...")
        time.sleep(3)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Closing the browser...")
    driver.quit()
    print("Process completed. Responses saved to 'german_perplexity_farright.json'.")