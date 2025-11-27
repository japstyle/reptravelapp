from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
import json

from scoring import score_route
from route_finder import find_routes, get_all_stations, get_all_lines

app = FastAPI(title='Japan Route Optimizer')
templates = Jinja2Templates(directory="templates")
DATA_DIR = Path('data')

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get('/lines')
def lines():
    p = DATA_DIR / 'train_lines.json'
    if not p.exists():
        raise HTTPException(404, 'train_lines.json not found; run scripts/fetch_odpt.py')
    return json.loads(p.read_text(encoding='utf-8'))

@app.get('/stations')
def stations():
    p = DATA_DIR / 'stations.json'
    if not p.exists():
        raise HTTPException(404, 'stations.json not found; run scripts/fetch_odpt.py')
    return json.loads(p.read_text(encoding='utf-8'))

@app.get('/api/network-stations')
def network_stations():
    """Get all available stations from the route finder network with bilingual names."""
    stations_data = []
    station_names = get_all_stations()
    
    # Load stations.json for Japanese names
    stations_path = DATA_DIR / 'stations.json'
    stations_map = {}
    
    if stations_path.exists():
        stations_json = json.loads(stations_path.read_text(encoding='utf-8'))
        for station in stations_json:
            title = station.get('odpt:stationTitle', {})
            en_name = title.get('en', '')
            ja_name = title.get('ja', '')
            if en_name:
                # Normalize the English name to match network.json format
                normalized = en_name.lower().replace(' ', '-')
                stations_map[en_name] = ja_name
                stations_map[normalized] = ja_name
    
    # Build structured station data
    for station_name in station_names:
        normalized_id = station_name.lower().replace(' ', '-')
        ja_name = stations_map.get(station_name, stations_map.get(normalized_id, ''))
        
        stations_data.append({
            'id': normalized_id,
            'name_en': station_name,
            'name_ja': ja_name
        })
    
    return {"stations": stations_data}

@app.get('/api/network-lines')
def network_lines():
    """Get all available lines from the route finder network."""
    return {"lines": get_all_lines()}

class RouteCandidate(BaseModel):
    segments: List[Dict[str, Any]]

@app.post('/score-route')
def post_score(candidate: RouteCandidate):
    return score_route(candidate.dict())

@app.post('/compare')
def compare(candidates: List[RouteCandidate]):
    out = []
    for c in candidates:
        s = score_route(c.dict())
        out.append({'candidate': c, 'score': s})
    out.sort(key=lambda x: x['score']['total_seconds'])
    return out

@app.get("/search")
def search_page(request: Request, q: str | None = None):
    p = DATA_DIR / "stations.json"
    stations = []
    
    if p.exists():
        stations = json.loads(p.read_text(encoding="utf-8"))

    results = []
    if q:
        q_low = q.lower()
        for st in stations:
            title = st.get("odpt:stationTitle", {})
            ja = title.get("ja", "")
            en = title.get("en", "")

            if q_low in ja.lower() or q_low in en.lower():
                results.append({
                    "id": st.get("owl:sameAs"),
                    "ja": ja,
                    "en": en,
                })

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": q or "",
            "results": results
        }
    )

from realtime_data import get_train_information_dict

# ... (existing code) ...

from fastapi import Header
from i18n import get_translator, get_best_match_language
# ... (imports)

# ... (existing code) ...

@app.get("/route-compare")
def route_compare_page(request: Request, origin: str | None = None, destination:str | None = None, accept_language: str | None = Header(None)):
    """Main route comparison UI."""
    routes = []
    scored_routes = []
    error_message = None
    
    # i18n setup
    lang = get_best_match_language(accept_language)
    _ = get_translator(lang)

    if origin and destination:
        # Validate inputs
        if not origin.strip():
            error_message = _("error_enter_origin")
        elif not destination.strip():
            error_message = _("error_enter_destination")
        else:
            # Normalize station names
            from route_finder import _normalize_station, _find_station
            
            origin_normalized = _find_station(origin)
            destination_normalized = _find_station(destination)
            
            # Check if stations exist
            if not origin_normalized:
                error_message = _("error_station_not_found", station_name=origin)
            elif not destination_normalized:
                error_message = _("error_station_not_found", station_name=destination)
            elif origin_normalized == destination_normalized:
                error_message = _("error_origin_destination_same")
            else:
                # Find route alternatives
                routes = find_routes(origin, destination)
                
                # Get real-time train information
                train_info = get_train_information_dict()
                normal_statuses = {"平常どおり運転", "平常運行", "遅延はありません"}
                
                # Add delay info to routes
                for route in routes:
                    for segment in route.get("segments", []):
                        if segment.get("type") == "ride":
                            delay_text = ""
                            for line_id in segment.get("line_ids", []):
                                odpt_line_id = f"odpt.TrainInformation:{line_id}"
                                status = train_info.get(odpt_line_id)
                                if status and not any(normal in status for normal in normal_statuses):
                                    delay_text = status
                                    break
                            segment["delay_info"] = delay_text

                # Score each route
                for route in routes:
                    score = score_route(route)
                    scored_routes.append({
                        'name': route.get('name', 'Unnamed Route'),
                        'segments': route['segments'],
                        'score': score,
                        'total_minutes': round(score['total_seconds'] / 60, 1),
                        'actual_ride_minutes': sum(s['duration_seconds'] for s in route['segments']) / 60
                    })
                
                scored_routes.sort(key=lambda x: x['score']['total_seconds'])
    elif origin or destination:
        if not origin or not origin.strip():
            error_message = _("error_enter_origin")
        elif not destination or not destination.strip():
            error_message = _("error_enter_destination")
    
    available_stations = get_all_stations()
    
    context = {
        "request": request,
        "origin": origin or "",
        "destination": destination or "",
        "routes": scored_routes,
        "available_stations": available_stations,
        "error_message": error_message,
        "_": _
    }
    return templates.TemplateResponse("route_compare.html", context)

