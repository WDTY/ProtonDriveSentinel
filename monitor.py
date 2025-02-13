import time
import configparser
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import Client as TwilioClient
import logging
import sys

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# General settings
ALERT_SERVICE = config['general'].get('alert_service', 'twilio').lower()
PROTON_DRIVE_URL = config['general'].get('proton_drive_url')

# Twilio settings
TWILIO_ACCOUNT_SID = config['twilio'].get('account_sid')
TWILIO_AUTH_TOKEN = config['twilio'].get('auth_token')
TWILIO_WHATSAPP_NUMBER = config['twilio'].get('whatsapp_number')
TARGET_WHATSAPP_NUMBER = config['twilio'].get('target_number')

# Telegram settings
TELEGRAM_BOT_TOKEN = config['telegram'].get('bot_token')
TELEGRAM_CHAT_ID = config['telegram'].get('chat_id')

# Track known items (files and directories)
KNOWN_ITEMS = set()

def send_telegram_message(message):
    """Sends a message via Telegram."""
    if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        logging.error("Telegram configuration is incomplete.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info("Message sent via Telegram.")
        else:
            logging.error("Failed to send message via Telegram: %s", response.text)
    except Exception as e:
        logging.error("Error sending message via Telegram: %s", e)

def get_proton_drive_items():
    """Scrapes Proton Drive and returns a set of available files and directories."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--user-data-dir=/tmp/chrome-user-data")

    driver = webdriver.Chrome(options=options)
    logging.info("Opening Proton Drive: %s", PROTON_DRIVE_URL)
    driver.get(PROTON_DRIVE_URL)

    try:
        # Wait up to 15 seconds for items to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Folder') or contains(text(), '.')]"))
        )
        logging.info("Items loaded successfully.")
    except Exception as e:
        logging.error("Timeout waiting for items: %s", e)

    # Debug: Save page source
    page_source = driver.page_source
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(page_source)

    # Detect both files and folders using the refined XPath
    item_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Folder') or contains(text(), '.')]")
    items = {item.text.strip() for item in item_elements if item.text.strip()}

    logging.info("Items found: %s", items)
    driver.quit()
    return items


def check_for_new_items():
    """Checks for new or modified items on Proton Drive and sends alerts."""
    global KNOWN_ITEMS
    current_items = get_proton_drive_items()

    # Log the list of items retrieved
    logging.info("Retrieved items: %s", current_items)

    new_items = current_items - KNOWN_ITEMS
    if new_items:
        KNOWN_ITEMS.update(current_items)
        send_alerts(new_items)

def send_alerts(new_items):
    """Sends alerts via the selected service."""
    message = f"New items detected:\n" + "\n".join(new_items)
    if ALERT_SERVICE == 'twilio':
        send_whatsapp_alert_twilio(message)
    elif ALERT_SERVICE == 'telegram':
        send_telegram_message(message)
    else:
        logging.error("Unknown alert service specified: %s", ALERT_SERVICE)

def send_whatsapp_alert_twilio(message):
    """Sends a WhatsApp alert via Twilio."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, TARGET_WHATSAPP_NUMBER]):
        logging.error("Twilio configuration is incomplete.")
        return
    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            body=message,
            to=f"whatsapp:{TARGET_WHATSAPP_NUMBER}"
        )
        logging.info("WhatsApp message sent via Twilio: %s", msg.sid)
    except Exception as e:
        logging.error("Failed to send WhatsApp message via Twilio: %s", e)

if __name__ == "__main__":
    try:
        startup_message = f"Monitoring started for {PROTON_DRIVE_URL}"
        logging.info(startup_message)
        send_telegram_message(startup_message)
        while True:
            check_for_new_items()
            time.sleep(60)  # Check every 60 seconds
    except KeyboardInterrupt:
        shutdown_message = "Monitoring script has been stopped."
        logging.info(shutdown_message)
        send_telegram_message(shutdown_message)
    except Exception as e:
        error_message = f"An error occurred: {e}"
        logging.error(error_message)
