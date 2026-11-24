"""
D247 Betting & User Account Client Module
"""

from typing import Any, Dict, List, Optional, Union
import requests
from .crypto import encrypt_cryptojs, decrypt_cryptojs, DEFAULT_CRYPTO_KEY


class BettingClient:
    """Client for D247 User Account and Betting APIs"""

    BASE_URL = "https://d247.com"

    def __init__(self, token: Optional[str] = None, key: str = DEFAULT_CRYPTO_KEY, timeout: int = 15):
        self.key = key
        self.timeout = timeout
        self.token = token
        self.session = requests.Session()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://d247.com",
            "Referer": "https://d247.com/home"
        }
        self.session.headers.update(headers)
        
        if self.token:
            self.set_token(self.token)

    def set_token(self, token: str):
        """Updates the session with a new authentication token"""
        self.token = token
        self.session.cookies.set("g_token", token, domain="d247.com")

    def _post_encrypted(self, path: str, payload: Any) -> Dict[str, Any]:
        """Encrypts payload with CryptoJS AES, sends POST with cookies, and decrypts response"""
        url = f"{self.BASE_URL}{path}"
        enc_data = encrypt_cryptojs(payload, self.key)
        resp = self.session.post(url, json={"data": enc_data}, timeout=self.timeout)
        
        if resp.status_code == 401:
            try:
                dec = decrypt_cryptojs(resp.json().get("data", ""), self.key)
                return {"authenticated": False, "status_code": 401, "error": dec.get("msg", "Please Login"), "raw": dec}
            except Exception:
                return {"authenticated": False, "status_code": 401, "error": "Please Login"}

        resp.raise_for_status()
        json_resp = resp.json()
        if "data" in json_resp:
            return decrypt_cryptojs(json_resp["data"], self.key)
        return json_resp

    def get_user_data(self) -> Dict[str, Any]:
        """Fetches logged-in user's balance, credit limit, current exposure, and username."""
        return self._post_encrypted("/api/front/userdata", {})

    def get_user_book(self, game_id: Union[int, str]) -> Dict[str, Any]:
        """Fetches user's open bets and position/exposure on a specific game."""
        return self._post_encrypted("/api/front/userbook", {"gmid": str(game_id)})

    def get_button_list(self) -> Dict[str, Any]:
        """Fetches user's custom quick bet stake button values (e.g. 100, 500, 1000)"""
        return self._post_encrypted("/api/front/buttonlist", {})

    def get_current_bets(self) -> Dict[str, Any]:
        """Fetches all open/unmatched/matched bets across sports"""
        return self._post_encrypted("/api/front/currentbets", {})

    def get_account_statement(self, start_date: str = "", end_date: str = "") -> Dict[str, Any]:
        """Fetches historical bet settlement records and account PnL statement"""
        return self._post_encrypted("/api/front/accountstatement", {"fromDate": start_date, "toDate": end_date})

    @staticmethod
    def build_bet_payload(
        game_id: Union[int, str],
        market_id: Union[int, str],
        runner_id: Union[int, str],
        runner_name: str,
        bet_type: str,
        odds: float,
        stake: float,
        market_type: str = "match"
    ) -> Dict[str, Any]:
        """
        Constructs and validates the exact payload expected by /api/front/placebet.
        """
        bet_type_clean = bet_type.lower().strip()
        if bet_type_clean not in ["back", "lay"]:
            raise ValueError(f"Invalid bet_type '{bet_type}'. Must be 'back' or 'lay'.")
        if stake <= 0:
            raise ValueError(f"Stake must be greater than 0, got {stake}")
        if odds <= 1.0 and market_type != "fancy":
            raise ValueError(f"Odds must be greater than 1.0 for match markets, got {odds}")

        if bet_type_clean == "back":
            profit = round(stake * (odds - 1.0), 2)
        else:
            profit = round(stake * (odds - 1.0), 2)

        return {
            "gmid": int(game_id),
            "mid": int(market_id),
            "sid": int(runner_id),
            "nat": runner_name,
            "otype": bet_type_clean,
            "uRate": float(odds),
            "amount": float(stake),
            "profit": profit,
            "gtype": market_type,
            "betStatus": True
        }

    def place_bet(self, bet_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submits a bet to D247 exchange."""
        return self._post_encrypted("/api/front/placebet", bet_payload)
