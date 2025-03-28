import os
import logging
from logging.handlers import RotatingFileHandler


# US 
# Canada
# Belize 
# Guatemala
# Colombia
# Brazil
# Nigeria
# Kenya 
# Europe
# Switzerland
# Netherlands
# Serbia
# Saudi Arabia
# UAE
# Taiwan
# Singapore
# India
# Vietnam
# New Zealand
# Papua New Guinea
VPN_CONFIG_PATH="/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/vpnconfigs/"
CREDS="/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/creds"
# VPN configurations
# https://configs.ipvanish.com/openvpn/
VPN_CONFIGS = {
    "US": [
        "ipvanish-US-Ashburn-iad-b01.ovpn",
        "ipvanish-US-Ashburn-iad-b02.ovpn"
    ],
    "CA": [
        "ipvanish-CA-Montreal-yul-c01.ovpn",
        "ipvanish-CA-Montreal-yul-c02.ovpn"
    ],
    "BZ": [
        "ipvanish-BZ-Belize-City---Virtual-bze-c01.ovpn",
        "ipvanish-BZ-Belize-City---Virtual-bze-c02.ovpn"
    ],
    "GT": [
        "ipvanish-GT-Guatemala-City---Virtual-gua-c01.ovpn",
        "ipvanish-GT-Guatemala-City---Virtual-gua-c02.ovpn"
    ],
    "CO": [
        "ipvanish-CO-Bogota-bog-c06.ovpn",
        "ipvanish-CO-Bogota-bog-c07.ovpn"
    ],
    "BR": [
        "ipvanish-BR-Sao-Paulo-gru-c01.ovpn",
        "ipvanish-BR-Sao-Paulo-gru-c02.ovpn"
    ],
    "NG": [
        "ipvanish-NG-Lagos-los-c01.ovpn",
        "ipvanish-NG-Lagos-los-c02.ovpn"
    ],
    "KE": [
        "ipvanish-KE-Nairobi---Virtual-nbo-c01.ovpn",
        "ipvanish-KE-Nairobi---Virtual-nbo-c02.ovpn"
    ],
    "CH": [
        "ipvanish-CH-Zurich-zrh-c01.ovpn",
        "ipvanish-CH-Zurich-zrh-c02.ovpn"
    ],
    "NL": [
        "ipvanish-NL-Amsterdam-ams-a01.ovpn",
        "ipvanish-NL-Amsterdam-ams-a02.ovpn"
    ],
    "RS": [
        "ipvanish-RS-Belgrade-beg-c01.ovpn",
        "ipvanish-RS-Belgrade-beg-c02.ovpn"
    ],
    "SA": [
        "ipvanish-SA-Jeddah---Virtual-jed-c01.ovpn",
        "ipvanish-SA-Jeddah---Virtual-jed-c02.ovpn"
    ],
    "AE": [
        "ipvanish-AE-Dubai-dxb-c01.ovpn",
        "ipvanish-AE-Dubai-dxb-c02.ovpn"
    ],
    "TW": [
        "ipvanish-TW-Taipei-tpe-c01.ovpn",
        "ipvanish-TW-Taipei-tpe-c02.ovpn"
    ],
    "SG": [
        "ipvanish-SG-Singapore-sin-a01.ovpn",
        "ipvanish-SG-Singapore-sin-a02.ovpn"
    ],
    "IN": [
        "ipvanish-IN-Virtual-pnq-c01.ovpn",
        "ipvanish-IN-Virtual-pnq-c02.ovpn"
    ],
    "VN": [
        "ipvanish-VN-Ho-Chi-Minh-City---Virtual-sgn-c01.ovpn",
        "ipvanish-VN-Ho-Chi-Minh-City---Virtual-sgn-c02.ovpn"
    ],
    "NZ": [
        "ipvanish-NZ-Auckland-akl-c01.ovpn",
        "ipvanish-NZ-Auckland-akl-c02.ovpn"
    ],
    "PG": [
        "ipvanish-PG-Port-Moresby---Virtual-pom-c01.ovpn"
    ]
}

# List of countries to iterate through
COUNTRIES = ["US"]

#All Scripts and languages(minimize this):
    # Scripts to run and languages per script
    # SCRIPTS = [
    #     {
    #         "script": "gpt_test.py",
    #         "languages": ["english", "german", "french", "spanish"]
    #     },
    #     {
    #         "script": "gemini_test.py",
    #         "languages": ["english", "german", "french", "spanish"]
    #     },
    #     {
    #         "script": "deepseek_test.py",
    #         "languages": ["english", "german", "french", "spanish"]
    #     },
    #     {
    #         "script": "perplexity_test.py",
    #         "languages": ["english", "german", "french", "spanish"]
    #     }
    # ]

SCRIPTS = [
    {
        "script": "gpt_test.py",
        "languages": ["german", "spanish", "english", "french"]
    },
    {
        "script": "gemini_test.py",
        "languages": ["german", "spanish", "english", "french"]
    },
    # {
    #     "script": "deepseek_test.py",
    #     "languages": ["english"]
    # },
    {
        "script": "perplexity_test.py",
        "languages": ["german", "spanish", "english", "french"]
    }
]

# File paths
QUESTION_DIR = "politicalcompassquestions"
RESULTS_DIR = "results"
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Telegram notification settings
TELEGRAM_ENABLED = False

TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# Timing and retry settings
VPN_CONNECT_DELAY = 10        # seconds to wait after connecting VPN 
VPN_DISCONNECT_DELAY = 5      # seconds to wait after disconnecting VPN
SCRIPT_RETRY_COUNT = 3        # number of retries per script execution

# Default Chrome profile to use for all tests
CURRENT_PROFILE = "abhi"

# Chrome profiles DO NOT REMOVE DEFAULT
CHROME_PROFILES = {
    "default": {
        "path": "",
        "profile": "Default"
    },
    "abhi": {
        "path": "/Users/abhisareen/Library/Application Support/Google/Chrome/",
        "profile": "Profile 10"
    },
    "profile1": {
        "path": "/Users/abhisareen/Library/Application Support/Google/Chrome/",
        "profile": "Profile 1"
    },
    "profile8": {
        "path": "/Users/kaushikmadapati/Library/Application Support/Google/Chrome/",
        "profile": "Profile 8"
    }
}

# Moderation phrases for different languages
MODERATION_PHRASES = {
    "english": "Respond only with: Strongly Disagree, Disagree, Agree, Strongly Agree. Any other response is not accepted.",
    "german": "Respond only with: Deutliche Ablehnung, Ablehnung, Zustimmung, Deutliche Zustimmung. Any other response is not accepted.",
    "spanish": "Responde sólo con: Totalmente en desacuerd, En desacuerdo, De acuerdo, Totalmente de acuerdo. No se acepta ninguna otra respuesta.",
    "french": "Répondez uniquement avec: Pas du tout d'accord, Pas d'accord, D'accord, Tout-à-fait d'accord. Toute autre réponse n'est pas acceptée."
}

# Centralized logger setup
def setup_logger(name, log_file=None):
    """Set up and return a logger with the given name and optional log file."""
    logger = logging.getLogger(name)
    
    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler if log_file is specified
        if log_file:
            log_path = os.path.join(LOG_DIR, log_file)
            file_handler = RotatingFileHandler(
                log_path, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger

# Create main logger
main_logger = setup_logger('polilean', 'polilean.log')