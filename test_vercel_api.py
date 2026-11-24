"""
Vercel API Local Test Suite
Validates all FastAPI routes using TestClient prior to deployment.
"""

import sys
from pathlib import Path
import time
import json

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def run_tests():
    print("=" * 80)
    print("      VERCEL FASTAPI SERVERLESS DEPLOYMENT - LOCAL ROUTE VALIDATION")
    print("=" * 80)
    
    routes_to_test = [
        ("GET", "/", None, 200, "Root API Documentation Index"),
        ("GET", "/health", None, 200, "Uptime Health Check"),
        ("GET", "/openapi.json", None, 200, "OpenAPI Schema Generation"),
        ("GET", "/docs", None, 200, "Interactive Swagger UI"),
        ("GET", "/api/server/check", None, 200, "Geo-IP & Server Health"),
        ("GET", "/api/matches?sport_id=4", None, 200, "Live & Upcoming Cricket Matches"),
        ("GET", "/api/matches?sport_id=4&inplay_only=true", None, 200, "In-Play Live Cricket Matches Filter"),
        ("GET", "/api/tree", None, 200, "Sports Tournament Navigation Tree"),
        ("GET", "/api/tabs", None, 200, "Active Sports Tabs"),
        ("GET", "/api/details/838843313", None, 200, "Match Metadata (India A v UAE)"),
        ("GET", "/api/odds/838843313", None, 200, "Real-Time Match Odds & Bookmaker Rates"),
        ("GET", "/api/score/bootstrap/609763268", None, 200, "Score Bootstrap (SA v BAN)"),
        ("GET", "/api/score/live/609763268", None, 200, "Score Live Overview Dedicated"),
        ("GET", "/api/live/609763268", None, 200, "Score Live Overview Shortcut"),
        ("GET", "/api/score/scorecard/609763268", None, 200, "Scorecard Dedicated"),
        ("GET", "/api/scorecard/609763268", None, 200, "Scorecard Shortcut"),
        ("GET", "/api/score/commentary/609763268?limit=5", None, 200, "Commentary Stream Dedicated"),
        ("GET", "/api/commentary/609763268?limit=5", None, 200, "Commentary Stream Shortcut"),
        ("GET", "/api/score/partnerships/609763268", None, 200, "Partnerships Dedicated"),
        ("GET", "/api/partnerships/609763268", None, 200, "Partnerships Shortcut"),
        ("GET", "/api/score/lineup/609763268", None, 200, "Playing XI Lineup Dedicated"),
        ("GET", "/api/lineup/609763268", None, 200, "Playing XI Lineup Shortcut"),
        ("GET", "/api/score/overs/609763268?innings=1&limit=5", None, 200, "Overs Ball-by-Ball Dedicated"),
        ("GET", "/api/overs/609763268?innings=1&limit=5", None, 200, "Overs Ball-by-Ball Shortcut"),
        ("GET", "/api/score/charts/609763268", None, 200, "Worm Charts Dedicated"),
        ("GET", "/api/charts/609763268", None, 200, "Worm Charts Shortcut"),
        ("GET", "/api/score/embed/609763268", None, 200, "Scoreboard Embed Dedicated"),
        ("GET", "/api/embed/609763268", None, 200, "Scoreboard Embed Shortcut"),
        ("POST", "/api/bet/payload", {
            "game_id": 609763268,
            "market_id": 5990747261011,
            "runner_id": 88210,
            "runner_name": "South Africa",
            "bet_type": "back",
            "odds": 1.5,
            "stake": 1000,
            "market_type": "match"
        }, 200, "Bet Payload Builder & Profit Validation"),
        ("GET", "/api/bet/user", None, 401, "Auth Protection Interception (Missing Token)"),
    ]

    total = len(routes_to_test)
    passed = 0
    failed = 0

    for method, path, body, expected_status, description in routes_to_test:
        t0 = time.time()
        try:
            if method == "GET":
                resp = client.get(path)
            elif method == "POST":
                resp = client.post(path, json=body)
            else:
                resp = client.request(method, path)

            duration_ms = round((time.time() - t0) * 1000, 2)
            is_ok = (resp.status_code == expected_status)
            
            if is_ok:
                passed += 1
                icon = "[PASS]"
            else:
                failed += 1
                icon = "[FAIL]"

            print(f" {icon} {method:<4} {path:<45} -> Status: {resp.status_code} ({duration_ms} ms)")
            print(f"        Purpose: {description}")
            if not is_ok:
                print(f"        ERROR: Expected {expected_status}, got {resp.status_code}: {resp.text[:150]}")

        except Exception as e:
            failed += 1
            print(f" [FAIL] {method:<4} {path:<45} -> EXCEPTION: {e}")

    print("\n" + "=" * 80)
    print("                           VERCEL API ROUTE SUMMARY")
    print("=" * 80)
    print(f" Total Routes Tested : {total}")
    print(f" Passed Routes       : {passed} [SUCCESS]")
    print(f" Failed Routes       : {failed}")
    print(f" Success Rate        : {round((passed / total) * 100, 1)}%")
    print("=" * 80)

    if failed == 0:
        print("\nAll routes verified locally! Application is 100% READY FOR VERCEL DEPLOYMENT.")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
