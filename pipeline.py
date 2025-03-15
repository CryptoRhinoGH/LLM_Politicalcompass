import subprocess
import json
import os
import time
import logging
import requests
import config
from threading import Lock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

script_lock = Lock()

class VPNController:
    def __init__(self, country):
        self.country = country
        self.configs = config.VPN_CONFIGS.get(country, [])

    def connect(self):
        for config_file in self.configs:
            try:
                subprocess.run(["sudo", "openvpn", "--config", config_file], check=True)
                logging.info(f"Connected to VPN using {config_file}")
                return True
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to connect using {config_file}: {e}")
                send_telegram_message(f"VPN connection failed using {config_file}")
        return False

    def disconnect(self):
        subprocess.run(["sudo", "killall", "openvpn"], check=True)
        logging.info("VPN disconnected.")


def send_telegram_message(message):
    if config.TELEGRAM_ENABLED:
        try:
            requests.get(f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                         params={"chat_id": config.TELEGRAM_CHAT_ID, "text": message})
            logging.info("Telegram notification sent.")
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")


def run_script(script_name, language):
    with script_lock:
        env = os.environ.copy()
        env["LANGUAGE"] = language
        command = ["python3", script_name]

        logging.info(f"Running {script_name} for language: {language}")
        try:
            subprocess.run(command, env=env, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Script {script_name} failed for language {language}: {e}")
            send_telegram_message(f"Script {script_name} failed for language {language}")


def main():
    for country in config.COUNTRIES:
        vpn = VPNController(country)
        logging.info(f"Connecting VPN for country: {country}")

        if not vpn.configs:
            logging.warning(f"No VPN configs available for country: {country}")
            send_telegram_message(f"No VPN configs available for country: {country}")
            continue

        connected = vpn.connect()
        if not connected:
            continue

        time.sleep(config.VPN_CONNECT_DELAY)

        for script_info in config.SCRIPTS:
            script_name = script_info["script"]
            languages = script_info["languages"]
            for language in languages:
                retries = config.SCRIPT_RETRY_COUNT
                while retries > 0:
                    try:
                        run_script(script_name, language)
                        break
                    except Exception as e:
                        retries -= 1
                        logging.error(f"Retrying script {script_name} for language {language}, attempts left: {retries}")
                        if retries == 0:
                            send_telegram_message(f"Script {script_name} for language {language} failed after retries")

        vpn.disconnect()
        time.sleep(config.VPN_DISCONNECT_DELAY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
        send_telegram_message("Script execution interrupted by user.")
