import os
import logging
from logging.handlers import RotatingFileHandler

# VPN configurations
VPN_CONFIGS = {
    "US": [
        "/path/to/vpnconfigs/ipvanish-US-Cincinnati-cvg-b09.ovpn",
        "/path/to/vpnconfigs/ipvanish-US-New-York-nyc-c32.ovpn"
    ],
    # Add more countries and their configurations as needed
}

# List of countries to iterate through
COUNTRIES = ["US"]

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
        "languages": ["english"]
    },
    {
        "script": "gemini_test.py",
        "languages": ["english"]
    },
    {
        "script": "deepseek_test.py",
        "languages": ["english"]
    },
    {
        "script": "perplexity_test.py",
        "languages": ["english"]
    }
]

# File paths
QUESTION_DIR = "politicalcompassquestions"
RESULTS_DIR = "results"
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Telegram notification settings
TELEGRAM_ENABLED = True
# TELEGRAM_BOT_TOKEN = "1490935675:AAGvRH0xrMurN5Sb5UJpP2ZCHZ6KwVgMf_Y" ## TE Notifier
TELEGRAM_BOT_TOKEN = "1428479715:AAExp9C7Jk1drQm8MdUju84nLmmAHsNqsa8"  ## movement_sensor.py
TELEGRAM_CHAT_ID = "1426503248"

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