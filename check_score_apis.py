import requests
import json

base_url = "https://apiscraed.vercel.app"
game_id = "609763268"

endpoints = [
    ("1a. Score Overview (Dedicated)", f"/api/score/bootstrap/{game_id}"),
    ("1b. Score Overview (Shortcut)", f"/api/live/{game_id}"),
    ("2a. Scoreboard / Scorecard (Dedicated)", f"/api/score/scorecard/{game_id}"),
    ("2b. Scoreboard / Scorecard (Shortcut)", f"/api/scorecard/{game_id}"),
    ("3a. Commentary Text Stream (Dedicated)", f"/api/score/commentary/{game_id}?limit=5"),
    ("3b. Commentary Text Stream (Shortcut)", f"/api/commentary/{game_id}?limit=5"),
    ("4a. Batting Partnerships (Dedicated)", f"/api/score/partnerships/{game_id}"),
    ("4b. Batting Partnerships (Shortcut)", f"/api/partnerships/{game_id}"),
    ("5a. Playing XI & Lineup (Dedicated)", f"/api/score/lineup/{game_id}"),
    ("5b. Playing XI & Lineup (Shortcut)", f"/api/lineup/{game_id}"),
    ("6a. Ball-by-Ball Overs Log (Dedicated)", f"/api/score/overs/{game_id}?innings=1&limit=2"),
    ("6b. Ball-by-Ball Overs Log (Shortcut)", f"/api/overs/{game_id}?innings=1&limit=2"),
    ("7a. Worm Charts & Run Rate (Dedicated)", f"/api/score/charts/{game_id}"),
    ("7b. Worm Charts & Run Rate (Shortcut)", f"/api/charts/{game_id}"),
    ("8a. Scoreboard Embed Widget (Dedicated)", f"/api/score/embed/{game_id}"),
    ("8b. Scoreboard Embed Widget (Shortcut)", f"/api/embed/{game_id}")
]

print("=== CHECKING ALL SCORE-RELATED APIS ON VERCEL ===")
results = []

for name, path in endpoints:
    url = base_url + path
    try:
        r = requests.get(url, timeout=12)
        status = r.status_code
        data = r.json() if "json" in r.headers.get("content-type", "") else r.text[:200]
        
        info = {}
        info["name"] = name
        info["url"] = url
        info["status"] = status
        info["available"] = (status == 200)
        
        if status == 200 and isinstance(data, dict):
            if "scorecard" in data:
                inn = data["scorecard"].get("innings", [])
                info["preview"] = f"{len(inn)} Innings recorded with full batting/bowling statistics"
            elif "entries" in data:
                txt = data["entries"][0].get("text", "")[:70] if data.get("entries") else ""
                info["preview"] = f"{len(data.get('entries', []))} commentary balls. Latest: '{txt}...'"
            elif "lineup" in data:
                teams = data["lineup"].get("teams", [])
                team_names = [t.get("name") for t in teams]
                p_count = len(teams[0].get("players", [])) if teams else 0
                info["preview"] = f"Teams: {team_names}, Players per squad: ~{p_count} players with captain & keeper"
            elif "partnerships" in path or ("innings" in data and "partnerships" in str(data)):
                info["preview"] = f"Partnerships per wicket recorded for {len(data.get('innings', []))} innings"
            elif "match_name" in data:
                info["preview"] = f"{data.get('match_name')} | Status: {data.get('match_status')} | Runs: {data.get('runs')}/{data.get('wickets')} ({data.get('overs')} ov) | Toss: {data.get('toss')}"
            elif "overs" in data:
                latest = data["overs"][0] if data.get("overs") else {}
                balls = [b.get("display") for b in latest.get("balls", [])]
                info["preview"] = f"Latest Over {latest.get('overNumber')}: {' '.join(balls)} (Bowler: {latest.get('bowler', {}).get('name')})"
            elif "embed_url" in data:
                info["preview"] = f"Embed Iframe URL: {data.get('embed_url')}"
            else:
                info["preview"] = f"Keys: {list(data.keys())[:5]}"
        else:
            info["preview"] = str(data)[:150]

        results.append(info)
        icon = "✅ AVAILABLE" if status == 200 else "❌ NOT AVAILABLE"
        print(f"\n{icon} -> {name}")
        print(f"  URL    : {url}")
        print(f"  Status : HTTP {status}")
        print(f"  Detail : {info['preview']}")

    except Exception as e:
        print(f"\n❌ FAILED -> {name}: {e}")

print("\n" + "="*80)
total = len(results)
avail = sum(1 for x in results if x["available"])
print(f"TOTAL CHECKED: {total} | AVAILABLE: {avail} | MISSING: {total - avail}")
print("="*80)
