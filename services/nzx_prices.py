# services/nzx_prices.py

import os
import requests
from typing import Dict, List, Optional

BASE_URL = "https://nzxplorer.co.nz/api/v1"


# =========================
# ASK ENDPOINT (CORE FIX)
# =========================
def _ask_for_prices(tickers: List[str]) -> Dict[str, Optional[float]]:
    """
    Uses NZXplorer Copilot /ask endpoint to fetch multiple prices at once.
    """

    url = f"{BASE_URL}/ask"

    headers = {
        "X-API-Key": os.getenv("NZXPLORER_API_KEY", ""),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 Chrome/122 Safari/537.36",
    }

    # We explicitly ask for structured output
    payload = {
        "query": (
            "Return the latest prices for the following NZX tickers as JSON "
            "mapping ticker to price:\n\n" + ", ".join(tickers)
        ),
        "format": "json"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        print(f"[NZXplorer ASK] network error: {e}")
        return {t: None for t in tickers}

    if r.status_code != 200:
        print(f"[NZXplorer ASK] error {r.status_code}: {r.text}")
        return {t: None for t in tickers}

    try:
        data = r.json()

        # Try common response shapes defensively
        prices = (
            data.get("result")
            or data.get("data")
            or data
        )

        if not isinstance(prices, dict):
            print("[NZXplorer ASK] unexpected response format")
            return {t: None for t in tickers}

        return {t: prices.get(t) for t in tickers}

    except Exception as e:
        print(f"[NZXplorer ASK] parse error: {e}")
        return {t: None for t in tickers}


# =========================
# PUBLIC API
# =========================
def fetch_nzx_prices(tickers: List[str]) -> Dict[str, Optional[float]]:
    """
    Main entry point used by your system.
    Now fully batch-based via /ask.
    """

    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list")

    # clean input
    tickers = [t.upper().strip() for t in tickers]

    return _ask_for_prices(tickers)


# =========================
# LEGACY SUPPORT
# =========================
def get_price(ticker: str):
    """
    Optional single-ticker fallback (uses batch internally).
    """
    return fetch_nzx_prices([ticker]).get(ticker)
