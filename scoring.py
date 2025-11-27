# scoring.py

"""
Route scoring logic for the Japan Route Optimizer.
This converts human comfort into math.
"""

import json
from pathlib import Path
from typing import Optional, Dict

HELL_STATIONS = {
    "Otemachi": 90,       # 90 seconds penalty
    "Shinjuku": 75,
    "Tokyo": 60,
    "Iidabashi": 45,
}

# Load transfer database
_transfer_db = None

def _load_transfers():
    global _transfer_db
    if _transfer_db is None:
        transfer_path = Path('data/transfers.json')
        if transfer_path.exists():
            _transfer_db = json.loads(transfer_path.read_text(encoding='utf-8'))
        else:
            _transfer_db = []
    return _transfer_db

def find_transfer_data(station: str, from_line: str, to_line: str) -> Optional[Dict]:
    """Find transfer data for a specific station and line combination."""
    transfers = _load_transfers()
    for t in transfers:
        if (t['station'].lower() == station.lower() and 
            t['from_line'] == from_line and 
            t['to_line'] == to_line):
            return t
        # Also check reverse direction
        if (t['station'].lower() == station.lower() and 
            t['from_line'] == to_line and 
            t['to_line'] == from_line):
            return t
    return None

def calculate_transfer_time(transfer_data: Dict) -> float:
    """
    Calculate realistic transfer time based on physical characteristics.
    
    Formula:
    - Base walking time: distance_m / 60 (assuming 60m/min walking speed)
    - Floor penalty: 15 seconds per floor
    - Stair penalty: 10 seconds per staircase (in addition to floor time)
    - Escalator bonus: -5 seconds per escalator (makes floors easier)
    - Crowd multiplier: base_time * crowd_factor
    - Confusion penalty: confusion_level * 10 seconds
    - Platform type bonus/penalty
    """
    distance_m = transfer_data.get('distance_m', 0)
    floors = transfer_data.get('floors', 0)
    stairs = transfer_data.get('stairs', 0)
    escalators = transfer_data.get('escalators', 0)
    crowd_factor = transfer_data.get('crowd_factor', 1.0)
    confusion_level = transfer_data.get('confusion_level', 0)
    platform_type = transfer_data.get('platform_type', 'different_platform')
    
    # Base walking time (seconds)
    base_walk = (distance_m / 60) * 60  # 60m/min = 1m/s
    
    # Vertical movement
    floor_penalty = floors * 15
    stair_penalty = stairs * 10
    escalator_bonus = escalators * -5
    
    # Calculate before crowd factor
    pre_crowd_time = base_walk + floor_penalty + stair_penalty + escalator_bonus
    
    # Apply crowd factor
    crowded_time = pre_crowd_time * crowd_factor
    
    # Confusion penalty (getting lost, checking signs)
    confusion_penalty = confusion_level * 10
    
    # Platform type adjustment
    platform_penalty = 0
    if platform_type == 'same_platform':
        platform_penalty = -30  # Easy transfer bonus
    elif platform_type == 'cross_platform':
        platform_penalty = 0    # Neutral
    elif platform_type == 'different_platform':
        platform_penalty = 20   # Extra navigation time
    
    total = crowded_time + confusion_penalty + platform_penalty
    
    return max(30, total)  # Minimum 30 seconds for any transfer

def score_segment(segment: dict) -> dict:
    """
    A segment is expected to contain:
    - duration_seconds: int (riding time)
    - from_station: str
    - to_station: str
    - from_line: str (optional, for transfer lookup)
    - to_line: str (optional, for transfer lookup)
    - is_transfer: bool (whether this segment is a transfer)
    
    Legacy fields (still supported):
    - walk_seconds: int
    - stairs: int (0 = none, 1 = some, 2 = many)
    - same_company_transfer: bool
    """

    base = segment.get("duration_seconds", 0)
    from_s = segment.get("from_station", "")
    to_s = segment.get("to_station", "")
    from_line = segment.get("from_line", "")
    to_line = segment.get("to_line", "")
    is_transfer = segment.get("is_transfer", False)
    
    # Initialize penalties
    walk_penalty = 0
    stairs_penalty = 0
    transfer_penalty = 0
    same_company_bonus = 0
    hell_penalty = 0
    
    # If this is a transfer segment, try to find detailed transfer data
    if is_transfer and from_line and to_line:
        # Try to find in transfer database
        transfer_data = find_transfer_data(from_s, from_line, to_line)
        if transfer_data:
            # Use detailed transfer calculation
            transfer_penalty = calculate_transfer_time(transfer_data)
        else:
            # Fall back to legacy calculation
            walk = segment.get("walk_seconds", 120)  # Default 2min transfer
            stairs = segment.get("stairs", 1)
            walk_penalty = walk * 1.8
            if stairs == 1:
                stairs_penalty = 20
            elif stairs >= 2:
                stairs_penalty = 45
            transfer_penalty = walk_penalty + stairs_penalty
        
        # Same company bonus
        same_company = segment.get("same_company_transfer", False)
        same_company_bonus = -20 if same_company else 0
    else:
        # Regular segment (riding), check for hell stations
        if from_s in HELL_STATIONS:
            hell_penalty += HELL_STATIONS[from_s]
        if to_s in HELL_STATIONS:
            hell_penalty += HELL_STATIONS[to_s]

    segment_score = (
        base +
        transfer_penalty +
        hell_penalty +
        same_company_bonus
    )

    return {
        "base": base,
        "transfer_penalty": transfer_penalty,
        "hell_penalty": hell_penalty,
        "same_company_bonus": same_company_bonus,
        "total": segment_score
    }


def score_route(route: dict) -> dict:
    """
    Expects:
    { "segments": [ { ... }, { ... } ] }
    """
    segments = route.get("segments", [])
    breakdown = []
    total = 0

    for seg in segments:
        result = score_segment(seg)
        breakdown.append(result)
        total += result["total"]

    return {
        "total_seconds": total,
        "segments": breakdown
    }
