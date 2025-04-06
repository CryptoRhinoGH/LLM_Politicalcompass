import subprocess
import os
import time
import requests
import argparse
from threading import Lock
import config
import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

# Get the main logger
logger = config.main_logger

script_lock = Lock()

class VPNController:
    def __init__(self, country):
        self.country = country
        self.configs = config.VPN_CONFIGS.get(country, [])
        self.logger = config.setup_logger(f'vpn_{country}', f'vpn_{country}.log')
        self.current_index = 0  # Keep track of the last used config

    def connect(self):
        attempts = 0
        total_configs = len(self.configs)

        while attempts < total_configs:
            config_file = self.configs[self.current_index]
            full_config_path = os.path.join(config.VPN_CONFIG_PATH, os.path.basename(config_file))
            self.logger.info(f"Trying to connect using: {full_config_path}")

            try:
                result = subprocess.run(
                    ["zsh", "nordvpn.sh", config.CREDS, full_config_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(config.VPN_CONNECT_DELAY)
                if result.returncode == 0:
                    self.logger.info("Connected. Verifying public IP...")
                    ip_info = self._check_ip()

                    if ip_info and ip_info.get("ip"):
                        ip = ip_info.get("ip")
                        country_code = ip_info.get("country")
                        self.logger.info(f"Verified IP: {ip}, Country: {country_code}")
                        self.send_notification(f"VPN connected: {ip} ({country_code}) via {os.path.basename(config_file)}")
                        return True
                    else:
                        self.logger.warning("VPN IP check failed — moving to next config.")
                else:
                    self.logger.warning(f"VPN script failed:\n{result.stderr.decode()}")

            except Exception as e:
                self.logger.error(f"Error connecting VPN: {e}")
                self.send_notification(f"VPN exception: {e}")

            self.current_index = (self.current_index + 1) % total_configs
            attempts += 1
            time.sleep(3)

        self.logger.error("All VPN configs exhausted without success.")
        return False

    def rotate_and_connect(self):
        self.disconnect()
        time.sleep(3)
        self.current_index = (self.current_index + 1) % len(self.configs)
        return self.connect()

    def _check_ip(self):
        try:
            result = subprocess.run(
                ["zsh", "nordvpn.sh", "check_ip"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                return json.loads(result.stdout.decode())
            else:
                self.logger.warning(f"check_ip failed:\n{result.stderr.decode()}")
        except Exception as e:
            self.logger.warning(f"check_ip exception: {e}")
        return None

    def disconnect(self):
        self.logger.info("Disconnecting VPN...")
        try:
            subprocess.run(["zsh", "nordvpn.sh", "disconnect"], check=True)
            self.logger.info("VPN disconnected.")
            self.send_notification("VPN disconnected.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"VPN disconnection failed: {e}")
            self.send_notification("VPN disconnection failed.")

    def send_notification(self, message):
        if config.TELEGRAM_ENABLED:
            try:
                requests.get(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                    params={"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
                )
                self.logger.info("Telegram notification sent.")
            except Exception as e:
                self.logger.error(f"Failed to send Telegram message: {e}")



def run_script(script_name, language, country, profile=None, trial_number=None):
    with script_lock:
        script_logger = config.setup_logger(
            f'script_{script_name}_{language}_{country}',
            f'script_{script_name}_{language}_{country}.log'
        )
        
        script_logger.info(f"Running {script_name} for language: {language}, country: {country}, profile: {profile or config.CURRENT_PROFILE}")
        try:
            cmd = ["python3", script_name, "--language", language, "--country", country]
            if profile:
                cmd.extend(["--profile", profile])
            if trial_number:
                cmd.extend(["-t", trial_number])

            subprocess.run(
                cmd,
                check=True,
                env={**os.environ, "LANGUAGE": language, "COUNTRY": country}
            )
            script_logger.info(f"Successfully completed {script_name} for {language}, {country}")
            return True
        except subprocess.CalledProcessError as e:
            if e.returncode == 42:
                script_logger.warning("Script requested VPN rotation.")
                return "vpn_switch"
            script_logger.error(f"Script {script_name} failed for language {language}, country {country}: {e}")
            send_notification(f"Script {script_name} failed for language {language}, country {country}")
            return False


def send_notification(message):
    if config.TELEGRAM_ENABLED:
        try:
            requests.get(
                f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                params={"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
            )
            logger.info("Telegram notification sent.")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")


def main(profile=None, trial_number=None):
    # Ensure results directory exists
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    
    # Log start of pipeline
    logger.info(f"Starting Political Compass LLM testing pipeline with profile: {profile or config.CURRENT_PROFILE}")
    send_notification(f"Starting Political Compass LLM testing pipeline with profile: {profile or config.CURRENT_PROFILE}")
    
    for country in config.COUNTRIES:
        vpn = VPNController(country)
        logger.info(f"Processing country: {country}")
        
        if not vpn.configs:
            logger.warning(f"No VPN configs available for country: {country}")
            send_notification(f"No VPN configs available for country: {country}")
            continue
        
        connected = vpn.connect()
        # connected = True
        
        if not connected:
            logger.error(f"Failed to connect to VPN for country: {country}")
            continue
        
        # for language in languages:
        print("starting script")

        unique_languages = set()
        for script_info in config.SCRIPTS:
            unique_languages.update(script_info["languages"])

        for language in unique_languages:
            for script_info in config.SCRIPTS:
                if language not in script_info["languages"]:
                    continue

                script_name = script_info["script"]
                print(f"{script_name}, {language}")
                base_script_name = script_name.replace("_test.py", "")
                
                retries = config.SCRIPT_RETRY_COUNT
                success = False

                result_filename = f"results/Trial{trial_number}_{base_script_name}_{language}_{country}.json"
                if os.path.exists(result_filename):
                    print(f"Checking dry-run for {result_filename}...")
                    dry_run_result = subprocess.run(
                        ["python3", "political_compass.py", result_filename, "--dry-run"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    if dry_run_result.returncode == 0:
                        print(f"{result_filename} already processed successfully. Skipping...")
                        continue  # Skip this run since dry-run succeeded
                    else:
                        print(f"Dry-run failed or empty for {result_filename}. Proceeding with script execution...")

                
                while retries > 0 and not success:
                    try:
                        ## Check if results/Trial{trial_num}_{script_name(but remove _test.py from the end since script_name is like gpt_test.py)}_{country}.json exists, if so, then run the political compass in dry run and see if file is runnable
                        result = run_script(script_name, language, country, profile, trial_number)
                        if result == "vpn_switch":
                            logger.info(f"{script_name} requested VPN rotation for {language}, {country}")
                            vpn.rotate_and_connect()
                            continue
                        elif result is True:
                            success = True
                            break
                    except Exception as e:
                        retries -= 1
                        logger.error(f"Error running {script_name} for {language}, {country}, ERROR:{e}. Retries left: {retries}")
                        time.sleep(5)  # Wait before retrying
                
                if not success:
                    send_notification(f"Failed to run {script_name} for {language}, {country} after all retries")
        
        # Disconnect VPN after all tests for this country are complete
        vpn.disconnect()
        time.sleep(config.VPN_DISCONNECT_DELAY)
    
    # Log completion of pipeline
    logger.info("Political Compass LLM testing pipeline completed")
    send_notification("Political Compass LLM testing pipeline completed")


if __name__ == "__main__":
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Run Political Compass LLM testing pipeline')
        parser.add_argument('--profile', '-p', dest='profile',
                            help=f'Chrome profile to use (default: {config.CURRENT_PROFILE})')
        parser.add_argument('--trial_num', '-t', dest='trial_num',
                            help=f'Trial number', required=True)
        
        args = parser.parse_args()
        
        main(args.profile, args.trial_num)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        send_notification("Script execution interrupted by user.")
        vpn.disconnect()
    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}", exc_info=True)
        send_notification(f"Pipeline failed with error: {e}")