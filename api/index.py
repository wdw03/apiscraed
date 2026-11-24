"""
Production-Ready FastAPI Application for Vercel Serverless
D247 & Cricket Live Scoreboard API with Interactive Web Documentation Portal
"""

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path for Vercel serverless runtime
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException, Query, Header, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
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
# Web Documentation Portal HTML
# --------------------------------------------------------------------------

HTML_PORTAL = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>APIScraed - Live Cricket Score & Sports Odds API</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0b0f19; color: #f3f4f6; }
    code, pre { font-family: 'JetBrains Mono', monospace; }
    .glass-card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .badge-get { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-post { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
  </style>
</head>
<body class="min-h-screen antialiased selection:bg-emerald-500 selection:text-white">

  <!-- Navigation -->
  <header class="sticky top-0 z-50 border-b border-gray-800 bg-[#0b0f19]/80 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-300 flex items-center justify-center font-bold text-gray-950 text-xl shadow-lg shadow-emerald-500/20">
          ⚡
        </div>
        <div>
          <span class="font-bold text-lg text-white">APIScraed</span>
          <span class="text-xs text-emerald-400 block font-mono">v1.0.0 Production</span>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/docs" target="_blank" class="px-3.5 py-1.5 rounded-lg text-sm font-semibold bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition flex items-center gap-2">
          <i class="fa-solid fa-bolt text-emerald-400"></i> Swagger UI
        </a>
        <a href="https://github.com/wdw03/apiscraed" target="_blank" class="px-3.5 py-1.5 rounded-lg text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-2 shadow-lg shadow-emerald-600/30">
          <i class="fa-brands fa-github"></i> GitHub
        </a>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-8">
    <div class="text-center max-w-3xl mx-auto">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-4">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Production Serverless API Live on Vercel
      </div>
      <h1 class="text-4xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
        Real-Time Cricket Scores, <span class="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">Odds & Orderbook</span> APIs
      </h1>
      <p class="mt-4 text-gray-400 text-base sm:text-lg">
        Fast, zero-auth live scorecards, ball-by-ball commentary, back & lay odds, and tournament fixtures reverse-engineered with production-ready endpoints.
      </p>

      <!-- Quick Copy URL -->
      <div class="mt-6 flex items-center justify-center gap-2 max-w-xl mx-auto bg-gray-900 border border-gray-800 rounded-xl p-2 font-mono text-sm">
        <span class="text-gray-500 select-none px-2">Base URL:</span>
        <input type="text" id="baseUrl" readonly value="https://apiscraed.vercel.app" class="bg-transparent text-emerald-400 w-full focus:outline-none select-all font-semibold">
        <button onclick="navigator.clipboard.writeText('https://apiscraed.vercel.app'); alert('Base URL copied!');" class="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg text-xs transition">Copy</button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12">
      <div class="glass-card p-5 rounded-2xl">
        <div class="text-gray-400 text-xs font-semibold uppercase tracking-wider">Live Score API</div>
        <div class="text-2xl font-bold text-emerald-400 mt-1">Global CDN</div>
        <div class="text-xs text-gray-500 mt-1">Zero Auth • Ball-by-Ball</div>
      </div>
      <div class="glass-card p-5 rounded-2xl">
        <div class="text-gray-400 text-xs font-semibold uppercase tracking-wider">Market Odds</div>
        <div class="text-2xl font-bold text-teal-300 mt-1">Real-Time</div>
        <div class="text-xs text-gray-500 mt-1">Back & Lay • Bookmaker • Fancy</div>
      </div>
      <div class="glass-card p-5 rounded-2xl">
        <div class="text-gray-400 text-xs font-semibold uppercase tracking-wider">Crypto Protocol</div>
        <div class="text-2xl font-bold text-blue-400 mt-1">AES-256</div>
        <div class="text-xs text-gray-500 mt-1">CryptoJS EVP_BytesToKey</div>
      </div>
      <div class="glass-card p-5 rounded-2xl">
        <div class="text-gray-400 text-xs font-semibold uppercase tracking-wider">Test Suite</div>
        <div class="text-2xl font-bold text-purple-400 mt-1">100% Pass</div>
        <div class="text-xs text-gray-500 mt-1">21 Production Routes Verified</div>
      </div>
    </div>
  </section>

  <!-- Interactive Endpoint Playground -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="border-b border-gray-800 pb-4 mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-white">API Reference & Interactive Playground</h2>
        <p class="text-gray-400 text-sm">Click "Run Live" on any endpoint to test real-time data directly from your browser.</p>
      </div>
      <div class="flex items-center gap-2 text-xs font-mono">
        <span class="px-2 py-1 rounded badge-get font-semibold">GET = Public Feed</span>
        <span class="px-2 py-1 rounded badge-post font-semibold">POST = Encrypted Payload</span>
      </div>
    </div>

    <!-- Category 1: Cricket Live Score (8 Dedicated Endpoints) -->
    <div class="mb-12">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🏏</span>
          <h3 class="text-xl font-bold text-emerald-400">Cricket Live Score & Match Feed APIs</h3>
          <span class="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">8 Dedicated APIs • Zero Auth</span>
        </div>
        <span class="text-xs text-gray-400 font-mono">Live Match: SA vs BAN (ID: 609763268)</span>
      </div>

      <div class="grid gap-4">
        <!-- 1. Score Overview -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/bootstrap/{match_id}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/live/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/bootstrap/609763268')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Score Overview)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Live Match Overview</strong>: Match status (live/finished), Toss winner & decision, Total Runs, Wickets, Overs, Run Rate, Striker, Non-Striker, and Current Bowler.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Headers:</span> <code class="text-gray-300">Accept: application/json</code></div>
            <div><span class="text-gray-500">Cookies:</span> <span class="text-emerald-400 font-semibold">None (100% Free / Public)</span></div>
            <div><span class="text-gray-500">Param:</span> <code class="text-emerald-300">match_id (int / string)</code></div>
          </div>
        </div>

        <!-- 2. Full Scoreboard / Scorecard -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/scorecard/{match_id}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/scorecard/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/scorecard/609763268')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Full Scorecard)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Official Scoreboard & Statistics</strong>: All innings batting figures (Runs, Balls, 4s, 6s, Strike Rate, Dismissal/Wicket mode) and bowling figures (Overs, Maidens, Runs conceded, Wickets, Economy).
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Headers:</span> <code class="text-gray-300">Accept: application/json</code></div>
            <div><span class="text-gray-500">Cookies:</span> <span class="text-emerald-400 font-semibold">None (100% Public)</span></div>
            <div><span class="text-gray-500">Param:</span> <code class="text-emerald-300">match_id</code></div>
          </div>
        </div>

        <!-- 3. Commentary -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/commentary/{match_id}?limit=10</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/commentary/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/commentary/609763268?limit=10')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Commentary)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Ball-by-Ball Text Commentary</strong>: Play-by-play narrative descriptions for every single ball delivered, boundaries, milestone highlights, and wicket dismissals.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Headers:</span> <code class="text-gray-300">None required</code></div>
            <div><span class="text-gray-500">Query:</span> <code class="text-emerald-300">limit=10 (optional, default 50)</code></div>
          </div>
        </div>

        <!-- 4. Partnerships -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/partnerships/{match_id}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/partnerships/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/partnerships/609763268')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Partnerships)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Batting Partnerships</strong>: Wicket-by-wicket partnership breakdown, total partnership runs, balls faced, and individual batter run share for every stand.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Headers:</span> <code class="text-gray-300">None required</code></div>
            <div><span class="text-gray-500">Cookies:</span> <span class="text-emerald-400 font-semibold">None (100% Public)</span></div>
          </div>
        </div>

        <!-- 5. Lineup -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/lineup/{match_id}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/lineup/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/lineup/609763268')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Playing XI & Squad)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Playing XI & Squads</strong>: 11 starting players for each team, Captain (`isCaptain: true`), Wicket-Keeper (`isKeeper: true`), and full bench substitute players.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Headers:</span> <code class="text-gray-300">None required</code></div>
            <div><span class="text-gray-500">Cookies:</span> <span class="text-emerald-400 font-semibold">None (100% Public)</span></div>
          </div>
        </div>

        <!-- 6. Overs -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/overs/{match_id}?innings=1&limit=5</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/overs/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/overs/609763268?innings=1&limit=5')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Overs Log)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Ball-by-Ball Delivery Log</strong>: Complete sequence of deliveries for each over (dots, 1s, 4s, 6s, wickets, wides, no-balls) alongside bowler figures.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Query:</span> <code class="text-emerald-300">innings=1, limit=5</code></div>
            <div><span class="text-gray-500">Cookies:</span> <span class="text-emerald-400 font-semibold">None (100% Public)</span></div>
          </div>
        </div>

        <!-- 7. Charts -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/charts/{match_id}</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/charts/{match_id}</span>
            </div>
            <button onclick="testApi('/api/score/charts/609763268')" class="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 self-start lg:self-auto shadow-md shadow-emerald-600/20">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Worm & Charts)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Worm Graph & Run Rate Analytics</strong>: Over-by-over progression coordinates, cumulative scores, and required run rate curves for rendering frontend charts.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Headers:</span> <code class="text-gray-300">None required</code></div>
            <div><span class="text-gray-500">Cookies:</span> <span class="text-emerald-400 font-semibold">None (100% Public)</span></div>
          </div>
        </div>

        <!-- 8. Embed Widget -->
        <div class="glass-card rounded-2xl p-5 hover:border-emerald-500/40 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3 flex-wrap">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/score/embed/{match_id}?theme=dark</span>
              <span class="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shortcut: /api/embed/{match_id}</span>
            </div>
            <div class="flex items-center gap-2">
              <button onclick="testApi('/api/score/embed/609763268')" class="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-semibold transition flex items-center gap-1.5 border border-gray-700">
                <i class="fa-solid fa-code text-[10px]"></i> Get Embed JSON
              </button>
              <a href="/api/score/embed/609763268?redirect=true" target="_blank" class="px-3.5 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-md shadow-teal-600/20">
                <i class="fa-solid fa-up-right-from-square text-[10px]"></i> Open Scoreboard Widget
              </a>
            </div>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            <strong>Responsive HTML Iframe Widget</strong>: Direct embeddable widget URL and iframe tag for instant embedding into any React, Vue, WordPress, or mobile web app.
          </p>
          <div class="mt-3 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
            <div><span class="text-gray-500">Query:</span> <code class="text-emerald-300">theme=dark|light, redirect=true|false</code></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Category 2: Sports & Real-Time Odds -->
    <div class="mb-12">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-xl">📊</span>
        <h3 class="text-xl font-bold text-teal-400">Sports Fixtures & Real-Time Odds APIs</h3>
        <span class="text-xs px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300 font-semibold">Live Orderbook</span>
      </div>

      <div class="grid gap-4">
        <!-- Endpoint Card 6 -->
        <div class="glass-card rounded-2xl p-5 hover:border-teal-500/30 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/matches?sport_id=4&inplay_only=true</span>
            </div>
            <button onclick="testApi('/api/matches?sport_id=4&inplay_only=true')" class="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (In-Play Matches)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            Fetches all currently live in-play cricket matches with game IDs, tournament leagues, and start times.
          </p>
        </div>

        <!-- Endpoint Card 7 -->
        <div class="glass-card rounded-2xl p-5 hover:border-teal-500/30 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/odds/{game_id}</span>
            </div>
            <button onclick="testApi('/api/odds/838843313')" class="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Odds & Liquidity)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            Real-time Match Odds (Back & Lay prices and volume size), Bookmaker rates, and Fancy session markets.
          </p>
        </div>

        <!-- Endpoint Card 8 -->
        <div class="glass-card rounded-2xl p-5 hover:border-teal-500/30 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/tree</span>
            </div>
            <button onclick="testApi('/api/tree')" class="px-3 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-play text-[10px]"></i> Run Live (Sports Tree)
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            Full hierarchical sports navigation tree: Tournaments, Competitions, Series, and active games.
          </p>
        </div>
      </div>
    </div>

    <!-- Category 3: Betting Utilities -->
    <div class="mb-12">
      <div class="flex items-center gap-2 mb-4">
        <span class="text-xl">💰</span>
        <h3 class="text-xl font-bold text-blue-400">Betting Utilities & User Account APIs</h3>
      </div>

      <div class="grid gap-4">
        <!-- Endpoint Card 9 -->
        <div class="glass-card rounded-2xl p-5 hover:border-blue-500/30 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-post">POST</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/bet/payload</span>
            </div>
            <button onclick="testBetPayload()" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition flex items-center gap-1.5">
              <i class="fa-solid fa-play text-[10px]"></i> Build Validated Bet
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            Validates bet parameters (back/lay, odds, stake) and automatically calculates liability and net profit.
          </p>
        </div>

        <!-- Endpoint Card 10 -->
        <div class="glass-card rounded-2xl p-5 hover:border-blue-500/30 transition">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="px-2.5 py-1 rounded text-xs font-bold badge-get">GET</span>
              <span class="font-mono text-sm sm:text-base text-gray-200 font-semibold">/api/bet/user</span>
            </div>
            <button onclick="testApi('/api/bet/user')" class="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs font-semibold transition flex items-center gap-1.5 border border-gray-700">
              <i class="fa-solid fa-lock text-[10px]"></i> Test Auth Protection
            </button>
          </div>
          <p class="text-sm text-gray-400 mt-2">
            Fetches user account balance, credit limit, and current exposure. Requires active <code class="text-emerald-400">g_token</code> cookie.
          </p>
        </div>
      </div>
    </div>

    <!-- Live Output Modal / Viewer -->
    <div id="outputSection" class="hidden mb-12">
      <div class="glass-card rounded-2xl p-6 border-emerald-500/40">
        <div class="flex items-center justify-between pb-3 border-b border-gray-800">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="font-bold text-white text-sm" id="outputTitle">Live Response</span>
            <span id="outputStatus" class="text-xs px-2 py-0.5 rounded font-mono font-bold"></span>
          </div>
          <button onclick="document.getElementById('outputSection').classList.add('hidden')" class="text-gray-400 hover:text-white text-sm">Close ✕</button>
        </div>
        <pre id="outputContent" class="mt-4 p-4 rounded-xl bg-gray-950 text-emerald-400 text-xs overflow-x-auto max-h-96"></pre>
      </div>
    </div>

    <!-- Implementation Code Snippets -->
    <div class="glass-card rounded-3xl p-6 sm:p-8 mt-12 border-gray-800">
      <h3 class="text-2xl font-bold text-white mb-2">💻 Code Integration Examples</h3>
      <p class="text-gray-400 text-sm mb-6">Easily integrate real-time cricket scores and live odds into your application in seconds.</p>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Python Integration -->
        <div class="bg-gray-950 p-5 rounded-2xl border border-gray-800">
          <div class="flex items-center justify-between mb-3 text-xs text-gray-400">
            <span class="font-bold text-white"><i class="fa-brands fa-python text-yellow-400 mr-1.5"></i> Python</span>
            <button onclick="navigator.clipboard.writeText(document.getElementById('pyCode').innerText); alert('Python code copied!');" class="hover:text-white">Copy</button>
          </div>
          <pre id="pyCode" class="text-xs text-gray-300 overflow-x-auto"><code>import requests

BASE_URL = "https://apiscraed.vercel.app"

# 1. Fetch live inplay cricket matches
matches = requests.get(f"{BASE_URL}/api/matches?inplay_only=true").json()
print("Live Matches:", len(matches.get("matches", [])))

# 2. Fetch live cricket scorecard & overs
score = requests.get(f"{BASE_URL}/api/score/bootstrap/609763268").json()
print(f"Match: {score['match_name']} | Status: {score['match_status']}")

# 3. Fetch real-time Back/Lay Odds
odds = requests.get(f"{BASE_URL}/api/odds/838843313").json()
print("Markets Available:", len(odds.get("markets", [])))</code></pre>
        </div>

        <!-- JavaScript / Node Integration -->
        <div class="bg-gray-950 p-5 rounded-2xl border border-gray-800">
          <div class="flex items-center justify-between mb-3 text-xs text-gray-400">
            <span class="font-bold text-white"><i class="fa-brands fa-js text-yellow-300 mr-1.5"></i> JavaScript (Fetch)</span>
            <button onclick="navigator.clipboard.writeText(document.getElementById('jsCode').innerText); alert('JavaScript code copied!');" class="hover:text-white">Copy</button>
          </div>
          <pre id="jsCode" class="text-xs text-gray-300 overflow-x-auto"><code>const BASE_URL = "https://apiscraed.vercel.app";

// Fetch Live Cricket Score
async function getLiveScore(gameId) {
  const res = await fetch(`${BASE_URL}/api/score/bootstrap/${gameId}`);
  const data = await res.json();
  console.log(`${data.match_name}: ${data.runs}/${data.wickets} in ${data.overs} ov`);
}

// Fetch Real-time Odds
async function getOdds(gameId) {
  const res = await fetch(`${BASE_URL}/api/odds/${gameId}`);
  const data = await res.json();
  console.log(data.markets);
}

getLiveScore(609763268);</code></pre>
        </div>
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer class="border-t border-gray-900 bg-[#070a11] mt-20 py-8 text-center text-xs text-gray-500">
    <p>APIScraed • Deployed on Vercel Serverless Functions • Open Source on <a href="https://github.com/wdw03/apiscraed" class="text-emerald-400 hover:underline">GitHub</a></p>
  </footer>

  <script>
    async function testApi(path) {
      const outSec = document.getElementById('outputSection');
      const outTitle = document.getElementById('outputTitle');
      const outStatus = document.getElementById('outputStatus');
      const outContent = document.getElementById('outputContent');
      
      outSec.classList.remove('hidden');
      outTitle.innerText = "GET " + path;
      outStatus.className = "text-xs px-2 py-0.5 rounded font-mono font-bold bg-yellow-500/20 text-yellow-400";
      outStatus.innerText = "LOADING...";
      outContent.innerText = "Sending live request to " + path + "...";

      try {
        const res = await fetch(path);
        const data = await res.json();
        outStatus.innerText = "HTTP " + res.status;
        outStatus.className = res.status < 400 ? "text-xs px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-400" : "text-xs px-2 py-0.5 rounded font-mono font-bold bg-red-500/20 text-red-400";
        outContent.innerText = JSON.stringify(data, null, 2);
      } catch (err) {
        outStatus.innerText = "ERROR";
        outStatus.className = "text-xs px-2 py-0.5 rounded font-mono font-bold bg-red-500/20 text-red-400";
        outContent.innerText = err.toString();
      }
      outSec.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    async function testBetPayload() {
      const outSec = document.getElementById('outputSection');
      const outTitle = document.getElementById('outputTitle');
      const outStatus = document.getElementById('outputStatus');
      const outContent = document.getElementById('outputContent');
      
      outSec.classList.remove('hidden');
      outTitle.innerText = "POST /api/bet/payload";
      outStatus.className = "text-xs px-2 py-0.5 rounded font-mono font-bold bg-yellow-500/20 text-yellow-400";
      outStatus.innerText = "LOADING...";
      
      const payload = {
        game_id: 609763268,
        market_id: 5990747261011,
        runner_id: 88210,
        runner_name: "South Africa",
        bet_type: "back",
        odds: 1.5,
        stake: 1000,
        market_type: "match"
      };

      try {
        const res = await fetch("/api/bet/payload", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        outStatus.innerText = "HTTP " + res.status;
        outStatus.className = "text-xs px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-400";
        outContent.innerText = JSON.stringify(data, null, 2);
      } catch (err) {
        outStatus.innerText = "ERROR";
        outStatus.className = "text-xs px-2 py-0.5 rounded font-mono font-bold bg-red-500/20 text-red-400";
        outContent.innerText = err.toString();
      }
      outSec.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  </script>
</body>
</html>
"""

# --------------------------------------------------------------------------
# General Endpoints
# --------------------------------------------------------------------------

@app.get("/", tags=["General"], response_class=HTMLResponse)
def root(request: Request):
    """
    API Root - Returns interactive HTML Web Documentation Portal when accessed via browser,
    or JSON when Accept header specifies application/json.
    """
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return JSONResponse({
            "status": "online",
            "service": "D247 & Cricket Live Scoreboard API",
            "version": "1.0.0",
            "docs_url": "/docs",
            "portal_url": "/",
            "endpoints": {
                "live_matches": "/api/matches?sport_id=4&inplay_only=true",
                "sports_tree": "/api/tree",
                "realtime_odds": "/api/odds/{game_id}",
                "match_details": "/api/details/{game_id}",
                "1_score_overview": "/api/score/bootstrap/{match_id} [alias: /api/live/{match_id}]",
                "2_scorecard": "/api/score/scorecard/{match_id} [alias: /api/scorecard/{match_id}]",
                "3_commentary": "/api/score/commentary/{match_id} [alias: /api/commentary/{match_id}]",
                "4_partnerships": "/api/score/partnerships/{match_id} [alias: /api/partnerships/{match_id}]",
                "5_lineup": "/api/score/lineup/{match_id} [alias: /api/lineup/{match_id}]",
                "6_overs": "/api/score/overs/{match_id}?innings=1&limit=50 [alias: /api/overs/{match_id}]",
                "7_charts": "/api/score/charts/{match_id} [alias: /api/charts/{match_id}]",
                "8_embed_widget": "/api/score/embed/{match_id} [alias: /api/embed/{match_id}]",
                "bet_payload_builder": "POST /api/bet/payload"
            }
        })
    return HTMLResponse(content=HTML_PORTAL)


@app.get("/api", tags=["General"])
def api_index():
    """JSON API index and status"""
    return {
        "status": "online",
        "service": "D247 & Cricket Live Scoreboard API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "portal_url": "/"
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
# Cricket Live Score Endpoints (8 Dedicated Endpoints & Public Feeds)
# --------------------------------------------------------------------------

# 1. Live Match Score Overview
@app.get("/api/score/bootstrap/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/score/live/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/live/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_score_bootstrap(match_id: str):
    """
    1. Score API (Live Match Overview)
    Fetches real-time match state, toss, current runs/wickets/overs, active striker, non-striker, bowler, and run rate.
    Accepts numerical game_id (e.g. 609763268) or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_bootstrap(match_id)
        if not res.get("success"):
            return JSONResponse(status_code=404, content=res)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch score bootstrap: {str(e)}")


# 2. Scoreboard / Full Scorecard
@app.get("/api/score/scorecard/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/scorecard/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_scorecard(match_id: str):
    """
    2. Scoreboard API (Full Scorecard)
    Fetches complete official scorecard with all innings, batting stats (runs, balls, 4s, 6s, SR),
    bowling figures (overs, maidens, runs, wickets, economy), and dismissals.
    Accepts numerical game_id or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_scorecard(match_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scorecard: {str(e)}")


# 3. Ball-by-Ball Text Commentary Stream
@app.get("/api/score/commentary/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/commentary/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_commentary(
    match_id: str,
    limit: int = Query(50, description="Maximum commentary entries to return")
):
    """
    3. Commentary API (Ball-by-Ball Text Stream)
    Fetches live textual play-by-play commentary stream for every delivery.
    Accepts numerical game_id or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_commentary(match_id, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch commentary: {str(e)}")


# 4. Batting Partnerships Breakdown
@app.get("/api/score/partnerships/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/partnerships/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_partnerships(match_id: str):
    """
    4. Partnership API (Batting Partnerships)
    Fetches wicket-by-wicket partnership breakdown, batter run contributions, and balls faced.
    Accepts numerical game_id or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_partnerships(match_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch partnerships: {str(e)}")


# 5. Playing XI & Squad Lineup
@app.get("/api/score/lineup/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/lineup/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_lineup(match_id: str):
    """
    5. Lineup API (Playing XI & Squad)
    Fetches playing XI, captain indicator, wicket-keeper roles, and bench substitute players for both teams.
    Accepts numerical game_id or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_lineup(match_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch lineup: {str(e)}")


# 6. Ball-by-Ball Overs Log
@app.get("/api/score/overs/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/overs/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_overs(
    match_id: str,
    innings: int = Query(1, description="Inning number (1 or 2)"),
    limit: int = Query(50, description="Maximum overs to return")
):
    """
    6. Overs API (Ball-by-Ball Deliveries Log)
    Fetches ball-by-ball delivery log (dot, 1, 2, 4, 6, W, wide, no-ball) and bowler figures per over.
    Accepts numerical game_id or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_overs(match_id, innings_number=innings, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overs: {str(e)}")


# 7. Worm Graph & Charts
@app.get("/api/score/charts/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/charts/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_charts(match_id: str):
    """
    7. Charts API (Worm Graph & Run Rate Coordinates)
    Fetches Worm chart data, cumulative runs per over, and run-rate progression vectors.
    Accepts numerical game_id or provider event ID.
    No login or cookies required.
    """
    try:
        res = score_client.get_charts(match_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch charts: {str(e)}")


# 8. Responsive Scoreboard Embed Widget
@app.get("/api/score/embed/{match_id}", tags=["Cricket Live Score - Dedicated"])
@app.get("/api/embed/{match_id}", tags=["Cricket Live Score - Dedicated"])
def get_embed(
    match_id: str,
    theme: str = Query("dark", description="'dark' or 'light'"),
    redirect: bool = Query(False, description="Whether to redirect directly to embed HTML")
):
    """
    8. Embed Widget API (Responsive Scoreboard Widget)
    Returns direct iframe widget HTML and URL to embed live scoreboard inside any website or mobile app.
    Accepts numerical game_id or provider event ID.
    """
    url = score_client.get_embed_url(match_id, theme=theme)
    if redirect:
        return RedirectResponse(url=url)
    return {
        "game_id": match_id,
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
