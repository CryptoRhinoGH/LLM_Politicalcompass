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
# Switzerland
# Netherlands
# Serbia
# UAE
# Singapore
# India
# Vietnam
# New Zealand
# Papua New Guinea
VPN_CONFIG_PATH="/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/vpnconfigs/nord/ovpn_udp/"
CREDS="/Users/abhisareen/Documents/PSU/temp/mitproject/LLM_Polilean/nordvpncreds"
# VPN configurations
# https://configs.ipvanish.com/openvpn/
# VPN_CONFIGS = {
#     "US": [
#         "vpnconfigs/nord/ovpn_udp/us-ca100.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/us-ca101.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/us-ca102.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/us-ca103.nordvpn.com.udp.ovpn"
#     ],
#     "CA": [
#         "vpnconfigs/nord/ovpn_udp/ca-us100.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ca-us101.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ca-us102.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ca-us103.nordvpn.com.udp.ovpn"
#     ],
#     "BZ": [
#         "vpnconfigs/nord/ovpn_udp/bz1.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/bz2.nordvpn.com.udp.ovpn"
#     ],
#     "GT": [
#         "vpnconfigs/nord/ovpn_udp/gt1.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/gt2.nordvpn.com.udp.ovpn"
#     ],
#     "CO": [
#         "vpnconfigs/nord/ovpn_udp/co1.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/co10.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/co2.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/co3.nordvpn.com.udp.ovpn"
#     ],
#     "BR": [
#         "vpnconfigs/nord/ovpn_udp/br101.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/br102.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/br103.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/br104.nordvpn.com.udp.ovpn"
#     ],
#     "NG": [
#         "vpnconfigs/nord/ovpn_udp/ng3.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ng4.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ng5.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ng6.nordvpn.com.udp.ovpn"
#     ],
#     "KE": [
#         "vpnconfigs/nord/ovpn_udp/ke1.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ke2.nordvpn.com.udp.ovpn"
#     ],
#     "CH": [
#         "vpnconfigs/nord/ovpn_udp/ch-fr1.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ch-fr2.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ch-fr3.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ch-nl17.nordvpn.com.udp.ovpn"
#     ],
#     "NL": [
#         "vpnconfigs/nord/ovpn_udp/nl-ch17.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/nl-ch18.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/nl-ch19.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/nl-ch20.nordvpn.com.udp.ovpn"
#     ],
#     "RS": [
#         "vpnconfigs/nord/ovpn_udp/rs48.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/rs49.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/rs50.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/rs51.nordvpn.com.udp.ovpn"
#     ],
#     "AE": [
#         "vpnconfigs/nord/ovpn_udp/ae54.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ae55.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ae56.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/ae57.nordvpn.com.udp.ovpn"
#     ],
#     "TW": [
#         "vpnconfigs/nord/ovpn_udp/tw-hk7.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/tw164.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/tw165.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/tw166.nordvpn.com.udp.ovpn"
#     ],
#     "SG": [
#         "vpnconfigs/nord/ovpn_udp/sg455.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/sg456.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/sg457.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/sg458.nordvpn.com.udp.ovpn"
#     ],
#     "IN": [
#         "vpnconfigs/nord/ovpn_udp/in150.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/in151.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/in152.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/in153.nordvpn.com.udp.ovpn"
#     ],
#     "VN": [
#         "vpnconfigs/nord/ovpn_udp/vn42.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/vn43.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/vn44.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/vn45.nordvpn.com.udp.ovpn"
#     ],
#     "NZ": [
#         "vpnconfigs/nord/ovpn_udp/nz100.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/nz101.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/nz102.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/nz103.nordvpn.com.udp.ovpn"
#     ],
#     "PG": [
#         "vpnconfigs/nord/ovpn_udp/pg1.nordvpn.com.udp.ovpn",
#         "vpnconfigs/nord/ovpn_udp/pg2.nordvpn.com.udp.ovpn"
#     ]
# }

VPN_CONFIGS = {
    "US": [
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-l9X35Zfu_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-xzHOyL2t_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-tl3nXSCH_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-UjTCbjpT_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-1RcjyKaZ_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-nlGE89Vn_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-dXrZEj95_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-oMlJxnFE_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-Hg5laqWJ_lifetime-30m",
        "geo.iproyal.com:12321:A1cnN2UOJ6JEd73q:tcpMw5KSCphxopeI_country-us_session-hMKejTEI_lifetime-30m"
    ],
    "CA": [
        "vpnconfigs/nord/ovpn_udp/ca1190.nordvpn.com.udp.ovpn",

    ],
    "CO": [
        "vpnconfigs/nord/ovpn_udp/co9.nordvpn.com.udp.ovpn"
    ],
    "NG": [
        "vpnconfigs/nord/ovpn_udp/ng3.nordvpn.com.udp.ovpn",
    ],
    "CH": [
        "vpnconfigs/nord/ovpn_udp/ch218.nordvpn.com.udp.ovpn",
    ],
    "NL": [
        "vpnconfigs/nord/ovpn_udp/nl-uk15.nordvpn.com.udp.ovpn",
    ],
    "RS": [
        "vpnconfigs/nord/ovpn_udp/rs80.nordvpn.com.udp.ovpn",
    ],
    "AE": [
        "vpnconfigs/nord/ovpn_udp/ae62.nordvpn.com.udp.ovpn",

    ],
    "SG": [
        "vpnconfigs/nord/ovpn_udp/sg477.nordvpn.com.udp.ovpn",
    ],
    "IN": [
        "vpnconfigs/nord/ovpn_udp/in165.nordvpn.com.udp.ovpn",
    ],
    "VN": [
        "vpnconfigs/nord/ovpn_udp/vn44.nordvpn.com.udp.ovpn",
    ],
    "NZ": [
        "vpnconfigs/nord/ovpn_udp/nz87.nordvpn.com.udp.ovpn",
    ]
}

# List of countries to iterate through
# COUNTRIES = ["BZ", "GT", "KE", "AE", "TW", "SG", "IN", "VN", "NZ", "PG"]
COUNTRIES = ["US", "CA", "CO", "NG", "CH", "NL", "RS", "AE", "SG", "IN", "VN", "NZ"]
# COUNTRIES = ["US", "CA", "CO", "NG", "NL", "RS", "AE", "SG", "IN", "VN", "NZ"]

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
RESULTS_DIR = "resultsfarright"
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Telegram notification settings
TELEGRAM_ENABLED = False

TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# Timing and retry settings
VPN_CONNECT_DELAY = 5        # seconds to wait after connecting VPN 
VPN_DISCONNECT_DELAY = 5      # seconds to wait after disconnecting VPN
SCRIPT_RETRY_COUNT = 4        # number of retries per script execution

# Default Chrome profile to use for all tests
CURRENT_PROFILE = "tempresults"

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
    "farright": {
        "path": "/Users/abhisareen/Library/Application Support/Google/Chrome/",
        "profile": "Profile 3"
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