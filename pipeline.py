import subprocess
import os
import time
import requests
import argparse
from threading import Lock
import config

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time

# Get the main logger
logger = config.main_logger

script_lock = Lock()

# class VPNController:
#     def __init__(self, country):
#         self.country = country
#         self.configs = config.VPN_CONFIGS.get(country, [])
#         self.logger = config.setup_logger(f'vpn_{country}', f'vpn_{country}.log')

#     def connect(self):
#         for config_file in self.configs:
#             try:
#                 self.logger.info(f"Connecting to VPN using {config_file}")
#                 subprocess.run(["sudo", "openvpn", "--config", config.VPN_CONFIG_PATH + config_file, "--auth-user-pass", config.CREDS], check=True)
#                 self.logger.info(f"Connected to VPN using {config_file}")
#                 self.send_notification(f"VPN connected using {config_file}")
#                 return True
#             except subprocess.CalledProcessError as e:
#                 self.logger.error(f"Failed to connect using {config_file}: {e}")
#                 self.send_notification(f"VPN connection failed using {config_file}")
#         return False

#     def disconnect(self):
#         try:
#             subprocess.run(["sudo", "killall", "openvpn"], check=True)
#             self.logger.info("VPN disconnected.")
#             self.send_notification("VPN disconnected")
#         except subprocess.CalledProcessError as e:
#             self.logger.error(f"Failed to disconnect VPN: {e}")
            
#     def send_notification(self, message):
#         if config.TELEGRAM_ENABLED:
#             try:
#                 requests.get(
#                     f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
#                     params={"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
#                 )
#                 self.logger.info("Telegram notification sent.")
#             except Exception as e:
#                 self.logger.error(f"Failed to send Telegram message: {e}")


class VPNController:
    def __init__(self, country):
        self.country = country
        self.configs = config.VPN_CONFIGS.get(country, [])
        self.logger = config.setup_logger(f'vpn_{country}', f'vpn_{country}.log')
        self.process = None

    def connect(self):
        for config_file in self.configs:
            try:
                self.logger.info(f"Attempting VPN connection with config: {config_file}")
                
                self.process = subprocess.Popen(
                    ["sudo", "openvpn", "--daemon", "--config", config.VPN_CONFIG_PATH + config_file, "--auth-user-pass", config.CREDS],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.logger.info("OpenVPN process started in background. Verifying connection...")
                time.sleep(5)
                # if self.wait_for_connection():
                #     self.logger.info(f"Successfully connected to VPN using {config_file}")
                #     self.send_notification(f"VPN connected using {config_file}")
                #     return True
                # else:
                #     self.logger.warning(f"VPN verification failed for {config_file}")
                #     self.send_notification(f"VPN connection failed to verify using {config_file}")
                #     self.process.terminate()
                #     time.sleep(3)

            except Exception as e:
                self.logger.error(f"Error connecting with {config_file}: {e}")
                self.send_notification(f"Exception during VPN connection: {e}")

        return False

    def wait_for_connection(self, timeout=30, interval=3):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                ip = self.get_public_ip()
                if ip:
                    self.logger.info(ip)
                    return True
            except Exception:
                pass
            time.sleep(interval)
        return False

    def get_public_ip():
        try:
            options = Options()
            # options.headless = True  # Headless so it doesn't open a visible window

            driver = uc.Chrome(options=options)
            driver.get("https://icanhazip.com")
            
            time.sleep(3)  # Wait for page to load

            ip_text = driver.find_element(By.TAG_NAME, "body").text.strip()
            driver.quit()
            return ip_text

        except Exception as e:
            print(f"UC browser IP fetch failed: {e}")
            return None

    def disconnect(self):
        try:
            subprocess.run(["sudo", "killall", "openvpn"], check=True)
            self.logger.info("VPN disconnected.")
            self.send_notification("VPN disconnected.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to disconnect VPN: {e}")

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
        
        # connected = vpn.connect()
        connected = True
        
        if not connected:
            logger.error(f"Failed to connect to VPN for country: {country}")
            continue
        
        # time.sleep(config.VPN_CONNECT_DELAY)
        
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
                        success = run_script(script_name, language, country, profile, trial_number)
                        if success:
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
    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}", exc_info=True)
        send_notification(f"Pipeline failed with error: {e}")