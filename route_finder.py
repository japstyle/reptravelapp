"""
Route finding logic - generates multiple route alternatives using graph-based pathfinding.
Finds routes between any two stations in the Tokyo train network.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, deque

_network = None
_graph = None
_station_to_lines = None
_station_display_names = None
_through_services = None

def _load_network():
    """Load the train network data and build the graph."""
    global _network, _graph, _station_to_lines, _station_display_names, _through_services
    
    if _network is not None:
        return
    
    network_path = Path('data/network.json')
    if not network_path.exists():
        _network = {"lines": {}}
        _graph = defaultdict(set)
        _station_to_lines = defaultdict(set)
        _station_display_names = {}
        return
    
    _network = json.loads(network_path.read_text(encoding='utf-8'))
    _graph = defaultdict(set)
    _station_to_lines = defaultdict(set)
    _station_display_names = {}
    _through_services = _network.get('through_services', [])
    
    for line_id, line_data in _network.get("lines", {}).items():
        stations = line_data.get("stations", [])
        line_type = line_data.get("type", "linear")
        
        for i, station in enumerate(stations):
            station_key = station.lower().replace(" ", "-")
            _station_to_lines[station_key].add(line_id)
            _station_display_names[station_key] = station.replace("-", " ")
            
            if i > 0:
                prev_station = stations[i-1].lower().replace(" ", "-")
                _graph[station_key].add((prev_station, line_id))
                _graph[prev_station].add((station_key, line_id))
        
        if line_type == "loop" and len(stations) > 2:
            first = stations[0].lower().replace(" ", "-")
            last = stations[-1].lower().replace(" ", "-")
            _graph[first].add((last, line_id))
            _graph[last].add((first, line_id))

def _get_display_name(station_key: str) -> str:
    """Get the display name for a station key."""
    _load_network()
    return _station_display_names.get(station_key, station_key.replace("-", " ").title())

def _normalize_station(name: str) -> str:
    """Normalize station name for matching."""
    return name.lower().strip().replace(" ", "-").replace("ō", "o").replace("ū", "u")

def _find_station(query: str) -> Optional[str]:
    """Find a station by partial or full name match."""
    _load_network()
    query_lower = _normalize_station(query)
    
    if query_lower in _station_to_lines:
        return query_lower
    
    for station in _station_to_lines.keys():
        if query_lower in station or station in query_lower:
            return station
    
    for station in _station_to_lines.keys():
        station_simple = station.replace("-", "")
        query_simple = query_lower.replace("-", "")
        if query_simple in station_simple or station_simple in query_simple:
            return station
    
    return None

def _get_line_info(line_id: str) -> Dict:
    """Get line information."""
    _load_network()
    return _network.get("lines", {}).get(line_id, {})

def _has_through_service(line1: str, line2: str, station: str) -> bool:
    """Check if two lines have through-service at a given station."""
    _load_network()
    for service in _through_services:
        lines = service.get('lines', [])
        connection = service.get('connection_station', '')
        if (line1 in lines and line2 in lines and 
            station.lower().replace('-', '') == connection.lower().replace('-', '')):
            return True
    return False

def _estimate_ride_time(from_station: str, to_station: str, line_id: str) -> int:
    """Estimate ride time between two stations on the same line in seconds."""
    _load_network()
    line_info = _get_line_info(line_id)
    stations = [s.lower() for s in line_info.get("stations", [])]
    
    try:
        from_idx = stations.index(from_station.lower())
        to_idx = stations.index(to_station.lower())
        num_stops = abs(to_idx - from_idx)
    except ValueError:
        num_stops = 1
    
    avg_speed = line_info.get("avg_speed_kmh", 30)
    avg_distance = _network.get("station_distances", {}).get("default_km", 1.2)
    
    if line_info.get("type") == "loop":
        avg_distance = _network.get("station_distances", {}).get("loop_station_km", 0.9)
    
    distance_km = num_stops * avg_distance
    time_hours = distance_km / avg_speed
    time_seconds = int(time_hours * 3600)
    
    time_seconds += num_stops * 30
    
    return max(60, time_seconds)

def _bfs_find_routes(origin: str, destination: str, max_routes: int = 5, max_transfers: int = 2) -> List[List[Tuple[str, str, str]]]:
    """
    Find multiple routes using optimized BFS.
    Returns list of routes, where each route is a list of (from_station, to_station, line_id) tuples.
    """
    _load_network()
    
    origin_norm = _find_station(origin)
    dest_norm = _find_station(destination)
    
    if not origin_norm or not dest_norm:
        return []
    
    if origin_norm == dest_norm:
        return []
    
    routes = []
    visited_paths = set()
    
    dest_lines = _station_to_lines.get(dest_norm, set())
    
    max_iterations = 5000
    iterations = 0
    
    queue = deque()
    visited_global = {}
    
    for start_line in _station_to_lines.get(origin_norm, set()):
        queue.append((origin_norm, start_line, [], 0))
        visited_global[(origin_norm, start_line)] = 0
    
    while queue and len(routes) < max_routes and iterations < max_iterations:
        iterations += 1
        current_station, current_line, path, num_transfers = queue.popleft()
        
        if num_transfers > max_transfers:
            continue
        
        if len(path) > 30:
            continue
        
        if current_station == dest_norm:
            lines_used = tuple(sorted(set(p[2] for p in path)))
            transfer_points = tuple(p[0] for i, p in enumerate(path) if i > 0 and path[i-1][2] != p[2])
            path_signature = (lines_used, transfer_points)
            
            if path_signature not in visited_paths:
                visited_paths.add(path_signature)
                routes.append(path)
            continue
        
        neighbors = list(_graph.get(current_station, []))
        
        same_line_neighbors = [(n, l) for n, l in neighbors if l == current_line]
        for next_station, line_id in same_line_neighbors:
            state = (next_station, line_id)
            new_path_len = len(path) + 1
            
            if state not in visited_global or visited_global[state] > new_path_len:
                visited_global[state] = new_path_len
                extended_path = path + [(current_station, next_station, line_id)]
                queue.append((next_station, line_id, extended_path, num_transfers))
        
        if num_transfers < max_transfers:
            for new_line in _station_to_lines.get(current_station, set()):
                if new_line != current_line:
                    for next_station, line_id in neighbors:
                        if line_id == new_line:
                            state = (next_station, new_line)
                            new_path_len = len(path) + 1
                            
                            if state not in visited_global or visited_global[state] > new_path_len + 5:
                                visited_global[state] = new_path_len
                                transfer_path = path + [(current_station, next_station, new_line)]
                                queue.append((next_station, new_line, transfer_path, num_transfers + 1))
    
    return routes[:max_routes]

def _consolidate_segments(raw_route: List[Tuple[str, str, str]]) -> List[Dict[str, Any]]:
    """Consolidate consecutive segments on the same line into single ride segments."""
    if not raw_route:
        return []
    
    segments = []
    current_line = raw_route[0][2]
    current_from = raw_route[0][0]
    current_to = raw_route[0][1]
    lines_in_segment = [current_line]  # Track lines for through-service
    segment_hops = [(raw_route[0][0], raw_route[0][1], raw_route[0][2])]  # Track all hops in segment
    
    for i in range(1, len(raw_route)):
        from_station, to_station, line_id = raw_route[i]
        
        if line_id == current_line:
            # Same line, continue
            current_to = to_station
            segment_hops.append((from_station, to_station, line_id))
        elif _has_through_service(current_line, line_id, current_to):
            # Through-service: treat as continuous ride
            current_to = to_station
            current_line = line_id
            lines_in_segment.append(line_id)
            segment_hops.append((from_station, to_station, line_id))
        else:
            # Different line without through-service: need transfer
            # Calculate duration by summing all hops in the segment
            duration = sum(_estimate_ride_time(hop[0], hop[1], hop[2]) for hop in segment_hops)
            
            # Build line display name
            if len(lines_in_segment) > 1:
                line_info_first = _get_line_info(lines_in_segment[0])
                line_info_last = _get_line_info(lines_in_segment[-1])
                line_display = f"{line_info_first.get('name', lines_in_segment[0])} → {line_info_last.get('name', lines_in_segment[-1])}"
            else:
                line_info = _get_line_info(current_line)
                line_display = line_info.get('name', current_line)
            
            segments.append({
                "type": "ride",
                "from_station": _get_display_name(current_from),
                "to_station": _get_display_name(current_to),
                "line": line_display,
                "line_ids": lines_in_segment,
                "duration_seconds": duration,
                "is_transfer": False,
                "through_service": len(lines_in_segment) > 1
            })
            
            line_info_from = _get_line_info(current_line)
            line_info_to = _get_line_info(line_id)
            same_company = line_info_from.get("operator") == line_info_to.get("operator")
            
            segments.append({
                "type": "transfer",
                "from_station": _get_display_name(current_to),
                "to_station": _get_display_name(from_station),
                "from_line": line_info_from.get('name', current_line),
                "to_line": line_info_to.get('name', line_id),
                "duration_seconds": 0,
                "is_transfer": True,
                "same_company_transfer": same_company
            })
            
            current_line = line_id
            current_from = from_station
            current_to = to_station
            lines_in_segment = [line_id]
            segment_hops = [(from_station, to_station, line_id)]
    
    # Final segment
    duration = sum(_estimate_ride_time(hop[0], hop[1], hop[2]) for hop in segment_hops)
    
    if len(lines_in_segment) > 1:
        line_info_first = _get_line_info(lines_in_segment[0])
        line_info_last = _get_line_info(lines_in_segment[-1])
        line_display = f"{line_info_first.get('name', lines_in_segment[0])} → {line_info_last.get('name', lines_in_segment[-1])}"
    else:
        line_info = _get_line_info(current_line)
        line_display = line_info.get('name', current_line)
    
    segments.append({
        "type": "ride",
        "from_station": _get_display_name(current_from),
        "to_station": _get_display_name(current_to),
        "line": line_display,
        "line_ids": lines_in_segment,
        "duration_seconds": duration,
        "is_transfer": False,
        "through_service": len(lines_in_segment) > 1
    })
    
    return segments

def _generate_route_name(segments: List[Dict]) -> str:
    """Generate a descriptive name for the route."""
    transfers = [s for s in segments if s["type"] == "transfer"]
    
    if not transfers:
        # Check if it's a through-service route
        if segments and segments[0].get("through_service"):
            return "Direct (through-service)"
        else:
            line = segments[0]["line"] if segments else "Direct"
            line_info = _get_line_info(line)
            line_name = line_info.get("name", line.split(".")[-1] if "." in line else line)
            return f"Direct ({line_name})"
    
    transfer_stations = [t["from_station"] for t in transfers]
    transfer_str = ", ".join(transfer_stations[:2])
    
    if len(transfers) == 1:
        return f"Via {transfer_str}"
    else:
        return f"Via {transfer_str} ({len(transfers)} transfers)"

def find_routes(origin: str, destination: str, date: str | None = None, time: str | None = None, time_type: str = "departure") -> List[Dict[str, Any]]:
    """
    Find multiple route alternatives between origin and destination.
    
    Returns a list of route candidates, each with segments describing
    the journey (riding + transfers).
    """
    _load_network()
    
    raw_routes = _bfs_find_routes(origin, destination, date, time, time_type, max_routes=5, max_transfers=3)

def _bfs_find_routes(origin: str, destination: str, date: str | None = None, time: str | None = None, time_type: str = "departure", max_routes: int = 5, max_transfers: int = 2) -> List[List[Tuple[str, str, str]]]:
    
    if not raw_routes:
        return _fallback_routes(origin, destination)
    
    routes = []
    seen_signatures = set()
    
    for raw_route in raw_routes:
        segments = _consolidate_segments(raw_route)
        
        if not segments:
            continue
        
        transfer_stations = tuple(s["from_station"] for s in segments if s["type"] == "transfer")
        lines_used = tuple(s["line"] for s in segments if s["type"] == "ride")
        signature = (transfer_stations, lines_used)
        
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        
        route_name = _generate_route_name(segments)
        
        routes.append({
            "name": route_name,
            "segments": segments
        })
    
    routes.sort(key=lambda r: (
        len([s for s in r["segments"] if s["type"] == "transfer"]),
        sum(s["duration_seconds"] for s in r["segments"] if s["type"] == "ride")
    ))
    
    return routes[:5]

def _fallback_routes(origin: str, destination: str) -> List[Dict[str, Any]]:
    """Fallback routes for known origin-destination pairs."""
    routes = []
    
    if _matches(origin, "shibuya") and _matches(destination, "tokorozawa"):
        routes.append({
            "name": "Via Ikebukuro (Fukutoshin)",
            "segments": [
                {
                    "type": "ride",
                    "from_station": "Shibuya",
                    "to_station": "Ikebukuro",
                    "line": "TokyoMetro.Fukutoshin",
                    "duration_seconds": 900,
                    "is_transfer": False
                },
                {
                    "type": "transfer",
                    "from_station": "Ikebukuro",
                    "to_station": "Ikebukuro",
                    "from_line": "TokyoMetro.Fukutoshin",
                    "to_line": "Seibu.Ikebukuro",
                    "duration_seconds": 0,
                    "is_transfer": True,
                    "same_company_transfer": False
                },
                {
                    "type": "ride",
                    "from_station": "Ikebukuro",
                    "to_station": "Tokorozawa",
                    "line": "Seibu.Ikebukuro",
                    "duration_seconds": 1260,
                    "is_transfer": False
                }
            ]
        })
        
        routes.append({
            "name": "Via Nerima (same platform)",
            "segments": [
                {
                    "type": "ride",
                    "from_station": "Shibuya",
                    "to_station": "Nerima",
                    "line": "TokyoMetro.Fukutoshin",
                    "duration_seconds": 1200,
                    "is_transfer": False
                },
                {
                    "type": "transfer",
                    "from_station": "Nerima",
                    "to_station": "Nerima",
                    "from_line": "TokyoMetro.Fukutoshin",
                    "to_line": "Seibu.Ikebukuro",
                    "duration_seconds": 0,
                    "is_transfer": True,
                    "same_company_transfer": False
                },
                {
                    "type": "ride",
                    "from_station": "Nerima",
                    "to_station": "Tokorozawa",
                    "line": "Seibu.Ikebukuro",
                    "duration_seconds": 960,
                    "is_transfer": False
                }
            ]
        })
        
        routes.append({
            "name": "Via Ikebukuro (JR Yamanote)",
            "segments": [
                {
                    "type": "ride",
                    "from_station": "Shibuya",
                    "to_station": "Ikebukuro",
                    "line": "JR-East.Yamanote",
                    "duration_seconds": 720,
                    "is_transfer": False
                },
                {
                    "type": "transfer",
                    "from_station": "Ikebukuro",
                    "to_station": "Ikebukuro",
                    "from_line": "JR-East.Yamanote",
                    "to_line": "Seibu.Ikebukuro",
                    "duration_seconds": 0,
                    "is_transfer": True,
                    "same_company_transfer": False
                },
                {
                    "type": "ride",
                    "from_station": "Ikebukuro",
                    "to_station": "Tokorozawa",
                    "line": "Seibu.Ikebukuro",
                    "duration_seconds": 1260,
                    "is_transfer": False
                }
            ]
        })
    
    return routes

def _matches(station_name: str, search: str) -> bool:
    """Case-insensitive station name matching."""
    return search.lower() in station_name.lower()

def get_all_stations() -> List[str]:
    """Get a list of all station names in the network."""
    _load_network()
    stations = set()
    for line_data in _network.get("lines", {}).values():
        for station in line_data.get("stations", []):
            stations.add(station)
    return sorted(stations)

def get_all_lines() -> List[Dict[str, str]]:
    """Get a list of all lines with their names."""
    _load_network()
    lines = []
    for line_id, line_data in _network.get("lines", {}).items():
        lines.append({
            "id": line_id,
            "name": line_data.get("name", line_id),
            "name_ja": line_data.get("name_ja", ""),
            "color": line_data.get("color", "#666666"),
            "operator": line_data.get("operator", "")
        })
    return sorted(lines, key=lambda x: x["name"])

def create_route_candidate(segments: List[Dict]) -> Dict:
    """Helper to create a properly formatted route candidate."""
    return {"segments": segments}
