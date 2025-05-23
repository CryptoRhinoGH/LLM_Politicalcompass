import subprocess
import os
import time
import requests
import argparse
from threading import Lock
import config
import json
import time

# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# import undetected_chromedriver as uc

# Get the main logger
logger = config.main_logger

script_lock = Lock()

# class NordVPNController:
    # def __init__(self, country):
    #     self.country = country
    #     self.configs = config.VPN_CONFIGS.get(country, [])
    #     self.logger = config.setup_logger(f'vpn_{country}', f'vpn_{country}.log')
    #     self.current_index = 0  # Keep track of the last used config

    # def connect(self):
    #     attempts = 0
    #     total_configs = len(self.configs)

    #     while attempts < total_configs:
    #         config_file = self.configs[self.current_index]
    #         full_config_path = os.path.join(config.VPN_CONFIG_PATH, os.path.basename(config_file))
    #         self.logger.info(f"Trying to connect using: {full_config_path}")

    #         try:
    #             result = subprocess.run(
    #                 ["zsh", "nordvpn.sh", config.CREDS, full_config_path],
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE
    #             )
    #             time.sleep(config.VPN_CONNECT_DELAY)
    #             if result.returncode == 0:
    #                 self.logger.info("Connected. Verifying public IP...")
    #                 ip_info = self._check_ip()

    #                 if ip_info and ip_info.get("ip"):
    #                     ip = ip_info.get("ip")
    #                     country_code = ip_info.get("country")
    #                     self.logger.info(f"Verified IP: {ip}, Country: {country_code}")
    #                     self.send_notification(f"VPN connected: {ip} ({country_code}) via {os.path.basename(config_file)}")
    #                     return True
    #                 else:
    #                     self.logger.warning("VPN IP check failed — moving to next config.")
    #             else:
    #                 self.logger.warning(f"VPN script failed:\n{result.stderr.decode()}")

    #         except Exception as e:
    #             self.logger.error(f"Error connecting VPN: {e}")
    #             self.send_notification(f"VPN exception: {e}")

    #         self.current_index = (self.current_index + 1) % total_configs
    #         attempts += 1
    #         time.sleep(3)

    #     self.logger.error("All VPN configs exhausted without success.")
    #     return False

    # def rotate_and_connect(self):
    #     self.disconnect()
    #     time.sleep(3)
    #     self.current_index = (self.current_index + 1) % len(self.configs)
    #     return self.connect()

    # def _check_ip(self):
    #     try:
    #         result = subprocess.run(
    #             ["zsh", "nordvpn.sh", "check_ip"],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE
    #         )
    #         if result.returncode == 0:
    #             return json.loads(result.stdout.decode())
    #         else:
    #             self.logger.warning(f"check_ip failed:\n{result.stderr.decode()}")
    #     except Exception as e:
    #         self.logger.warning(f"check_ip exception: {e}")
    #     return None

    # def disconnect(self):
    #     self.logger.info("Disconnecting VPN...")
    #     try:
    #         subprocess.run(["zsh", "nordvpn.sh", "disconnect"], check=True)
    #         self.logger.info("VPN disconnected.")
    #         self.send_notification("VPN disconnected.")
    #     except subprocess.CalledProcessError as e:
    #         self.logger.error(f"VPN disconnection failed: {e}")
    #         self.send_notification("VPN disconnection failed.")

    # def send_notification(self, message):
    #     if config.TELEGRAM_ENABLED:
    #         try:
    #             requests.get(
    #                 f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
    #                 params={"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
    #             )
    #             self.logger.info("Telegram notification sent.")
    #         except Exception as e:
    #             self.logger.error(f"Failed to send Telegram message: {e}")

class VPNController:
    def __init__(self, country):
        self.country = country
        self.configs = config.VPN_CONFIGS.get(country, [])
        self.logger = config.setup_logger(f'proxy_{country}', f'proxy_{country}.log')
        self.proxy_index = 0  # Keep track of the current proxy index
        self.current_proxy = None

    def connect(self):
        if not self.configs:
            self.logger.error("No proxy configs available.")
            return None

        proxy = self.configs[self.proxy_index]
        self.current_proxy = proxy
        self.logger.info(f"Using proxy index {self.proxy_index}: {proxy}")

        # Optional: IP verification
        ip_info = self._check_ip()
        if ip_info and ip_info.get("ip"):
            ip = ip_info["ip"]
            country_code = ip_info.get("country", "Unknown")
            self.logger.info(f"Proxy IP verified: {ip} ({country_code})")
            self.send_notification(f"Proxy connected: {ip} ({country_code})")
        else:
            self.logger.warning("Failed to verify proxy IP (continuing anyway).")

        return self.proxy_index  # Return the index so the test script can pick the right proxy

    def rotate_and_connect(self):
        if not self.configs:
            self.logger.error("No proxy configs available to rotate.")
            return None

        self.proxy_index = (self.proxy_index + 1) % len(self.configs)
        self.logger.info(f"Rotating to next proxy index: {self.proxy_index}")
        return self.connect()

    def disconnect(self):
        self.logger.info("Proxy disconnect called — no action needed for SOCKS5.")
        self.send_notification("Proxy disconnect (noop).")

    def _check_ip(self):
        try:
            proxies = {
                "http": self.current_proxy,
                "https": self.current_proxy
            }
            response = requests.get("https://api.myip.com", proxies=proxies, timeout=10)
            return response.json()
        except Exception as e:
            self.logger.warning(f"Proxy check_ip exception: {e}")
            return None

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



def run_script(script_name, language, country, profile=None, trial_number=None, proxy_index=None):
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
            if proxy_index is not None:
                cmd.extend(["--proxy_index", str(proxy_index)])


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

def is_test_done(result_filename):
    """Return True if the test result exists and the dry-run passes."""
    if os.path.exists(result_filename):
        dry_run_result = subprocess.run(
            ["python3", "political_compass.py", result_filename, "--dry-run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return dry_run_result.returncode == 0
    return False

def gather_tests(country, trial_number):
    """Return a list of tasks (script_name, language, result_filename) for tests that are not yet complete."""
    tasks = []
    unique_languages = set()
    for script_info in config.SCRIPTS:
        unique_languages.update(script_info["languages"])
        
    for language in unique_languages:
        for script_info in config.SCRIPTS:
            if language not in script_info["languages"]:
                continue
            script_name = script_info["script"]
            base_script_name = script_name.replace("_test.py", "")
            result_filename = f"{config.RESULTS_DIR}/Trial{trial_number}_{base_script_name}_{language}_{country}.json"
            if not is_test_done(result_filename):
                tasks.append((script_name, language, result_filename))
    return tasks

def all_tests_completed(trial_number):
    """
    Returns True if for every expected (country, script, language) combination,
    the corresponding result file exists and passes the dry-run test.
    """
    for country in config.COUNTRIES:
        for script_info in config.SCRIPTS:
            for language in script_info["languages"]:
                base_script_name = script_info["script"].replace("_test.py", "")
                result_filename = f"{config.RESULTS_DIR}/Trial{trial_number}_{base_script_name}_{language}_{country}.json"
                # If the result file doesn't exist or the dry-run doesn't pass, tests are incomplete.
                if not os.path.exists(result_filename):
                    return False
                dry_run_result = subprocess.run(
                    ["python3", "political_compass.py", result_filename, "--dry-run"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if dry_run_result.returncode != 0:
                    return False
    return True

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
    try:
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
            
            tasks = gather_tests(country, trial_number)
            if not tasks:
                logger.info(f"No pending tests for {country}. Skipping VPN connection.")
                continue


            proxy_index = vpn.connect()
            # connected = True
            
            if proxy_index is None:
                logger.error(f"Failed to assign proxy for country: {country}")
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
                    
                    retries = len(vpn.configs)+1
                    success = False

                    result_filename = f"{config.RESULTS_DIR}/Trial{trial_number}_{base_script_name}_{language}_{country}.json"
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

                    
                    while retries >= 0 and not success:
                        try:
                            ## Check if results/Trial{trial_num}_{script_name(but remove _test.py from the end since script_name is like gpt_test.py)}_{country}.json exists, if so, then run the political compass in dry run and see if file is runnable
                            result = run_script(script_name, language, country, profile, trial_number, proxy_index)
                            if result == "vpn_switch":
                                logger.info(f"{script_name} requested VPN rotation for {language}, {country}")
                                retries -= 1
                                proxy_index = vpn.rotate_and_connect()
                                continue
                            elif result is True:
                                success = True
                                break
                        except Exception as e:
                            logger.error(f"Error running {script_name} for {language}, {country}, ERROR:{e}. Retries left: {retries}")
                            time.sleep(5)  # Wait before retrying
                        finally:
                            retries -= 1
                    
                    if not success:
                        send_notification(f"Failed to run {script_name} for {language}, {country} after all retries")
            
            # Disconnect VPN after all tests for this country are complete
            vpn.disconnect()
            time.sleep(config.VPN_DISCONNECT_DELAY)
        
        # Log completion of pipeline
        logger.info("Political Compass LLM testing pipeline completed")
        send_notification("Political Compass LLM testing pipeline completed")
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        send_notification("Pipeline interrupted by user.")
        try:
            vpn.disconnect()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}", exc_info=True)
        send_notification(f"Pipeline failed with error: {e}")


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

        max_iterations = 10
        iteration = 0
        while not all_tests_completed(args.trial_num) and iteration < max_iterations:
            main(args.profile, args.trial_num)
            iteration += 1
            logger.info(f"Pipeline iteration {iteration} completed. Checking test completion...")
            time.sleep(5)
        if all_tests_completed(args.trial_num):
            logger.info("All tests are complete!")
        else:
            logger.warning("Maximum iterations reached, but some tests are still incomplete.")


    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        send_notification("Script execution interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}", exc_info=True)
        send_notification(f"Pipeline failed with error: {e}")