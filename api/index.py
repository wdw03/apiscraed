"""
Production-Ready FastAPI Application for Vercel Serverless
D247 & Cricket Live Scoreboard API
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path for Vercel serverless runtime
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException, Query, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from core.score import ScoreClient
from core.sports import SportsClient
from core.betting import BettingClient
from core.crypto import DEFAULT_CRYPTO_KEY

# Initialize FastAPI App
app = FastAPI(
    title="D247 & Cricket Live Score API",
    description=(
        "Production-ready Serverless API providing real-time cricket live scores, ball-by-ball commentary, "
        "scorecards, match odds, bookmaker rates, and tournament fixtures. Deployable directly to Vercel."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin access from any frontend (React, Next.js, Vue, mobile apps, Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton client instances
score_client = ScoreClient()
sports_client = SportsClient()


# --------------------------------------------------------------------------
# Request & Response Models (Pydantic)
# --------------------------------------------------------------------------

class BetPayloadRequest(BaseModel):
    game_id: int = Field(..., description="Match ID (e.g. 609763268)", example=609763268)
    market_id: int = Field(..., description="Market ID (e.g. 5990747261011)", example=5990747261011)
    runner_id: int = Field(..., description="Selection ID of the runner/team", example=88210)
    runner_name: str = Field(..., description="Name of the team or runner", example="South Africa")
    bet_type: str = Field(..., description="'back' or 'lay'", example="back")
    odds: float = Field(..., description="Price rate / odds (e.g. 1.85)", example=1.85)
    stake: float = Field(..., description="Amount to bet", example=500.0)
    market_type: str = Field("match", description="'match', 'match1' (Bookmaker), or 'fancy'", example="match")


# --------------------------------------------------------------------------
# General Endpoints
# --------------------------------------------------------------------------

@app.get("/", tags=["General"])
def root():
    """API Root - Provides service health and documentation links"""
    return {
        "status": "online",
        "service": "D247 & Cricket Live Scoreboard API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "live_matches": "/api/matches?sport_id=4&inplay_only=true",
            "sports_tree": "/api/tree",
            "realtime_odds": "/api/odds/{game_id}",
            "match_details": "/api/details/{game_id}",
            "score_bootstrap": "/api/score/bootstrap/{game_id}",
            "score_scorecard": "/api/score/scorecard/{event_id}",
            "score_overs": "/api/score/overs/{event_id}?innings=1&limit=50",
            "score_commentary": "/api/score/commentary/{event_id}",
            "score_lineup": "/api/score/lineup/{event_id}",
            "score_charts": "/api/score/charts/{event_id}",
            "score_embed": "/api/score/embed/{game_id}",
            "bet_payload_builder": "POST /api/bet/payload"
        }
    }


@app.get("/health", tags=["General"])
def health():
    """Uptime / Health check endpoint"""
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/server/check", tags=["General"])
def check_server():
    """Checks Geo-IP, ISP, and proxy detection from upstream D247 infrastructure"""
    try:
        return sports_client.check_server()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check server: {str(e)}")


# --------------------------------------------------------------------------
# Sports, Tournaments & Live Odds Endpoints
# --------------------------------------------------------------------------

@app.get("/api/matches", tags=["Sports & Odds"])
def get_matches(
    sport_id: int = Query(4, description="Sport ID: 4=Cricket, 1=Soccer, 2=Tennis"),
    inplay_only: bool = Query(False, description="Filter only currently in-play live matches")
):
    """
    Fetches live and upcoming matches for the selected sport.
    No login required.
    """
    try:
        matches = sports_client.get_live_matches(sport_id=sport_id)
        if inplay_only:
            matches = [m for m in matches if m.get("iplay") is True]
        return {
            "success": True,
            "sport_id": sport_id,
            "inplay_only": inplay_only,
            "total_matches": len(matches),
            "matches": matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch matches: {str(e)}")


@app.get("/api/tree", tags=["Sports & Odds"])
def get_tree():
    """
    Fetches full hierarchical tournament navigation tree across all sports.
    No login required.
    """
    try:
        return sports_client.get_tree()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sports tree: {str(e)}")


@app.get("/api/tabs", tags=["Sports & Odds"])
def get_tabs():
    """Fetches active sports tabs configuration"""
    try:
        return sports_client.get_tabs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tabs: {str(e)}")


@app.get("/api/featured", tags=["Sports & Odds"])
def get_featured_events():
    """Fetches marquee/featured matches currently on the homepage"""
    try:
        return sports_client.get_latest_events()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch featured events: {str(e)}")


@app.get("/api/details/{game_id}", tags=["Sports & Odds"])
def get_game_details(
    game_id: int,
    sport_id: int = Query(4, description="Sport ID (default: 4 for Cricket)")
):
    """
    Fetches match metadata (league name, scorecard type, streaming availability).
    No login required.
    """
    try:
        return sports_client.get_game_details(game_id, sport_id=sport_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch match details: {str(e)}")


@app.get("/api/odds/{game_id}", tags=["Sports & Odds"])
def get_game_odds(
    game_id: int,
    sport_id: int = Query(4, description="Sport ID (default: 4 for Cricket)")
):
    """
    Fetches real-time Back/Lay prices, liquidity sizes, Match Odds, Bookmaker rates, and Fancy markets.
    No login required.
    """
    try:
        odds = sports_client.get_game_odds(game_id, sport_id=sport_id)
        return odds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch live odds: {str(e)}")


# --------------------------------------------------------------------------
# Cricket Live Score Endpoints (CloudFront CDN)
# --------------------------------------------------------------------------

@app.get("/api/score/bootstrap/{game_id}", tags=["Cricket Live Score"])
def get_score_bootstrap(game_id: int):
    """
    Fetches high-level live cricket score summary:
    Toss, match state, current runs/wickets/overs, active striker, non-striker, bowler, and providerEventId.
    No login required.
    """
    try:
        res = score_client.get_bootstrap(game_id)
        if not res.get("success"):
            return JSONResponse(status_code=404, content=res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch score bootstrap: {str(e)}")


@app.get("/api/score/scorecard/{event_id}", tags=["Cricket Live Score"])
def get_scorecard(event_id: str):
    """
    Fetches complete scorecard including all innings, batting stats, bowling figures, and wickets.
    Accepts either numerical `game_id` (e.g. 609763268) or provider ID (e.g. provider-3:...).
    No login required.
    """
    try:
        res = score_client.get_scorecard(event_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scorecard: {str(e)}")


@app.get("/api/score/overs/{event_id}", tags=["Cricket Live Score"])
def get_overs(
    event_id: str,
    innings: int = Query(1, description="Inning number (1 or 2)"),
    limit: int = Query(50, description="Maximum overs to return")
):
    """
    Fetches ball-by-ball commentary for each completed and in-progress over.
    Every single delivery display (dot, 1, 2, 4, 6, W, wide, no-ball) is included.
    No login required.
    """
    try:
        res = score_client.get_overs(event_id, innings_number=innings, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overs: {str(e)}")


@app.get("/api/score/commentary/{event_id}", tags=["Cricket Live Score"])
def get_commentary(
    event_id: str,
    limit: int = Query(50, description="Maximum commentary entries")
):
    """
    Fetches textual play-by-play commentary stream.
    No login required.
    """
    try:
        res = score_client.get_commentary(event_id, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commentary: {str(e)}")


@app.get("/api/score/lineup/{event_id}", tags=["Cricket Live Score"])
def get_lineup(event_id: str):
    """
    Fetches playing XI, captain, wicket-keeper, and bench players for both teams.
    No login required.
    """
    try:
        res = score_client.get_lineup(event_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lineup: {str(e)}")


@app.get("/api/score/partnerships/{event_id}", tags=["Cricket Live Score"])
def get_partnerships(event_id: str):
    """
    Fetches batting partnerships per wicket.
    No login required.
    """
    try:
        res = score_client.get_partnerships(event_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch partnerships: {str(e)}")


@app.get("/api/score/charts/{event_id}", tags=["Cricket Live Score"])
def get_charts(event_id: str):
    """
    Fetches Worm chart and run-rate progression data coordinates.
    No login required.
    """
    try:
        res = score_client.get_charts(event_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch charts: {str(e)}")


@app.get("/api/score/embed/{game_id}", tags=["Cricket Live Score"])
def get_embed(
    game_id: int,
    theme: str = Query("dark", description="'dark' or 'light'"),
    redirect: bool = Query(False, description="Whether to redirect directly to embed HTML")
):
    """
    Returns direct iframe widget URL or redirects to responsive HTML scoreboard embed.
    """
    url = score_client.get_embed_url(game_id, theme=theme)
    if redirect:
        return RedirectResponse(url=url)
    return {
        "game_id": game_id,
        "theme": theme,
        "embed_url": url,
        "iframe_code": f'<iframe src="{url}" width="100%" height="450" frameborder="0"></iframe>'
    }


# --------------------------------------------------------------------------
# Betting & User Account Endpoints
# --------------------------------------------------------------------------

@app.post("/api/bet/payload", tags=["Betting Utilities"])
def build_bet_payload(bet_req: BetPayloadRequest):
    """
    Constructs and validates the encrypted betData payload required for placing a bet.
    Calculates liability and profit automatically.
    """
    try:
        payload = BettingClient.build_bet_payload(
            game_id=bet_req.game_id,
            market_id=bet_req.market_id,
            runner_id=bet_req.runner_id,
            runner_name=bet_req.runner_name,
            bet_type=bet_req.bet_type,
            odds=bet_req.odds,
            stake=bet_req.stake,
            market_type=bet_req.market_type
        )
        return {
            "success": True,
            "validated_payload": payload,
            "calculated_profit": payload["profit"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid bet parameters: {str(e)}")


@app.get("/api/bet/user", tags=["Betting Utilities"])
def get_user_data(
    authorization: Optional[str] = Header(None, description="Optional 'Bearer <token>' or raw g_token value"),
    token: Optional[str] = Query(None, description="Optional g_token query parameter")
):
    """
    Fetches user account balance, credit limit, and current exposure.
    Requires an authenticated 'g_token' session cookie/token.
    """
    auth_token = token or (authorization.replace("Bearer ", "").strip() if authorization else None)
    if not auth_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"authenticated": False, "error": "Missing token. Provide 'g_token' in Authorization header or query parameter."}
        )
    client = BettingClient(token=auth_token)
    return client.get_user_data()


@app.get("/api/bet/book/{game_id}", tags=["Betting Utilities"])
def get_user_book(
    game_id: int,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    """
    Fetches user's open bets and exposure on a specific game.
    Requires an authenticated 'g_token' session cookie/token.
    """
    auth_token = token or (authorization.replace("Bearer ", "").strip() if authorization else None)
    if not auth_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"authenticated": False, "error": "Missing token. Provide 'g_token' in Authorization header or query parameter."}
        )
    client = BettingClient(token=auth_token)
    return client.get_user_book(game_id)
