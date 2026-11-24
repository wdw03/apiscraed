"""
D247 Sports & Live Odds Client
Interacts with D247 / DiamondExch backend APIs for:
  - Live & upcoming match feeds (Cricket, Football, Tennis, etc.)
  - Comprehensive sports navigation tree
  - Real-time Match Odds (Back/Lay prices & market liquidity)
  - Bookmaker markets & Fancy markets
  - Server health & Geo-IP telemetry
"""

from typing import Any, Dict, List, Optional, Union
import requests
from d247_crypto import encrypt_cryptojs, decrypt_cryptojs, DEFAULT_CRYPTO_KEY


class SportsClient:
    """Client for D247 Sports, Live Odds, and Tournament navigation"""

    BASE_URL = "https://d247.com"

    # Sport IDs standard on Diamond / D247
    SPORT_CRICKET = 4
    SPORT_SOCCER = 1
    SPORT_TENNIS = 2

    def __init__(self, key: str = DEFAULT_CRYPTO_KEY, timeout: int = 10):
        self.key = key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://d247.com",
            "Referer": "https://d247.com/home"
        })

    def _post_encrypted(self, path: str, payload: Any) -> Dict[str, Any]:
        """Encrypts payload with CryptoJS AES, sends POST, and decrypts the response"""
        url = f"{self.BASE_URL}{path}"
        enc_data = encrypt_cryptojs(payload, self.key)
        resp = self.session.post(url, json={"data": enc_data}, timeout=self.timeout)
        resp.raise_for_status()
        
        json_resp = resp.json()
        if "data" in json_resp:
            decrypted = decrypt_cryptojs(json_resp["data"], self.key)
            return decrypted
        return json_resp

    def check_server(self) -> Dict[str, Any]:
        """Checks client IP, Geo-location, ASN, and proxy/hosting detection"""
        return self._post_encrypted("/api/front/checkserver", {})

    def get_tabs(self) -> Dict[str, Any]:
        """Fetches active sport tabs (Cricket, Football, Tennis, Casino, etc.)"""
        return self._post_encrypted("/api/front/tablist", {})

    def get_latest_events(self) -> Dict[str, Any]:
        """Fetches marquee/featured matches currently displayed on homepage banner"""
        return self._post_encrypted("/api/front/get_latest_events", {})

    def get_tree(self) -> Dict[str, Any]:
        """
        Fetches full hierarchical sports navigation tree:
        Sports -> Competitions / Leagues -> Matches
        """
        return self._post_encrypted("/api/front/get_tree_open_data", {})

    def get_live_matches(self, sport_id: int = SPORT_CRICKET) -> List[Dict[str, Any]]:
        """
        Fetches all live (in-play) and upcoming matches for a given sport.
        
        Args:
            sport_id: 4 for Cricket, 1 for Soccer, 2 for Tennis
            
        Returns:
            List of match objects with game ID (gmid), event name (ename), inplay flag, stime, etc.
        """
        res = self._post_encrypted(f"/api/front/get_highlight_open_data?etid={sport_id}", {"etid": sport_id, "type": "all"})
        data = res.get("data", {})
        # t1: In-play / featured, t2: upcoming
        matches = data.get("t1", []) + data.get("t2", [])
        return matches

    def get_game_details(self, game_id: Union[int, str], sport_id: int = SPORT_CRICKET) -> Dict[str, Any]:
        """Fetches match metadata (league, stream status, scorecard type)"""
        return self._post_encrypted("/api/front/game_detail_open", {"etid": sport_id, "gmid": int(game_id)})

    def get_game_odds(self, game_id: Union[int, str], sport_id: int = SPORT_CRICKET) -> Dict[str, Any]:
        """
        Fetches real-time market odds, bookmaker, fancy markets, and back/lay runners.
        
        Args:
            game_id: Numerical game ID (e.g. 609763268)
            sport_id: 4 for Cricket
            
        Returns:
            Structured dictionary with Match Odds, Bookmaker, Fancy, and parsed runners.
        """
        res = self._post_encrypted(
            f"/api/front/game_data_open?etId={sport_id}&gameId={game_id}",
            {"etid": sport_id, "gmid": str(game_id)}
        )
        
        markets_raw = res.get("data", [])
        parsed_markets = []
        
        for m in markets_raw:
            market_info = {
                "market_id": m.get("mid"),
                "market_name": m.get("mname"),
                "market_type": m.get("gtype"),
                "status": m.get("status"),
                "min_stake": m.get("min"),
                "max_stake": m.get("max"),
                "runners": []
            }
            
            for sec in m.get("section", []):
                runner = {
                    "selection_id": sec.get("sid"),
                    "name": sec.get("nat"),
                    "status": sec.get("gstatus"),
                    "back_prices": [],
                    "lay_prices": []
                }
                for o in sec.get("odds", []):
                    price = o.get("odds", 0)
                    size = o.get("size", 0)
                    if price > 0:
                        entry = {"price": price, "size": size}
                        if o.get("otype") == "back":
                            runner["back_prices"].append(entry)
                        elif o.get("otype") == "lay":
                            runner["lay_prices"].append(entry)
                market_info["runners"].append(runner)
                
            parsed_markets.append(market_info)

        return {
            "success": res.get("status") == 200,
            "status": res.get("status"),
            "msg": res.get("msg"),
            "game_id": game_id,
            "markets": parsed_markets,
            "raw": res
        }
