"""
D247 Live Score Client Module
Communicates with CloudFront live cricket scoreboard service (dzfytm4o128av.cloudfront.net).
"""

import urllib.parse
from typing import Any, Dict, Optional, Union
import requests


class ScoreClient:
    """Client for CloudFront Cricket Scoreboard APIs"""

    BASE_URL = "https://dzfytm4o128av.cloudfront.net"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        # Direct desktop User-Agent without external origin to avoid CORS 403
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        if resp.status_code == 404:
            return {"success": False, "error": "Match not found or score not available for this event", "status_code": 404}
        if resp.status_code == 403:
            return {"success": False, "error": "Access forbidden: verify event ID format or provider ID", "status_code": 403}
        resp.raise_for_status()
        return resp.json()

    def get_embed_url(self, game_id: Union[int, str], theme: str = "dark") -> str:
        """Returns direct iframe embed URL for cricket scoreboard widget"""
        return f"{self.BASE_URL}/embed/{game_id}?theme={theme}"

    def get_bootstrap(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """
        Fetches live score summary, current inning, active batsman, bowler, and providerEventId.
        """
        data = self._get(f"/v1/events/{game_id}/bootstrap")
        if not data.get("score"):
            return data
            
        score_obj = data["score"]
        event = score_obj.get("event", {})
        detail = event.get("detail", {}) if isinstance(event, dict) else {}
        sport_details = score_obj.get("sportDetails", {}) if isinstance(score_obj.get("sportDetails"), dict) else {}
        inner_score = score_obj.get("score", {}) if isinstance(score_obj.get("score"), dict) else {}
        
        status_val = score_obj.get("status")
        match_status = status_val if isinstance(status_val, str) else (status_val.get("label") or status_val.get("state") if isinstance(status_val, dict) else None)
        
        sd_status = sport_details.get("status", {})
        if isinstance(sd_status, dict):
            status_label = sd_status.get("label") or sd_status.get("state")
            status_note = sd_status.get("note")
        else:
            status_label = str(sd_status) if sd_status else match_status
            status_note = None

        toss_obj = sport_details.get("toss")
        toss_text = toss_obj.get("text") if isinstance(toss_obj, dict) else str(toss_obj) if toss_obj else None

        striker = sport_details.get("striker")
        non_striker = sport_details.get("nonStriker")
        bowler = sport_details.get("bowler")

        return {
            "success": True,
            "game_id": game_id,
            "provider_event_id": score_obj.get("eventId"),
            "match_name": f"{detail.get('homeTeam', {}).get('name', 'Home')} vs {detail.get('awayTeam', {}).get('name', 'Away')}",
            "home_team": detail.get("homeTeam", {}).get("name"),
            "away_team": detail.get("awayTeam", {}).get("name"),
            "match_status": status_label or match_status,
            "status_note": status_note,
            "runs": inner_score.get("runs"),
            "wickets": inner_score.get("wickets"),
            "overs": inner_score.get("overs"),
            "run_rate": inner_score.get("runRate"),
            "format": event.get("format") if isinstance(event, dict) else None,
            "toss": toss_text,
            "striker": striker.get("name") if isinstance(striker, dict) else None,
            "non_striker": non_striker.get("name") if isinstance(non_striker, dict) else None,
            "current_bowler": bowler.get("name") if isinstance(bowler, dict) else None,
            "this_over": sport_details.get("thisOver", []),
            "raw": data
        }

    def _resolve_provider_id(self, event_identifier: Union[int, str]) -> str:
        """Resolves numeric game_id to provider-3:... eventId if needed"""
        ev_str = str(event_identifier)
        if "provider-" in ev_str or ":" in ev_str:
            return ev_str
        boot = self.get_bootstrap(ev_str)
        if boot.get("provider_event_id"):
            return boot["provider_event_id"]
        return ev_str

    def get_scorecard(self, event_identifier: Union[int, str]) -> Dict[str, Any]:
        """Fetches full scorecard with innings, batsmen statistics, bowlers statistics, and wickets."""
        provider_id = self._resolve_provider_id(event_identifier)
        encoded_id = urllib.parse.quote(provider_id)
        return self._get(f"/v1/events/{encoded_id}/cricket/scorecard")

    def get_overs(self, event_identifier: Union[int, str], innings_number: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Fetches ball-by-ball commentary for each completed and in-progress over."""
        provider_id = self._resolve_provider_id(event_identifier)
        encoded_id = urllib.parse.quote(provider_id)
        return self._get(f"/v1/events/{encoded_id}/cricket/overs", params={"inningsNumber": innings_number, "limit": limit})

    def get_commentary(self, event_identifier: Union[int, str], limit: int = 50) -> Dict[str, Any]:
        """Fetches textual play-by-play commentary stream"""
        provider_id = self._resolve_provider_id(event_identifier)
        encoded_id = urllib.parse.quote(provider_id)
        return self._get(f"/v1/events/{encoded_id}/cricket/commentary", params={"limit": limit})

    def get_lineup(self, event_identifier: Union[int, str]) -> Dict[str, Any]:
        """Fetches playing XI, captain, wicket-keeper, and bench players for both teams"""
        provider_id = self._resolve_provider_id(event_identifier)
        encoded_id = urllib.parse.quote(provider_id)
        return self._get(f"/v1/events/{encoded_id}/cricket/lineup")

    def get_partnerships(self, event_identifier: Union[int, str]) -> Dict[str, Any]:
        """Fetches batting partnerships by wicket"""
        provider_id = self._resolve_provider_id(event_identifier)
        encoded_id = urllib.parse.quote(provider_id)
        return self._get(f"/v1/events/{encoded_id}/cricket/partnerships")

    def get_charts(self, event_identifier: Union[int, str]) -> Dict[str, Any]:
        """Fetches run-rate progression and worm chart data points"""
        provider_id = self._resolve_provider_id(event_identifier)
        encoded_id = urllib.parse.quote(provider_id)
        return self._get(f"/v1/events/{encoded_id}/cricket/charts")
