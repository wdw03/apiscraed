# apiscraed - D247 & Cricket Scoreboard API Suite

Comprehensive reverse-engineered API documentation, Python client library, and automated test suite for **D247 / DiamondExch** and the **CloudFront Cricket Live Scoreboard**.

---

## 📌 Executive Summary & Test Results

All APIs captured in the Burp Suite export file (`ds`) have been thoroughly parsed, analyzed, tested, and reverse-engineered into a high-performance Python package.

### 🧪 Test Suite Summary
- **Total Automated Tests**: 16
- **Passed**: 16 (**100% Success Rate**)
- **Execution Time**: ~5.4 seconds
- **Authentication Bypass**: Discovered public Open endpoints (`game_data_open`, `get_highlight_open_data`, `get_tree_open_data`) that deliver real-time odds, markets, and in-play fixtures **without needing login or session cookies**.

```
================================================================================
          D247 & CLOUDFRONT CRICKET APIS - COMPLETE TEST SUITE
================================================================================
 [PASS] Cryptography -> CryptoJS AES Round-Trip (30.57 ms)
 [PASS] Sports API   -> Check Server / Geo-IP (2174.38 ms)
 [PASS] Sports API   -> Sports Navigation Tree (405.01 ms)
 [PASS] Sports API   -> Get Live & Upcoming Matches (229.18 ms)
 [PASS] Sports API   -> Game Details (ID: 838843313) (211.83 ms)
 [PASS] Sports API   -> Game Odds & Orderbook (ID: 838843313) (256.65 ms)
 [PASS] Score API    -> Score Bootstrap (ID: 609763268) (444.72 ms)
 [PASS] Score API    -> Full Scorecard (228.58 ms)
 [PASS] Score API    -> Ball-by-Ball Overs Commentary (219.62 ms)
 [PASS] Score API    -> Play-by-Play Text Commentary (244.46 ms)
 [PASS] Score API    -> Playing XI & Bench Lineup (215.27 ms)
 [PASS] Score API    -> Batting Partnerships (236.57 ms)
 [PASS] Score API    -> Worm / Run-Rate Charts (217.34 ms)
 [PASS] Score API    -> Embed Widget URL Generator (0.01 ms)
 [PASS] Betting API  -> Bet Payload Builder & Profit Validation (0.02 ms)
 [PASS] Betting API  -> Auth Protection & 401 Decryption (362.22 ms)
================================================================================
 Total Tests: 16 | Passed: 16 | Failed: 0 | Success Rate: 100.0%
================================================================================
```

---

## 📂 Project Structure

```
C:\Users\hqsav\OneDrive\Desktop\apiscarper\
├── ds                           # Raw Burp Suite XML capture (1.8 MB)
├── d247_crypto.py               # Bidirectional CryptoJS AES-256-CBC engine
├── d247_score.py                # CloudFront live cricket scoreboard client
├── d247_sports.py               # D247 sports, matches, and real-time odds client
├── d247_betting.py              # D247 betting, user account & exposure client
├── run_tests.py                 # Automated master test runner
├── example.py                   # Quick-start demonstration script
├── test_results.json            # Machine-readable test execution report
└── README.md                    # Full documentation & API guide
```

---

## 🔐 1. Cryptography & Encryption Protocol

D247 encrypts both request bodies and response data using **CryptoJS AES-256-CBC** with OpenSSL-style key derivation.

- **Secret Key**: `cae7b808-8b1e-4f47-87a5-1a4b6a08030e`
- **Prefix Header**: `Salted__` (Base64: `U2FsdGVkX1`)
- **Salt**: 8 random bytes
- **Key Derivation**: OpenSSL `EVP_BytesToKey` algorithm with MD5 hash loop (32-byte key + 16-byte IV).

### Payload Format:
```json
{
  "data": "U2FsdGVkX19NnFV9sViOqyw3KTm/IZIQb9EJWSvTRbGnmonnrMCgPFClRlkzhtV4"
}
```

### Python Crypto Usage (`d247_crypto.py`):
```python
from d247_crypto import encrypt_cryptojs, decrypt_cryptojs

# Encrypt any dict/data
encrypted_b64 = encrypt_cryptojs({"etid": 4, "type": "all"})

# Decrypt encrypted string
decrypted_json = decrypt_cryptojs(encrypted_b64)
print(decrypted_json)  # {'etid': 4, 'type': 'all'}
```

---

## 🏏 2. Cricket Live Score APIs (`dzfytm4o128av.cloudfront.net`)

### ⚠️ Important Access Rule
The CloudFront scoreboard domain validates CORS. If an external `Origin: https://d247.com` header is sent, it returns `HTTP 403 Forbidden`. Requests must be made **directly** or with standard desktop User-Agents without origin spoofing.

### 🔄 The Two-Tier Event ID Resolution
1. **Step 1 (Bootstrap)**: Query with numerical `gameId` (e.g., `609763268`).
2. **Step 2 (Extract Provider ID)**: Bootstrap returns the provider ID (e.g. `provider-3:6fb54c7a-839e-4866-9ba4-26a4771677b4`).
3. **Step 3 (Detailed Endpoints)**: Pass URL-encoded provider ID (`urllib.parse.quote(...)`) to fetch overs, scorecards, lineups, and charts.

### Scoreboard Endpoints Reference:

| Endpoint | Method | Params / Path | Description |
|---|---|---|---|
| `/v1/events/{gameId}/bootstrap` | GET | `gameId` (int) | Match status, current score, toss, active batsmen, bowler |
| `/v1/events/{providerId}/cricket/scorecard` | GET | `providerId` (str) | Full innings scorecard, batsmen runs/balls, bowler figures |
| `/v1/events/{providerId}/cricket/overs` | GET | `inningsNumber=1&limit=50` | Ball-by-ball commentary (dots, 1s, 4s, 6s, wickets) |
| `/v1/events/{providerId}/cricket/commentary` | GET | `limit=50` | Textual play-by-play live commentary |
| `/v1/events/{providerId}/cricket/lineup` | GET | `providerId` (str) | Playing XI, captain, wicket-keeper, bench |
| `/v1/events/{providerId}/cricket/partnerships` | GET | `providerId` (str) | Batting partnerships for every wicket |
| `/v1/events/{providerId}/cricket/charts` | GET | `providerId` (str) | Run rate graphs and Worm charts |
| `/embed/{gameId}?theme=dark` | GET | `theme=dark\|light` | Embeddable responsive HTML iframe scoreboard widget |
| `/ws` | WSS | WebSocket | Real-time score websocket stream (`subscribe_score`) |

### 🚀 Production Vercel Serverless Endpoints (`https://apiscraed.vercel.app`):

All 8 cricket endpoints are deployed as dedicated standalone routes with auto-resolution (accepting either numeric `game_id` or provider `event_id`):

| # | Dedicated Endpoint | Shortcut Alias | Description | Auth |
|---|---|---|---|:---:|
| 1 | `GET /api/score/bootstrap/{match_id}` | `GET /api/live/{match_id}` | Live score overview, toss, runs, wickets, overs | Free / No Auth |
| 2 | `GET /api/score/scorecard/{match_id}` | `GET /api/scorecard/{match_id}` | Full innings batting & bowling scorecards | Free / No Auth |
| 3 | `GET /api/score/commentary/{match_id}` | `GET /api/commentary/{match_id}` | Live ball-by-ball text commentary stream | Free / No Auth |
| 4 | `GET /api/score/partnerships/{match_id}` | `GET /api/partnerships/{match_id}` | Batting partnerships breakdown per wicket | Free / No Auth |
| 5 | `GET /api/score/lineup/{match_id}` | `GET /api/lineup/{match_id}` | Playing XI, captain, keeper & bench squads | Free / No Auth |
| 6 | `GET /api/score/overs/{match_id}` | `GET /api/overs/{match_id}` | Ball-by-ball delivery log & bowler figures | Free / No Auth |
| 7 | `GET /api/score/charts/{match_id}` | `GET /api/charts/{match_id}` | Worm chart coordinates & run rate vectors | Free / No Auth |
| 8 | `GET /api/score/embed/{match_id}` | `GET /api/embed/{match_id}` | Responsive HTML iframe widget URL | Free / No Auth |

### Python Score Example:
```python
from d247_score import ScoreClient

score = ScoreClient()

# 1. Get Live Overview
match = score.get_bootstrap(609763268)
print(f"Match: {match['match_name']} | Status: {match['match_status']}")
print(f"Toss: {match['toss']}")

# 2. Get Ball-by-Ball Overs
overs = score.get_overs(609763268, innings_number=1, limit=5)
latest_over = overs['overs'][0]
balls = [b['display'] for b in latest_over['balls']]
print(f"Latest Over {latest_over['overNumber']}: {' '.join(balls)}")

# 3. Get Iframe Widget URL
print("Widget:", score.get_embed_url(609763268))
```

---

## 📈 3. D247 Sports, Matches & Real-Time Odds APIs (`d247.com`)

### ⚡ Public Endpoints (NO Login or Cookies Required)

| Endpoint | Method | Payload | Description |
|---|---|---|---|
| `/api/front/get_highlight_open_data?etid=4` | POST | `{"etid": 4, "type": "all"}` | Live and upcoming cricket matches list |
| `/api/front/get_tree_open_data` | POST | `{}` | Complete sports navigation tree |
| `/api/front/game_data_open?etId=4&gameId={gmid}` | POST | `{"etid": 4, "gmid": "609763268"}` | Real-time Match Odds, Bookmaker, Fancy, Back/Lay prices & sizes |
| `/api/front/game_detail_open` | POST | `{"etid": 4, "gmid": 609763268}` | Match metadata (league, stream status) |
| `/api/front/checkserver` | POST | `{}` | Geo-IP telemetry, ISP, and proxy status |
| `/api/front/tablist` | POST | `{}` | Active sports tabs |
| `/api/front/get_latest_events` | POST | `{}` | Marquee homepage events |

### 🔒 Private Endpoints (Require `g_token` Cookie)

| Endpoint | Method | Payload | Description |
|---|---|---|---|
| `/api/front/userdata` | POST | `{}` | User balance, credit limit, exposure, username |
| `/api/front/userbook` | POST | `{"gmid": "609763268"}` | Open bets and exposure for specific match |
| `/api/front/placebet` | POST | `betData` object | Place a bet on Match Odds, Bookmaker, or Fancy |
| `/api/front/buttonlist` | POST | `{}` | Custom quick stake button values |
| `/api/front/currentbets` | POST | `{}` | Active un-matched / matched bets across sports |
| `/api/front/accountstatement` | POST | `{"fromDate": "", "toDate": ""}` | Settlement history and PnL statement |

### Python Sports & Odds Example:
```python
from d247_sports import SportsClient

sports = SportsClient()

# 1. Fetch all live cricket matches
matches = sports.get_live_matches(sport_id=SportsClient.SPORT_CRICKET)
for m in matches:
    if m.get("iplay"):
        print(f"[INPLAY] ID: {m['gmid']} | {m['ename']} | League: {m['cname']}")

# 2. Fetch live Back/Lay odds for a match
odds = sports.get_game_odds(686490552)
for mkt in odds["markets"]:
    print(f"\nMarket: {mkt['market_name']}")
    for runner in mkt["runners"]:
        back = runner["back_prices"][0] if runner["back_prices"] else {}
        lay = runner["lay_prices"][0] if runner["lay_prices"] else {}
        print(f"  {runner['name']:<18} | Back: {back.get('price')}@{back.get('size')} | Lay: {lay.get('price')}@{lay.get('size')}")
```

---

## 💰 4. Betting Execution & Validation

### Bet Data Payload Schema:
```json
{
  "gmid": 609763268,
  "mid": 5990747261011,
  "sid": 88210,
  "nat": "South Africa",
  "otype": "back",
  "uRate": 1.50,
  "amount": 1000.0,
  "profit": 500.0,
  "gtype": "match",
  "betStatus": true
}
```

### Python Betting Example:
```python
from d247_betting import BettingClient

# Initialize with session cookie from logged-in browser
betting = BettingClient(token="s%3APM9l_qB6JQ3G8s3fZauSdYGDef3JGb4W...")

# 1. Check Balance
user_info = betting.get_user_data()
print("Balance:", user_info.get("data", {}).get("bal"))

# 2. Build & Validate Bet Payload
payload = BettingClient.build_bet_payload(
    game_id=609763268,
    market_id=5990747261011,
    runner_id=88210,
    runner_name="South Africa",
    bet_type="back",
    odds=1.50,
    stake=1000
)

# 3. Submit Bet
# response = betting.place_bet(payload)
# print(response)
```

---

## 🚀 Quick Start & How to Run

1. **Run Full Test Suite**:
```bash
python run_tests.py
```

2. **Run Interactive Demo**:
```bash
python example.py
```

3. **Check Test Results JSON**:
Review `test_results.json` for detailed latency metrics and responses.
