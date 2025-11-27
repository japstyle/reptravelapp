import os
import json
from pathlib import Path
import requests
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Get the API base URL and token from environment variables
BASE = os.getenv('ODPT_BASE', 'https://api.odpt.org/api/v4')
TOKEN = os.getenv('ODPT_TOKEN')
if not TOKEN:
    raise SystemExit('Set ODPT_TOKEN in .env')

# Define the directory for storing data
TMP_DIR = Path('/tmp')

# Define headers for the API request
HEADERS = {'Accept': 'application/json'}
CACHE_FILE = TMP_DIR / 'train_information.json'
RAW_CACHE_FILE = TMP_DIR / 'train_information_raw.json'
CACHE_DURATION_SECONDS = 5 * 60  # 5 minutes

def _process_train_info_to_dict(train_info):
    """Processes the raw train info list into a dictionary."""
    info_dict = {}
    for item in train_info:
        line_id = item.get('owl:sameAs')
        info_text = item.get('odpt:trainInformationText', {}).get('ja')
        if line_id and info_text:
            info_dict[line_id] = info_text
    return info_dict

def fetch_train_information():
    """
    Fetches train information data from the ODPT API.
    """
    endpoint = 'odpt:TrainInformation'
    params = {'acl:consumerKey': TOKEN}
    url = f"{BASE}/{endpoint}"
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        train_info = response.json()
        
        # Save the raw fetched data to a file
        with open(RAW_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(train_info, f, ensure_ascii=False, indent=2)
        
        return train_info
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching train information: {e}")
        return None

def get_train_information_dict():
    """
    Returns a dictionary of train information, from cache if available and recent,
    otherwise by fetching from the API.
    """
    if CACHE_FILE.exists():
        last_modified_time = CACHE_FILE.stat().st_mtime
        if (time.time() - last_modified_time) < CACHE_DURATION_SECONDS:
            print("Loading train information from cache.")
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)

    print("Fetching fresh train information.")
    raw_info = fetch_train_information()
    if raw_info:
        info_dict = _process_train_info_to_dict(raw_info)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(info_dict, f, ensure_ascii=False, indent=2)
        print(f"Successfully fetched and saved processed train information to {CACHE_FILE}")
        return info_dict
    else:
        print("Failed to fetch train information, returning empty dict.")
        return {}


if __name__ == '__main__':
    print("Getting train information dictionary...")
    train_information_dict = get_train_information_dict()
    if train_information_dict:
        print("Successfully got train information.")
    else:
        print("Failed to get train information.")

