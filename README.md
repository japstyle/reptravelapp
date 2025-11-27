# Transfer-Aware Train Route Comparison App

A web app that helps you choose the best train route by considering **transfer convenience**, not just travel time.

## The Problem

Traditional route planners focus on the fastest route, but they ignore a critical factor: **how difficult the transfer is**. 

Two routes might take similar time on paper, but:
- One requires a 5-minute walk through a crowded multi-level station like Ikebukuro
- Another uses a simple same-platform transfer at Nerima

Which would you prefer?

## The Solution

This app scores routes based on:
- 🚶 **Walking distance** during transfers
- 🪜 **Stairs and floors** you need to navigate
- 👥 **Crowd levels** at major stations
- 🤔 **Confusion factor** (how easy it is to find your next platform)
- 🎯 **Platform type** (same platform, cross-platform, or different platform)

The result? A "felt time" that reflects how the journey actually feels, not just how long it takes.

## Example: Shibuya → Tokorozawa

### Route 1: Via Ikebukuro (Fukutoshin)
- Ride: Shibuya → Ikebukuro (15 min)
- **Transfer at Ikebukuro**: 380m walk, 2 floors, crowded, confusing (≈6 min penalty)
- Ride: Ikebukuro → Tokorozawa (21 min)
- **Total felt time: ≈42 minutes**

### Route 2: Via Nerima (Fukutoshin, same platform) ✨
- Ride: Shibuya → Nerima (20 min)
- **Transfer at Nerima**: 45m walk, same platform, easy (≈1 min penalty)
- Ride: Nerima → Tokorozawa (16 min)
- **Total felt time: ≈37 minutes**

Even though Route 2 has a longer ride time, the easy transfer makes it the better choice!

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your ODPT API token:
```bash
# Create .env file
echo "ODPT_TOKEN=your_token_here" > .env
```

3. Fetch station data:
```bash
python scripts/fetch_odpt.py
```

4. Run the app:
```bash
uvicorn main:app --reload
```

5. Open your browser to `http://localhost:8000/route-compare`

## Features

- 🔍 **Multi-route comparison**: See 3-5 alternative routes at once
- 📊 **Visual scoring**: Understand why one route is better than another
- ⚡ **Transfer database**: Detailed data for major Tokyo transfer stations
- 🎨 **Clean UI**: Side-by-side comparison with clear visual indicators

## API Endpoints

- `GET /route-compare?origin=Shibuya&destination=Tokorozawa` - Web UI for route comparison
- `POST /compare` - API endpoint for programmatic route scoring
- `POST /score-route` - Score a single route candidate
- `GET /stations` - List all stations from ODPT
- `GET /lines` - List all train lines from ODPT

## Transfer Database

The app uses a curated database of transfer characteristics at major stations (`data/transfers.json`). Each transfer includes:

```json
{
  "station": "Ikebukuro",
  "from_line": "TokyoMetro.Fukutoshin",
  "to_line": "Seibu.Ikebukuro",
  "distance_m": 380,
  "floors": 2,
  "stairs": 3,
  "escalators": 2,
  "crowd_factor": 1.4,
  "confusion_level": 3.5,
  "platform_type": "different_platform"
}
```

## Extending the App

### Add More Routes

Edit `route_finder.py` to add hardcoded route patterns, or implement dynamic route finding using ODPT station connection data.

### Add More Transfer Data

Edit `data/transfers.json` to add more transfer points. Measure the characteristics yourself or use station layout information.

### Customize Scoring

Edit `scoring.py` to adjust the scoring formula based on your preferences:
- Walking speed
- Stair penalties
- Crowd tolerance
- Platform type bonuses

## Future Enhancements

- 🗺️ **Dynamic route finding**: Use ODPT connection data to generate routes automatically
- 📱 **Mobile app**: Native iOS/Android apps
- 🕐 **Time-based scoring**: Different penalties for rush hour vs off-peak
- 🌐 **Multi-language**: Support for more languages beyond Japanese/English
- 💾 **User preferences**: Save your transfer preferences and favorite routes
- 📈 **Historical data**: Learn from actual user journey times

## Tech Stack

- **Backend**: FastAPI (Python)
- **Data Source**: Open Data Challenge for Public Transportation in Tokyo (ODPT)
- **Frontend**: HTML/CSS with Jinja2 templates
- **Deployment**: Can be deployed to any Python hosting service

## License

MIT

## Contributing

Contributions welcome! Especially:
- More transfer data for stations
- Route finding algorithms
- UI/UX improvements
- Mobile apps
