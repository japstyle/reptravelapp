import os, json
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()
BASE = os.getenv('ODPT_BASE', 'https://api.odpt.org/api/v4')
TOKEN = os.getenv('ODPT_TOKEN')
if not TOKEN:
    raise SystemExit('Set ODPT_TOKEN in .env')

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

HEADERS = {'Accept': 'application/json'}

def fetch(endpoint, params=None):
    params = params or {}
    params.update({'acl:consumerKey': TOKEN})
    url = f"{BASE}/{endpoint}"
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == '__main__':
    print('Fetching odpt:Railway...')
    railways = fetch('odpt:Railway')
    (DATA_DIR / 'train_lines.json').write_text(json.dumps(railways, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Saved data/train_lines.json')

    print('Fetching odpt:Station...')
    stations = fetch('odpt:Station')
    (DATA_DIR / 'stations.json').write_text(json.dumps(stations, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Saved data/stations.json')

    # Create starter transfers.json if not exists
    transfers_path = DATA_DIR / 'transfers.json'
    if not transfers_path.exists():
        starter = [
            {"station":"Ikebukuro","from_line":"Fukutoshin","to_line":"Seibu","distance_m":380,"floors":2,"stairs":3,"escalators":2,"crowd_factor":1.4,"confusion_level":3.5},
            {"station":"Nerima","from_line":"Fukutoshin","to_line":"Seibu","distance_m":45,"floors":0,"stairs":0,"escalators":0,"crowd_factor":1.1,"confusion_level":0.5},
            {"station":"Iidabashi","from_line":"Yurakucho","to_line":"Tozai","distance_m":260,"floors":1,"stairs":2,"escalators":1,"crowd_factor":1.5,"confusion_level":2.0},
            {"station":"Otemachi","from_line":"Yurakucho","to_line":"Tozai","distance_m":160,"floors":0,"stairs":1,"escalators":2,"crowd_factor":1.2,"confusion_level":1.0}
        ]
        transfers_path.write_text(json.dumps(starter, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Created data/transfers.json (starter entries)')

    print('Done.')
