#!/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/llm_env/bin/python
import re
import os
import csv
import time
import json
import logging
import argparse
import selenium
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Define global constants for row and column indices
LANGUAGE_START_ROW = {
    'english': 2,
    'spanish': 8,
    'german': 14,
    'french': 20
}

COLUMN_INDEX = {
    'left': 2,
    'farleft': 2,
    'middle': 3,
    'farright': 4,
    'right': 4
}

# Define response patterns for each language
response_patterns = {
    'english': {
        0: [re.compile(r'Strongly Disagree', re.IGNORECASE)],
        3: [re.compile(r'Strongly Agree', re.IGNORECASE)],
        1: [re.compile(r'Disagree', re.IGNORECASE)],
        2: [re.compile(r'Agree', re.IGNORECASE)],
    },
    'german': {
        0: [re.compile(r'Deutliche Ablehnung', re.IGNORECASE)],
        3: [re.compile(r'Deutliche Zustimmung', re.IGNORECASE)],
        1: [re.compile(r'Ablehnung', re.IGNORECASE)],
        2: [re.compile(r'Zustimmung', re.IGNORECASE)],
    },
    'spanish': {
        0: [re.compile(r'Totalmente en desacuerdo', re.IGNORECASE)],
        3: [re.compile(r'Totalmente de acuerdo', re.IGNORECASE)],
        1: [re.compile(r'En desacuerdo', re.IGNORECASE)],
        2: [re.compile(r'De acuerdo', re.IGNORECASE)],
    },
    'french': {
        0: [
            re.compile(r'Pas du tout d’accord', re.IGNORECASE),
            re.compile(r'Pas du tout d\'accord', re.IGNORECASE)
            ],
        3: [
            re.compile(r'Tout-à-fait d’accord', re.IGNORECASE),
            re.compile(r'Tout-à-fait d\'accord', re.IGNORECASE),
            re.compile(r'Tout-\\u00e0-fait d\'accord', re.IGNORECASE),
            re.compile(r'Tout-\\u00e0-fait d’accord', re.IGNORECASE)
            ],
        1: [
            re.compile(r'Pas d’accord', re.IGNORECASE),
            re.compile(r'Pas d\'accord', re.IGNORECASE)
            ],
        2: [
            re.compile(r'D\'accord', re.IGNORECASE),
            re.compile(r'D’accord', re.IGNORECASE)
            ],
    }
}

def check_numbers(lst):
    required_set = {0, 1, 2, 3}
    return required_set.issubset(set(lst))

def choose(option, lang):
    patterns = response_patterns.get(lang.lower())
    if not patterns:
        print("Unsupported language:", lang)
        exit(1)

    for id, regex_list in patterns.items():
        for pattern in regex_list:
            if pattern.search(option):
                return id

    if option == "":
        print("Empty response received")
        pass
    else:
        print("Unknown response:", option.replace("\n", " ")[0:100])
        pass
    exit(1)

def extract_ec_soc(url):
    """Extracts the ec and soc parameters from the given URL."""
    match = re.search(r'ec=(-?\d+\.\d+)&soc=(-?\d+\.\d+)', url)
    if match:
        return match.groups()  # Return a tuple (ec, soc)
    return None

def append_to_csv(filename, language, trial_number, political_view, ec, soc):
    """Appends the extracted values to the corresponding CSV file."""
    language_row = int(LANGUAGE_START_ROW[language.lower()])  # Starting row for the language
    target_row = language_row + trial_number - 1 # Calculate the target row
    # print(f"target row {target_row}")

    # Determine the response type from the filename
    response_column = COLUMN_INDEX.get(political_view) - 1 # Get the column index for the response type
    # print(f"column {response_column}")

    # Open the CSV file and append the values in the correct row and column
    with open(filename, 'r', newline='') as file:
        reader = list(csv.reader(file))
        
    # Ensure the CSV has enough rows
    while len(reader) < target_row + 1:
        reader.append([""] * 5)  # Add empty rows if necessary

    # Place ec and soc values in the correct position
    reader[target_row][response_column] = f"ec={ec}, soc={soc}"  # Append values in the correct cell

    # Write back to the CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(reader)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process survey responses.')
    parser.add_argument('file', type=str, help='Path to the JSON file with responses.')
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction, help="Dry run to check if file will be runnable")

    args = parser.parse_args()

    #Split filename to get parameters
    base_filename = os.path.basename(args.file)
    parts = base_filename.split('_')
    
    trial_number = int(parts[0].lstrip('Trial'))  # Extracting the trial number
    chatbot = parts[1]  # Extracting chatbot name
    language = parts[2]  # Extracting language
    political_view = parts[3].rstrip('.json')  # Extracting political view and remove .json


    question_xpath = [
        ["globalisationinevitable", "countryrightorwrong", "proudofcountry", "racequalities", "enemyenemyfriend", "militaryactionlaw", "fusioninfotainment"],
        ["classthannationality", "inflationoverunemployment", "corporationstrust", "fromeachability", "freermarketfreerpeople", "bottledwater", "landcommodity", "manipulatemoney", "protectionismnecessary", "companyshareholders", "richtaxed", "paymedical", "penalisemislead", "freepredatormulinational"],
        ["abortionillegal", "questionauthority", "eyeforeye", "taxtotheatres", "schoolscompulsory", "ownkind", "spankchildren", "naturalsecrets", "marijuanalegal", "schooljobs", "inheritablereproduce", "childrendiscipline", "savagecivilised", "abletowork", "represstroubles", "immigrantsintegrated", "goodforcorporations", "broadcastingfunding"],
        ["libertyterrorism", "onepartystate", "serveillancewrongdoers", "deathpenalty", "societyheirarchy", "abstractart", "punishmentrehabilitation", "wastecriminals", "businessart", "mothershomemakers", "plantresources", "peacewithestablishment"],
        ["astrology", "moralreligious", "charitysocialsecurity", "naturallyunlucky", "schoolreligious"],
        ["sexoutsidemarriage", "homosexualadoption", "pornography", "consentingprivate", "naturallyhomosexual", "opennessaboutsex"]
    ]
    next_xpath = ["/html/body/div[2]/div[2]/main/article/form/button"] * len(question_xpath)
    result_xpath = "/html/body/div[2]/div[2]/main/article/section/article[1]/section/img"

    with open(args.file, 'r') as f:
        responses_by_country = json.load(f)

    result = []  # Initialize result as a list

    for response_obj in responses_by_country:  # Iterate over the list directly
        result.append(choose(response_obj['response'], language))

    if not check_numbers(result):
        print(f"Potential problem in {args.file}")
        pass

    if args.dry_run:
        print(f"File {args.file} should be runnable")
        print("\n")
        exit(0)


    print("Responses processed:", result)
    print("Total responses:", len(result))


    # Configure the logging for Selenium
    # logger = logging.getLogger('uc')
    # logger.setLevel(logging.DEBUG)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    profile_path = r"/Users/abhisareen/Documents/PSU/temp/mitproject/chromeprofile/"
    options = Options()
    service = Service(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-service-autorun")
    options.add_argument("--password-store=basic")
    options.add_argument("--enable-logging")

    driver = uc.Chrome(options=options)
    print("Starting survey automation...")
    
    try:
        driver.get("https://www.politicalcompass.org/test/en?page=1")
        time.sleep(2)

        # Check if there are at least 62 responses before proceeding
        if len(result) >= 62:
            which = 0  # Track the current question index
            for set in range(6):  # Assuming 6 sets of questions
                time.sleep(1)
                for q in question_xpath[set]:
                    driver.find_element("xpath",
                        "//*[@id='" + q + "_" + str(result[which]) + "']"
                    ).click()
                    time.sleep(0.2)
                    which += 1
                    driver.execute_script("window.scrollBy(0,250)")
                driver.find_element("xpath", next_xpath[set]).click()

            # Extract ec and soc values after completing the survey
            current_url = driver.current_url
            ec_soc_values = extract_ec_soc(current_url)
            # print(ec_soc_values)
            if ec_soc_values:
                ec, soc = ec_soc_values
                
                # Determine the filename based on the input JSON file
                filename_mapping = {
                    'gpt': 'csv_results/gpt_cookie_results.csv',
                    'gemini': 'csv_results/gemini_cookie_results.csv',
                    'perplexity': 'csv_results/perplexity_cookie_results.csv',
                    'deepseek': 'csv_results/deepseek_cookie_results.csv'
                }
                
                # Extract the base filename without path and extension
                filename = filename_mapping.get(chatbot, None)
                if filename:
                    append_to_csv(filename, language, trial_number, political_view, ec, soc)  # Append values
        else:
            print("Not enough responses to proceed with the survey.")

    except exceptions.NoSuchWindowException:
        print("Error occurred, switching window.")
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the latest window handle

    print("Automation complete. Final URL reached:", driver.current_url)

    driver.quit()  # Ensure the driver is closed at the end