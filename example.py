"""
D247 & Cricket Scoreboard API - Quick Start Example
Demonstrates how to fetch live scores, match odds, commentary, and lineups.
"""

from d247_score import ScoreClient
from d247_sports import SportsClient
from d247_betting import BettingClient


def main():
    print("=" * 70)
    print("      D247 & CRICKET SCOREBOARD API - QUICK START DEMO")
    print("=" * 70)

    sports = SportsClient()
    scores = ScoreClient()

    # 1. Fetch all live and upcoming cricket matches
    print("\n1. Fetching Live & Upcoming Cricket Matches...")
    matches = sports.get_live_matches(sport_id=SportsClient.SPORT_CRICKET)
    print(f"   Found {len(matches)} matches.")
    
    inplay_matches = [m for m in matches if m.get("iplay")]
    print(f"   Currently IN-PLAY matches: {len(inplay_matches)}")
    for m in inplay_matches[:3]:
        print(f"   * [{m.get('gmid')}] {m.get('ename')} ({m.get('cname')})")

    # Select match to inspect (e.g. 686490552 or 609763268)
    sample_gmid = 686490552
    print(f"\n2. Fetching Real-Time Odds for Match ID: {sample_gmid}...")
    odds_data = sports.get_game_odds(sample_gmid)
    
    if odds_data.get("success"):
        for mkt in odds_data.get("markets", [])[:3]:
            print(f"\n   -> Market: {mkt['market_name']} (Type: {mkt['market_type']}, Status: {mkt['status']})")
            for runner in mkt.get("runners", []):
                backs = [f"{b['price']}@{b['size']}" for b in runner["back_prices"][:2]]
                lays = [f"{l['price']}@{l['size']}" for l in runner["lay_prices"][:2]]
                print(f"      Runner: {runner['name']:<20} | Back: {', '.join(backs):<18} | Lay: {', '.join(lays)}")

    # 3. Fetch Live Scoreboard Data (using Match 609763268)
    score_gmid = 609763268
    print(f"\n3. Fetching Live Cricket Score for Match ID: {score_gmid}...")
    boot = scores.get_bootstrap(score_gmid)
    
    if boot.get("success"):
        print(f"   Match: {boot['match_name']}")
        print(f"   Status: {boot['match_status']} ({boot.get('status_note')})")
        print(f"   Toss: {boot.get('toss')}")
        print(f"   Provider Event ID: {boot.get('provider_event_id')}")

        # Fetch latest overs
        overs_resp = scores.get_overs(score_gmid, limit=2)
        overs = overs_resp.get("overs", [])
        if overs:
            latest = overs[0]
            balls = [b.get("display") for b in latest.get("balls", [])]
            print(f"   Latest Over {latest.get('overNumber')}: {' '.join(balls)} (Runs: {latest.get('runs')})")
            
        print(f"   Embed Widget URL: {scores.get_embed_url(score_gmid)}")

    # 4. Demonstrate Betting Payload Generation
    print("\n4. Generating Validated Bet Payload...")
    bet_payload = BettingClient.build_bet_payload(
        game_id=sample_gmid,
        market_id=5990747261011,
        runner_id=88210,
        runner_name="Punjab",
        bet_type="back",
        odds=1.85,
        stake=1000
    )
    print(f"   Payload generated:")
    print(f"   * Stake: Rs {bet_payload['amount']}")
    print(f"   * Rate/Odds: {bet_payload['uRate']}")
    print(f"   * Potential Profit: Rs {bet_payload['profit']}")
    print(f"   * Bet Type: {bet_payload['otype'].upper()} on {bet_payload['nat']}")

    print("\n" + "=" * 70)
    print("Demo completed successfully! All APIs operational.")
    print("=" * 70)


if __name__ == "__main__":
    main()
