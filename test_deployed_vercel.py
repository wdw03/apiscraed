import requests
import time
import json

BASE_URL = "https://apiscraed.vercel.app"

tests = [
    ("GET", "/", None, 200, "Root API Info"),
    ("GET", "/health", None, 200, "Health Check"),
    ("GET", "/docs", None, 200, "Interactive Swagger Docs"),
    ("GET", "/api/matches?sport_id=4", None, 200, "Live & Upcoming Cricket Matches"),
    ("GET", "/api/matches?sport_id=4&inplay_only=true", None, 200, "In-Play Live Matches Filter"),
    ("GET", "/api/tree", None, 200, "Sports Tournament Tree"),
    ("GET", "/api/tabs", None, 200, "Active Sports Tabs"),
    ("GET", "/api/details/838843313", None, 200, "Match Metadata (India A v UAE)"),
    ("GET", "/api/odds/838843313", None, 200, "Real-Time Odds & Bookmaker Orderbook"),
    ("GET", "/api/score/bootstrap/609763268", None, 200, "Cricket Live Score Overview"),
    ("GET", "/api/score/scorecard/609763268", None, 200, "Full Cricket Scorecard"),
    ("GET", "/api/score/overs/609763268?innings=1&limit=5", None, 200, "Ball-by-Ball Overs Commentary"),
    ("GET", "/api/score/commentary/609763268?limit=5", None, 200, "Live Text Commentary Stream"),
    ("GET", "/api/score/lineup/609763268", None, 200, "Playing XI & Lineup"),
    ("GET", "/api/score/partnerships/609763268", None, 200, "Batting Partnerships"),
    ("GET", "/api/score/charts/609763268", None, 200, "Worm Chart & Run Rate Data"),
    ("GET", "/api/score/embed/609763268", None, 200, "Scoreboard Iframe Embed Widget"),
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
    ("GET", "/api/server/check", None, 200, "Geo-IP & Server Connection Telemetry"),
    ("GET", "/api/bet/user", None, 401, "Auth Protection & 401 Interception")
]

print("=" * 80)
print("     LIVE PRODUCTION TEST SUITE: https://apiscraed.vercel.app")
print("=" * 80)

results = []
for method, path, body, expected_status, name in tests:
    url = BASE_URL + path
    t0 = time.time()
    try:
        if method == "GET":
            r = requests.get(url, timeout=15)
        else:
            r = requests.post(url, json=body, timeout=15)
        latency = round((time.time() - t0) * 1000, 2)
        passed = (r.status_code == expected_status)
        icon = "[PASS]" if passed else "[FAIL]"
        print(f" {icon} {method:<4} {path:<48} -> HTTP {r.status_code} ({latency} ms)")
        print(f"       Test: {name}")
        if not passed:
            print(f"       ERROR: {r.text[:200]}")
        results.append({
            "test": name,
            "method": method,
            "endpoint": path,
            "url": url,
            "expected_status": expected_status,
            "actual_status": r.status_code,
            "latency_ms": latency,
            "passed": passed,
            "sample_response": r.text[:300]
        })
    except Exception as e:
        print(f" [FAIL] {method:<4} {path} -> EXCEPTION: {e}")
        results.append({
            "test": name,
            "method": method,
            "endpoint": path,
            "url": url,
            "passed": False,
            "error": str(e)
        })

print("\n" + "=" * 80)
total = len(results)
passed_cnt = sum(1 for x in results if x.get("passed"))
print(f" Total Live Endpoints Tested : {total}")
print(f" Passed                     : {passed_cnt} [SUCCESS]")
print(f" Failed                     : {total - passed_cnt}")
print(f" Success Rate               : {round((passed_cnt / total) * 100, 1)}%")
print("=" * 80)

with open("live_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Live test results saved to 'live_test_results.json'")
