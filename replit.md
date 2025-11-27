# Transfer-Aware Train Route Comparison App

## Overview
This is a FastAPI web application that helps users choose the best train route in Tokyo by considering transfer convenience, not just travel time. The app scores routes based on walking distance, stairs, crowd levels, confusion factor, and platform type during transfers.

## Recent Changes
- **2024-11-26**: Imported from GitHub and configured for Replit environment
  - Installed Python 3.11 and all required dependencies
  - Added jinja2 to requirements.txt
  - Created run.py to start FastAPI on 0.0.0.0:5000
  - Configured workflow to run the FastAPI server
  - Set up for deployment

## Project Architecture

### Backend (FastAPI)
- **main.py**: Main FastAPI application with all endpoints
  - `/` - Homepage
  - `/route-compare` - Main route comparison UI
  - `/search` - Station search page
  - `/stations` - API endpoint to list all stations
  - `/lines` - API endpoint to list all train lines
  - `/score-route` - Score a single route candidate
  - `/compare` - Compare multiple routes

### Core Logic
- **scoring.py**: Route scoring algorithm that calculates "felt time" based on transfer characteristics
- **route_finder.py**: Finds multiple route alternatives (currently hardcoded for demo routes)

### Data
- **data/stations.json**: Station data from ODPT API (must be fetched)
- **data/train_lines.json**: Train line data from ODPT API (must be fetched)
- **data/transfers.json**: Transfer characteristics database (walking distance, floors, stairs, crowds, etc.)

### Frontend
- **templates/**: Jinja2 HTML templates
  - index.html - Homepage
  - route_compare.html - Route comparison interface
  - search.html - Station search

### Scripts
- **scripts/fetch_odpt.py**: Fetches station and train line data from ODPT API (requires API token)

## Tech Stack
- Python 3.11
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Jinja2 (templating)
- Pydantic (data validation)
- ODPT API (Open Data Challenge for Public Transportation in Tokyo)

## Running the App
The app runs automatically via the configured workflow on port 5000.

### Manual Run
```bash
python run.py
```

### Fetching Station Data (Optional)
The app works out of the box with hardcoded demo routes (e.g., Shibuya → Tokorozawa).

To enable full station search and access to real ODPT data:
1. Get an API token from https://developer.odpt.org/
2. Create a .env file with: `ODPT_TOKEN=your_token_here`
3. Run: `python scripts/fetch_odpt.py`

**Without ODPT data:**
- ✅ Homepage and route comparison UI work normally
- ✅ Demo routes (Shibuya → Tokorozawa) work with transfer scoring
- ✅ Search page loads but returns no results
- ❌ `/stations` and `/lines` API endpoints return 404

**With ODPT data:**
- ✅ Full station search functionality
- ✅ Access to all station and line data via API

## User Preferences
None configured yet.

## Current State
- ✅ Application running on port 5000
- ✅ All dependencies installed
- ⚠️ Station data not yet fetched (optional - requires ODPT API token)
- ✅ Sample transfer data available in data/transfers.json
- ✅ Demo route working: Shibuya → Tokorozawa
