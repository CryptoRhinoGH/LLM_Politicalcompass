import re
import time
import json
import logging
import argparse
import selenium
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def choose(option):
    patterns = {
        0: re.compile(r'Strongly Disagree', re.IGNORECASE),
        3: re.compile(r'Strongly Agree', re.IGNORECASE),
        1: re.compile(r'Disagree', re.IGNORECASE),
        2: re.compile(r'Agree', re.IGNORECASE),
    }

    for id, pattern in patterns.items():
        if pattern.search(option):
            return id

    print("what?", option)
    exit(1)

# Old code choice - from github
# def choice(agree, disagree):
#     if agree == 0 and disagree == 0:
#         return 1
#     if agree >= disagree + threshold:
#         return 3
#     elif agree >= disagree:
#         return 2
#     elif disagree >= agree + threshold:
#         return 0
#     elif disagree >= agree:
#         return 1
#     else:
#         print("what?")
#         exit(0)

if __name__ == "__main__":
    
    question_xpath = [
        ["globalisationinevitable", "countryrightorwrong", "proudofcountry", "racequalities", "enemyenemyfriend", "militaryactionlaw", "fusioninfotainment"],
        ["classthannationality", "inflationoverunemployment", "corporationstrust", "fromeachability", "freermarketfreerpeople", "bottledwater", "landcommodity", "manipulatemoney", "protectionismnecessary", "companyshareholders", "richtaxed", "paymedical", "penalisemislead", "freepredatormulinational"],
        ["abortionillegal", "questionauthority", "eyeforeye", "taxtotheatres", "schoolscompulsory", "ownkind", "spankchildren", "naturalsecrets", "marijuanalegal", "schooljobs", "inheritablereproduce", "childrendiscipline", "savagecivilised", "abletowork", "represstroubles", "immigrantsintegrated", "goodforcorporations", "broadcastingfunding"],
        ["libertyterrorism", "onepartystate", "serveillancewrongdoers", "deathpenalty", "societyheirarchy", "abstractart", "punishmentrehabilitation", "wastecriminals", "businessart", "mothershomemakers", "plantresources", "peacewithestablishment"],
        ["astrology", "moralreligious", "charitysocialsecurity", "naturallyunlucky", "schoolreligious"],
        ["sexoutsidemarriage", "homosexualadoption", "pornography", "consentingprivate", "naturallyhomosexual", "opennessaboutsex"]
    ]
    next_xpath = ["/html/body/div[2]/div[2]/main/article/form/button", "/html/body/div[2]/div[2]/main/article/form/button",
    "/html/body/div[2]/div[2]/main/article/form/button", "/html/body/div[2]/div[2]/main/article/form/button",
    "/html/body/div[2]/div[2]/main/article/form/button", "/html/body/div[2]/div[2]/main/article/form/button"]

    result_xpath = "/html/body/div[2]/div[2]/main/article/section/article[1]/section/img"

with open('responses.json', 'r') as f:
    responses_by_country = json.load(f)

result = {}

for country, responses in responses_by_country.items():
    result[country] = []
    for response_obj in responses:
        result[country].append(choose(response_obj['response']))

print(result)
print(len(result['us']), len(result['ca']), len(result['in']), len(result['nz']))

which = 0

# Configure the logging for Selenium
logger = logging.getLogger('uc')
logger.setLevel(logging.DEBUG)

# Optional: Add a console handler if you want the logs to appear in the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


profile_path = r"/Users/abhisareen/Documents/PSU/temp/mitproject/chromeprofile/"

options = Options()
service = Service(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

options.add_argument(f"--user-data-dir={profile_path}")
# options.add_argument("--flag-switches-begin --flag-switches-end --no-first-run --no-service-autorun --password-store=basic --profile-directory=Profile 2")
options.add_argument("--no-first-run")
options.add_argument("--no-service-autorun")
options.add_argument("--password-store=basic")
options.add_argument("--enable-logging")

driver = uc.Chrome(options=options)
for country in result:
    print(f"Starting country: {country}")
    try:
        driver.get("https://www.politicalcompass.org/test/en?page=1")
    except exceptions.NoSuchWindowException:
        print("error occured, switching")
        driver.switch_to.window(driver.window_handles[-1]) # Switch to latest window handle
        driver.get("https://www.politicalcompass.org/test/en?page=1")
    time.sleep(3)
    # Initialize the Chrome WebDriver with visible GUI
    if len(result[country])>=62:
        which = 0
        for set in range(6):
            time.sleep(2)
            for q in question_xpath[set]:
                driver.find_element("xpath",
                    "//*[@id='" + q + "_" + str(result[country][which]) + "']"
                ).click()
                time.sleep(0.3)
                which += 1
                driver.execute_script("window.scrollBy(0,250)")
            driver.find_element("xpath", next_xpath[set]).click()
    else:
        print(f"Country {country} has {len(result[country])} responses")
    input("Press Enter to continue to next country:")


time.sleep(5000)