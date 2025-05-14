import re
import os
import csv
import time
import json
import logging
import argparse
import selenium
import pandas as pd
import undetected_chromedriver as uc
# from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SUMMARY_CSV = "csv_results/summary.csv"

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

def append_summary_row(trial, pol_leaning, chatbot, language, country, ec, soc, filename):
    os.makedirs(os.path.dirname(SUMMARY_CSV), exist_ok=True)

    # Define columns in order
    cols = ["trial","pol_leaning","chatbot","language","country",
            "results_x","results_y","filename","results_xy"]

    # Build the new row as a DataFrame
    new_row = pd.DataFrame([{
        "trial":       trial,
        "pol_leaning": pol_leaning,
        "chatbot":     chatbot,
        "language":    language,
        "country":     country,
        "results_x":   ec,
        "results_y":   soc,
        "filename":    filename,
        "results_xy":  f"{ec}&{soc}"
    }], columns=cols)

    # Load existing data if the file exists
    if os.path.exists(SUMMARY_CSV):
        df = pd.read_csv(SUMMARY_CSV)

        # Check if this filename is already present
        if filename in df["filename"].values:
            print(f"⚠️  Warning: Overwriting existing entry for {filename}")

        # Drop any rows with the same filename
        df = df[df["filename"] != filename]
    else:
        df = pd.DataFrame(columns=cols)

    # Concatenate the new row and write back to the CSV
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(SUMMARY_CSV, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process survey responses.')
    parser.add_argument('file', type=str, help='Path to the JSON file with responses.')
    parser.add_argument('--dry-run', action=argparse.BooleanOptionalAction, help="Dry run to check if file will be runnable")

    args = parser.parse_args()

    base_filename = os.path.basename(args.file).rstrip('.json')
    parts = base_filename.split('_') 
    trial_number = int(parts[0].lstrip('Trial'))
    pol_leaning  = parts[1]
    chatbot      = parts[2]
    language     = parts[3]
    country      = parts[4]


    question_xpath = [
        ["globalisationinevitable", "countryrightorwrong", "proudofcountry", "racequalities", "enemyenemyfriend", "militaryactionlaw", "fusioninfotainment"],
        ["classthannationality", "inflationoverunemployment", "corporationstrust", "fromeachability", "freermarketfreerpeople", "bottledwater", "landcommodity", "manipulatemoney", "protectionismnecessary", "companyshareholders", "richtaxed", "paymedical", "penalisemislead", "freepredatormulinational"],
        ["abortionillegal", "questionauthority", "eyeforeye", "taxtotheatres", "schoolscompulsory", "ownkind", "spankchildren", "naturalsecrets", "marijuanalegal", "schooljobs", "inheritablereproduce", "childrendiscipline", "savagecivilised", "abletowork", "represstroubles", "immigrantsintegrated", "goodforcorporations", "broadcastingfunding"],
        ["libertyterrorism", "onepartystate", "serveillancewrongdoers", "deathpenalty", "societyheirarchy", "abstractart", "punishmentrehabilitation", "wastecriminals", "businessart", "mothershomemakers", "plantresources", "peacewithestablishment"],
        ["astrology", "moralreligious", "charitysocialsecurity", "naturallyunlucky", "schoolreligious"],
        ["sexoutsidemarriage", "homosexualadoption", "pornography", "consentingprivate", "naturallyhomosexual", "opennessaboutsex"]
    ]
    next_xpath = ["/html/body/div[2]/div[2]/div[2]/article/form/button"] * len(question_xpath)
    # result_xpath = "/html/body/div[2]/div[2]/main/article/section/article[1]/section/img"

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

    options = Options()
    # service = Service(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    
    options.add_argument(f"--user-data-dir=/Users/abhisareen/Documents/PSU/temp/mitproject/chrome_profiles/")
    options.add_argument(f"--profile-directory=Default")
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
                append_summary_row(
                    trial       = trial_number,
                    pol_leaning = pol_leaning,
                    chatbot     = chatbot,
                    language    = language,
                    country     = country,
                    ec          = ec,
                    soc         = soc,
                    filename    = base_filename,
                )
                print(f"Appended summary for {base_filename} to {SUMMARY_CSV}")
        else:
            print("Not enough responses to proceed with the survey.")

    except exceptions.NoSuchWindowException:
        print("Error occurred, switching window.")
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the latest window handle
    finally:
        final_url = driver.current_url
        driver.quit()  # Ensure the driver is closed at the end
    print("Automation complete. Final URL reached:", final_url)