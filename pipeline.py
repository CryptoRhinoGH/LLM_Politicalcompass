import subprocess
import os
import time
import requests
import argparse
from threading import Lock
import config

# Get the main logger
logger = config.main_logger

script_lock = Lock()

class VPNController:
    def __init__(self, country):
        self.country = country
        self.configs = config.VPN_CONFIGS.get(country, [])
        self.logger = config.setup_logger(f'vpn_{country}', f'vpn_{country}.log')

    def connect(self):
        for config_file in self.configs:
            try:
                self.logger.info(f"Connecting to VPN using {config_file}")
                subprocess.run(["sudo", "openvpn", "--config", config_file], check=True)
                self.logger.info(f"Connected to VPN using {config_file}")
                self.send_notification(f"VPN connected using {config_file}")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to connect using {config_file}: {e}")
                self.send_notification(f"VPN connection failed using {config_file}")
        return False

    def disconnect(self):
        try:
            subprocess.run(["sudo", "killall", "openvpn"], check=True)
            self.logger.info("VPN disconnected.")
            self.send_notification("VPN disconnected")
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


def run_script(script_name, language, country, profile=None):
    with script_lock:
        script_logger = config.setup_logger(
            f'script_{script_name}_{language}_{country}',
            f'script_{script_name}_{language}_{country}.log'
        )
        
        script_logger.info(f"Running {script_name} for language: {language}, country: {country}, profile: {profile or config.CURRENT_PROFILE}")
        try:
            cmd = ["python3", script_name, language, country]
            if profile:
                cmd.extend(["--profile", profile])
                
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


def main(profile=None):
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
        
        for script_info in config.SCRIPTS:
            script_name = script_info["script"]
            languages = script_info["languages"]
            
            for language in languages:
                retries = config.SCRIPT_RETRY_COUNT
                success = False
                
                while retries > 0 and not success:
                    try:
                        success = run_script(script_name, language, country, profile)
                        if success:
                            break
                    except Exception as e:
                        retries -= 1
                        logger.error(f"Error running {script_name} for {language}, {country}. Retries left: {retries}")
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
        
        args = parser.parse_args()
        
        main(args.profile)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        send_notification("Script execution interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}", exc_info=True)
        send_notification(f"Pipeline failed with error: {e}")