# Vercel Deployment & Production Guide

This directory is pre-configured and 100% production-ready for deployment to **Vercel Serverless Functions**.

---

## ⚡ Option 1: Deploy with Vercel CLI (Fastest - 1 Command)

Open PowerShell in this directory (`C:\Users\hqsav\OneDrive\Desktop\apiscarper`):

```powershell
# 1. Preview Deployment (Login if prompted)
npx vercel

# 2. Production Deployment
npx vercel --prod
```

When prompted:
- **Set up and deploy?**: `y`
- **Which scope?**: Choose your Vercel account
- **Link to existing project?**: `n`
- **What's your project's name?**: `d247-cricket-api` (or any name)
- **In which directory is your code located?**: `./` (press Enter)
- **Want to modify these settings?**: `n`

Vercel will output your live URL:
`https://d247-cricket-api.vercel.app`

---

## 🐙 Option 2: Deploy via GitHub (Recommended for Auto-Deployments)

1. Initialize Git and commit the files:
```powershell
git init
git add .
git commit -m "Production-ready D247 & Cricket Scoreboard API for Vercel"
```

2. Create a repository on GitHub and push:
```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

3. Go to [vercel.com/new](https://vercel.com/new):
- Import your GitHub repository.
- Keep **Framework Preset** as **Other**.
- Root Directory: `./`
- Click **Deploy**!

Any future `git push` will automatically trigger a new deployment on Vercel.

---

## 💻 Option 3: Run Locally with Uvicorn (Development & Testing)

```powershell
# Start local server on port 8000
python -m uvicorn api.index:app --reload --port 8000
```

Once started, open in your browser:
- 📖 **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📑 **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 🔍 **Root Status**: [http://localhost:8000/](http://localhost:8000/)

---

## 🧪 Run Automated Route Validation

Before deploying, you can run the comprehensive local test suite verifying all 21 routes:

```powershell
python test_vercel_api.py
```

Expected Output:
```
================================================================================
                           VERCEL API ROUTE SUMMARY
================================================================================
 Total Routes Tested : 21
 Passed Routes       : 21 [SUCCESS]
 Failed Routes       : 0
 Success Rate        : 100.0%
================================================================================
```

---

## 🌐 Complete Vercel API Endpoints Reference

Once deployed (e.g. `https://your-api.vercel.app`):

### 1. General & Health
- `GET /` - Root info, endpoint dictionary & status
- `GET /health` - Uptime check (`{"status": "ok"}`)
- `GET /docs` - Interactive Swagger UI
- `GET /openapi.json` - OpenAPI 3.0 schema
- `GET /api/server/check` - Geo-IP, ISP & server connection telemetry

### 2. Live Sports & Fixtures (No Auth)
- `GET /api/matches?sport_id=4&inplay_only=true` - Live in-play cricket matches
- `GET /api/matches?sport_id=4` - All upcoming & live cricket fixtures
- `GET /api/tree` - Full tournament & sports hierarchy tree
- `GET /api/tabs` - Active sport tabs
- `GET /api/featured` - Marquee banner matches

### 3. Real-Time Odds & Markets (No Auth)
- `GET /api/odds/{game_id}` - Real-time Back/Lay orderbook prices, liquidity, Match Odds, Bookmaker rates, Fancy markets
- `GET /api/details/{game_id}` - League name, stream status, scorecard format

### 4. Cricket Live Score & Commentary (CloudFront - No Auth)
- `GET /api/score/bootstrap/{game_id}` - Score overview, toss, runs, wickets, overs, striker, bowler
- `GET /api/score/scorecard/{event_id}` - Full scorecard (all innings, batsmen, bowlers, wickets)
- `GET /api/score/overs/{event_id}?innings=1&limit=50` - Ball-by-ball delivery commentary (dots, 1s, 4s, 6s, wickets)
- `GET /api/score/commentary/{event_id}?limit=50` - Textual live play-by-play commentary
- `GET /api/score/lineup/{event_id}` - Playing XI, captain, wicketkeeper, bench players
- `GET /api/score/partnerships/{event_id}` - Batting partnerships per wicket
- `GET /api/score/charts/{event_id}` - Worm chart & run rate coordinates
- `GET /api/score/embed/{game_id}` - Responsive HTML iframe embed URL & code

### 5. Betting Utilities
- `POST /api/bet/payload` - Validates bet parameters and calculates liability/profit
- `GET /api/bet/user` - User balance, credit, exposure (requires `g_token` header/param)
- `GET /api/bet/book/{game_id}` - User open position on match (requires `g_token`)

---

## 🔒 Environment Variables (Optional)

In your Vercel Project Dashboard (**Settings -> Environment Variables**):
- `D247_CRYPTO_KEY`: Passphrase used for D247 CryptoJS AES encryption (Default is already pre-configured to `cae7b808-8b1e-4f47-87a5-1a4b6a08030e`).
