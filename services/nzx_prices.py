# services/nzx_prices.py

import os
import time
import requests
from typing import Optional

BASE_URL = "https://nzxplorer.co.nz/api/v1"

# simple in-memory cache for GitHub Actions run
_PRICE_CACHE = {}


class NZXplorerBlocked(Exception):
    pass


def _headers():
    return {
        "X-API-Key": os.getenv("NZXPLORER_API_KEY", ""),
        # 👇 critical: bypass bot heuristics
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Connection": "keep-alive",
    }


def _fetch_price_from_api(ticker: str) -> Optional[float]:
    url = f"{BASE_URL}/prices/{ticker}?format=llm"

    try:
        resp = requests.get(url, headers=_headers(), timeout=10)
    except Exception as e:
        print(f"[NZXplorer] Network error for {ticker}: {e}")
        return None

    # 🧨 Explicit bot protection detection
    if resp.status_code == 403:
        raise NZXplorerBlocked(
            f"403 blocked by NZXplorer bot protection for {ticker}: {resp.text}"
        )

    if resp.status_code == 429:
        print(f"[NZXplorer] Rate limited for {ticker}, backing off...")
        time.sleep(1.0)
        return None

    if resp.status_code != 200:
        print(f"[NZXplorer] Bad response {resp.status_code} for {ticker}: {resp.text}")
        return None

    try:
        data = resp.json()
        return float(data.get("price"))
    except Exception:
        print(f"[NZXplorer] JSON parse error for {ticker}")
        return None


def get_price(ticker: str) -> Optional[float]:
    """
    Main entry point used by calculations layer.
    Never returns 0. Only None or valid price.
    """

    # 1. cache (prevents repeated API calls in same run)
    if ticker in _PRICE_CACHE:
        return _PRICE_CACHE[ticker]

    # 2. API fetch (with light pacing to avoid bot detection)
    time.sleep(0.25)  # 👈 IMPORTANT: avoids burst detection

    price = _fetch_price_from_api(ticker)

    if price is not None and price > 0:
        _PRICE_CACHE[ticker] = price
        return price

    # 3. fail gracefully (DO NOT RETURN ZERO)
    return None

# ===== Backward compatibility layer =====

def fetch_nzx_prices(ticker: str):
    """
    Legacy wrapper so existing code doesn't break.
    Returns a float or None.
    """
    return get_price(ticker)
