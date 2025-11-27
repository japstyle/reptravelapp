# Quick Start Guide

## Your Question Answered

> "Should I stay on one line to Tokorozawa or change at Ikebukuro?"

**Answer: It depends on the transfer!** This app shows you exactly why.

### Example Results (Shibuya → Tokorozawa)

1. **Via Nerima (BEST)**: 36.5 min felt time
   - Same-platform transfer at Nerima (45m walk, super easy)
   - Even though the ride is slightly longer, the easy transfer wins!

2. **Via Ikebukuro (JR)**: 39.1 min felt time
   - Moderate transfer at Ikebukuro from JR to Seibu

3. **Via Ikebukuro (Fukutoshin)**: 47 min felt time
   - Complex transfer: 380m walk, 2 floors, crowded
   - Adds 11 minutes of felt time!

## Running the App

### 1. Start the server
```bash
uvicorn main:app --reload
```

### 2. Open your browser
Go to: `http://localhost:8000`

### 3. Try it out
- Click "Compare Routes Now"
- Enter: Origin = `Shibuya`, Destination = `Tokorozawa`
- Click "Compare Routes"

You'll see all three routes side-by-side with:
- Felt time vs actual time
- Transfer details (distance, floors, platform type)
- Visual indicators for easy vs complex transfers
- Score breakdown

## Understanding the Results

### Felt Time vs Actual Time
- **Actual Time**: Just the riding time
- **Felt Time**: What it actually feels like, including transfer difficulty

### Transfer Scoring
- **Same platform** (like Nerima): Almost no penalty
- **Cross platform**: Small penalty
- **Different platform** (like Ikebukuro): Big penalty based on distance, floors, crowds

### The Algorithm
Each transfer considers:
- Walking distance (60m/min base speed)
- Floors (15 sec per floor)
- Stairs (10 sec per staircase)
- Escalators (saves 5 sec per floor)
- Crowds (multiplies time by crowd factor)
- Confusion (10 sec per confusion point)
- Platform type (30 sec bonus for same platform)

## Test the Scoring

```bash
python test_scoring.py
```

This will verify:
- Transfer database lookups work
- Nerima is scored easier than Ikebukuro
- Route comparison selects the best route

## Adding Your Own Routes

### Option 1: Add to route_finder.py
Edit `route_finder.py` and add your route patterns in the `find_routes()` function.

### Option 2: Add transfer data
Edit `data/transfers.json` to add your local transfer stations with real measurements.

## API Usage

### Score a custom route
```bash
curl -X POST http://localhost:8000/score-route \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [
      {
        "type": "ride",
        "from_station": "Shibuya",
        "to_station": "Ikebukuro",
        "line": "JR-East.Yamanote",
        "duration_seconds": 720,
        "is_transfer": false
      },
      {
        "type": "transfer",
        "from_station": "Ikebukuro",
        "to_station": "Ikebukuro",
        "from_line": "JR-East.Yamanote",
        "to_line": "Seibu.Ikebukuro",
        "is_transfer": true
      }
    ]
  }'
```

## Tips

1. **For daily commutes**: Add your common transfers to `transfers.json` with real measurements
2. **Rush hour**: Increase `crowd_factor` in transfers during peak times
3. **Luggage**: Increase stair penalties if you have luggage
4. **Customization**: Edit scoring.py formulas to match your preferences

## Next Steps

1. Try the demo route: Shibuya → Tokorozawa
2. Add your own common routes to `route_finder.py`
3. Measure and add your local transfers to `transfers.json`
4. Customize scoring weights in `scoring.py`
5. Deploy to a server so you can access it on your phone!

Enjoy finding better routes! 🚉
