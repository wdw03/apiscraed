"""
D247 & CloudFront Comprehensive API Test Suite
Automated test runner verifying all scraped APIs:
  - Cryptography (CryptoJS AES-256)
  - Live Score APIs (Bootstrap, Scorecard, Overs, Commentary, Lineup, Partnerships, Charts)
  - Sports & Odds APIs (Live Matches, Categories Tree, Match Odds, Bookmaker, Fancy)
  - Betting & User APIs (Payload validation, Auth check, Exposure)
"""

import time
import json
import sys
from typing import Any
from d247_crypto import encrypt_cryptojs, decrypt_cryptojs
from d247_score import ScoreClient
from d247_sports import SportsClient
from d247_betting import BettingClient


class TestRunner:
    def __init__(self):
        self.results = []
        self.score_client = ScoreClient()
        self.sports_client = SportsClient()
        self.betting_client = BettingClient()

    def record(self, test_name: str, category: str, passed: bool, duration_ms: float, details: str = "", data: Any = None):
        self.results.append({
            "name": test_name,
            "category": category,
            "passed": passed,
            "duration_ms": round(duration_ms, 2),
            "details": details,
            "data_summary": data
        })
        icon = "[PASS]" if passed else "[FAIL]"
        print(f" {icon} {category} -> {test_name} ({round(duration_ms, 2)} ms)")
        if details:
            print(f"       Info: {details}")

    def run_all(self):
        print("=" * 80)
        print("          D247 & CLOUDFRONT CRICKET APIS - COMPLETE TEST SUITE")
        print("=" * 80)
        start_time = time.time()

        # -------------------------------------------------------------
        # 1. CRYPTO ENGINE TESTS
        # -------------------------------------------------------------
        print("\n[PHASE 1] Testing CryptoJS AES-256 Crypto Engine...")
        t0 = time.time()
        try:
            sample_payload = {"etid": 4, "gmid": "609763268", "active": True, "amount": 1000.5}
            enc = encrypt_cryptojs(sample_payload)
            dec = decrypt_cryptojs(enc)
            passed = (dec == sample_payload and enc.startswith("U2FsdGVkX1"))
            self.record("CryptoJS AES Round-Trip", "Cryptography", passed, (time.time() - t0) * 1000,
                        f"Encrypted format starts with 'U2FsdGVkX1' (Salted__), Decrypted matches exactly")
        except Exception as e:
            self.record("CryptoJS AES Round-Trip", "Cryptography", False, (time.time() - t0) * 1000, str(e))

        # -------------------------------------------------------------
        # 2. SPORTS & ODDS ENGINE TESTS
        # -------------------------------------------------------------
        print("\n[PHASE 2] Testing D247 Sports & Odds Engine...")

        # 2.1 Check Server & Geo IP
        t0 = time.time()
        try:
            srv = self.sports_client.check_server()
            passed = srv.get("status") == "success"
            self.record("Check Server / Geo-IP", "Sports API", passed, (time.time() - t0) * 1000,
                        f"IP: {srv.get('query')}, Region: {srv.get('regionName')}, ISP: {srv.get('isp')}")
        except Exception as e:
            self.record("Check Server / Geo-IP", "Sports API", False, (time.time() - t0) * 1000, str(e))

        # 2.2 Navigation Tree
        t0 = time.time()
        try:
            tree = self.sports_client.get_tree()
            passed = tree.get("status") == 200
            t_data = tree.get("data", {})
            self.record("Sports Navigation Tree", "Sports API", passed, (time.time() - t0) * 1000,
                        f"Categories: t1={len(t_data.get('t1', []))}, t2={len(t_data.get('t2', []))}")
        except Exception as e:
            self.record("Sports Navigation Tree", "Sports API", False, (time.time() - t0) * 1000, str(e))

        # 2.3 Live & Upcoming Cricket Matches
        t0 = time.time()
        live_matches = []
        try:
            live_matches = self.sports_client.get_live_matches(SportsClient.SPORT_CRICKET)
            passed = len(live_matches) > 0
            sample_match = live_matches[0] if live_matches else {}
            self.record("Get Live & Upcoming Matches", "Sports API", passed, (time.time() - t0) * 1000,
                        f"Total matches found: {len(live_matches)}, Sample: {sample_match.get('ename')} (ID: {sample_match.get('gmid')})")
        except Exception as e:
            self.record("Get Live & Upcoming Matches", "Sports API", False, (time.time() - t0) * 1000, str(e))

        # Select a sample match for testing odds (e.g. 686490552 or 609763268 or live match)
        test_gmid = 686490552
        if live_matches:
            # Prefer inplay match if available
            inplay = [m for m in live_matches if m.get("iplay")]
            if inplay:
                test_gmid = inplay[0].get("gmid")
            else:
                test_gmid = live_matches[0].get("gmid")

        # 2.4 Game Details
        t0 = time.time()
        try:
            gdetail = self.sports_client.get_game_details(test_gmid)
            passed = gdetail.get("status") == 200
            self.record(f"Game Details (ID: {test_gmid})", "Sports API", passed, (time.time() - t0) * 1000,
                        f"Status: {gdetail.get('status')}, Msg: {gdetail.get('msg')}")
        except Exception as e:
            self.record(f"Game Details (ID: {test_gmid})", "Sports API", False, (time.time() - t0) * 1000, str(e))

        # 2.5 Real-Time Game Odds & Orderbook
        t0 = time.time()
        try:
            godds = self.sports_client.get_game_odds(test_gmid)
            passed = godds.get("success", False)
            markets = godds.get("markets", [])
            market_names = [m["market_name"] for m in markets[:4]]
            self.record(f"Game Odds & Orderbook (ID: {test_gmid})", "Sports API", passed, (time.time() - t0) * 1000,
                        f"Found {len(markets)} active markets: {', '.join(market_names)}")
        except Exception as e:
            self.record(f"Game Odds & Orderbook (ID: {test_gmid})", "Sports API", False, (time.time() - t0) * 1000, str(e))

        # -------------------------------------------------------------
        # 3. SCORE ENGINE TESTS (CloudFront)
        # -------------------------------------------------------------
        print("\n[PHASE 3] Testing CloudFront Score Engine...")

        # We know 609763268 and 686490552 have active scoreboard instances
        score_test_id = 609763268

        # 3.1 Score Bootstrap
        t0 = time.time()
        boot_res = {}
        try:
            boot_res = self.score_client.get_bootstrap(score_test_id)
            passed = boot_res.get("success", False)
            self.record(f"Score Bootstrap (ID: {score_test_id})", "Score API", passed, (time.time() - t0) * 1000,
                        f"Match: {boot_res.get('match_name')}, Status: {boot_res.get('match_status')}, Provider ID: {boot_res.get('provider_event_id')}")
        except Exception as e:
            self.record(f"Score Bootstrap (ID: {score_test_id})", "Score API", False, (time.time() - t0) * 1000, str(e))

        provider_id = boot_res.get("provider_event_id") or "provider-3:6fb54c7a-839e-4866-9ba4-26a4771677b4"

        # 3.2 Full Scorecard
        t0 = time.time()
        try:
            scard = self.score_client.get_scorecard(provider_id)
            passed = "scorecard" in scard
            innings = scard.get("scorecard", {}).get("innings", [])
            self.record("Full Scorecard", "Score API", passed, (time.time() - t0) * 1000,
                        f"Innings count: {len(innings)}")
        except Exception as e:
            self.record("Full Scorecard", "Score API", False, (time.time() - t0) * 1000, str(e))

        # 3.3 Ball-by-Ball Overs
        t0 = time.time()
        try:
            overs = self.score_client.get_overs(provider_id, innings_number=1, limit=10)
            passed = "overs" in overs
            overs_list = overs.get("overs", [])
            latest_over = overs_list[0] if overs_list else {}
            self.record("Ball-by-Ball Overs Commentary", "Score API", passed, (time.time() - t0) * 1000,
                        f"Overs returned: {len(overs_list)}, Latest: Over {latest_over.get('overNumber')}")
        except Exception as e:
            self.record("Ball-by-Ball Overs Commentary", "Score API", False, (time.time() - t0) * 1000, str(e))

        # 3.4 Text Commentary
        t0 = time.time()
        try:
            comm = self.score_client.get_commentary(provider_id, limit=10)
            passed = "entries" in comm
            entries = comm.get("entries", [])
            self.record("Play-by-Play Text Commentary", "Score API", passed, (time.time() - t0) * 1000,
                        f"Commentary entries returned: {len(entries)}")
        except Exception as e:
            self.record("Play-by-Play Text Commentary", "Score API", False, (time.time() - t0) * 1000, str(e))

        # 3.5 Lineup / Playing XI
        t0 = time.time()
        try:
            lineup = self.score_client.get_lineup(provider_id)
            passed = "lineup" in lineup
            teams = lineup.get("lineup", {}).get("teams", [])
            self.record("Playing XI & Bench Lineup", "Score API", passed, (time.time() - t0) * 1000,
                        f"Teams present: {len(teams)}")
        except Exception as e:
            self.record("Playing XI & Bench Lineup", "Score API", False, (time.time() - t0) * 1000, str(e))

        # 3.6 Partnerships
        t0 = time.time()
        try:
            parts = self.score_client.get_partnerships(provider_id)
            passed = "innings" in parts
            inn_count = len(parts.get("innings", []))
            self.record("Batting Partnerships", "Score API", passed, (time.time() - t0) * 1000,
                        f"Innings partnerships data: {inn_count}")
        except Exception as e:
            self.record("Batting Partnerships", "Score API", False, (time.time() - t0) * 1000, str(e))

        # 3.7 Worm / Run-Rate Charts
        t0 = time.time()
        try:
            charts = self.score_client.get_charts(provider_id)
            passed = "innings" in charts
            self.record("Worm / Run-Rate Charts", "Score API", passed, (time.time() - t0) * 1000,
                        f"Chart series present for {len(charts.get('innings', []))} innings")
        except Exception as e:
            self.record("Worm / Run-Rate Charts", "Score API", False, (time.time() - t0) * 1000, str(e))

        # 3.8 Embed Widget URL
        t0 = time.time()
        embed_url = self.score_client.get_embed_url(score_test_id)
        passed = embed_url.startswith("https://") and str(score_test_id) in embed_url
        self.record("Embed Widget URL Generator", "Score API", passed, (time.time() - t0) * 1000,
                    f"Embed URL: {embed_url}")

        # -------------------------------------------------------------
        # 4. BETTING & USER ACCOUNT TESTS
        # -------------------------------------------------------------
        print("\n[PHASE 4] Testing Betting & User Account Engine...")

        # 4.1 Bet Payload Builder & Validation
        t0 = time.time()
        try:
            payload = BettingClient.build_bet_payload(
                game_id=609763268,
                market_id=5990747261011,
                runner_id=88210,
                runner_name="South Africa",
                bet_type="back",
                odds=1.50,
                stake=500
            )
            passed = (payload["profit"] == 250.0 and payload["otype"] == "back" and payload["amount"] == 500)
            self.record("Bet Payload Builder & Profit Validation", "Betting API", passed, (time.time() - t0) * 1000,
                        f"Calculated Stake: {payload['amount']}, Rate: {payload['uRate']}, Profit: {payload['profit']}")
        except Exception as e:
            self.record("Bet Payload Builder & Profit Validation", "Betting API", False, (time.time() - t0) * 1000, str(e))

        # 4.2 Unauthenticated Access Handling
        t0 = time.time()
        try:
            u_data = self.betting_client.get_user_data()
            # Must properly detect unauthenticated state and return 401 'Please Login'
            passed = (u_data.get("authenticated") is False and u_data.get("status_code") == 401)
            self.record("Auth Protection & 401 Decryption", "Betting API", passed, (time.time() - t0) * 1000,
                        f"Gracefully intercepted 401: '{u_data.get('error')}'")
        except Exception as e:
            self.record("Auth Protection & 401 Decryption", "Betting API", False, (time.time() - t0) * 1000, str(e))

        # -------------------------------------------------------------
        # SUMMARY
        # -------------------------------------------------------------
        total_time = (time.time() - start_time) * 1000
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests

        print("\n" + "=" * 80)
        print("                               TEST SUMMARY")
        print("=" * 80)
        print(f" Total Tests Run    : {total_tests}")
        print(f" Passed Tests       : {passed_tests} [SUCCESS]")
        print(f" Failed Tests       : {failed_tests}")
        print(f" Success Rate       : {round((passed_tests / total_tests) * 100, 1)}%")
        print(f" Total Elapsed Time : {round(total_time, 2)} ms")
        print("=" * 80)

        # Save results to JSON
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{round((passed_tests / total_tests) * 100, 1)}%",
                "results": self.results
            }, f, indent=2)
        print("\nFull test results saved to 'test_results.json'")

        return failed_tests == 0


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
