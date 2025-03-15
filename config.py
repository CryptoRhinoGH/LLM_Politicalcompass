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
SCRIPTS = [
    {"script": "deepseek.py", "languages": ["french", "german", "spanish"]},
    {"script": "gemini.py", "languages": ["french", "german", "spanish"]},
    {"script": "gpt.py", "languages": ["french", "german", "spanish"]},
    {"script": "perplexity.py", "languages": ["french", "german", "spanish"]}
]

# Telegram notification settings
TELEGRAM_ENABLED = True
# TELEGRAM_BOT_TOKEN = "1490935675:AAGvRH0xrMurN5Sb5UJpP2ZCHZ6KwVgMf_Y" ## TE Notifier
TELEGRAM_BOT_TOKEN = "1428479715:AAExp9C7Jk1drQm8MdUju84nLmmAHsNqsa8"  ## movement_sensor.py
TELEGRAM_CHAT_ID = "1426503248"

# Timing and retry settings
VPN_CONNECT_DELAY = 10        # seconds to wait after connecting VPN
VPN_DISCONNECT_DELAY = 5      # seconds to wait after disconnecting VPN
SCRIPT_RETRY_COUNT = 3        # number of retries per script execution
