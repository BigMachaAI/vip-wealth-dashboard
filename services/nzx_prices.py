# services/nzx_prices.py

import os
import time
import requests
from typing import Dict, List, Optional

BASE_URL = "https://nzxplorer.co.nz/api/v1"

REQUESTS_PER_MINUTE = 10
DELAY_BETWEEN_REQUESTS = 6.5  # safe spacing (60/10 = 6s, add buffer)


# =========================
# SINGLE PRICE CALL
# =========================
def _fetch_price(ticker: str) -> Optional[float]:
    url = f"{BASE_URL}/prices/{ticker}?format=llm"

    headers = {
        "X-API-Key": os.getenv("NZXPLORER_API_KEY", ""),
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        print(f"[NZXplorer] network error {ticker}: {e}")
        return None

    if r.status_code == 429:
        print(f"[NZXplorer] 429 rate limit for {ticker}")
        return None

    if r.status_code != 200:
        print(f"[NZXplorer] {r.status_code} for {ticker}")
        return None

    try:
        return float(r.json().get("price"))
    except:
        return None


# =========================
# BATCH HANDLER (KEY FIX)
# =========================
def fetch_nzx_prices(tickers: List[str]) -> Dict[str, Optional[float]]:
    """
    Fetch prices with strict rate limiting:
    - max 10 requests per minute
    - no caching
    - deterministic batching
    """

    results = {}

    for i, ticker in enumerate(tickers):

        # enforce rate limit
        if i > 0:
            time.sleep(DELAY_BETWEEN_REQUESTS)

        # extra safety: pause every 10 requests
        if i > 0 and i % REQUESTS_PER_MINUTE == 0:
            print("[NZXplorer] rate limit window hit → sleeping 60s")
            time.sleep(60)

        price = _fetch_price(ticker)
        results[ticker] = price

    return results


# =========================
# LEGACY SUPPORT (safe)
# =========================
def get_price(ticker: str):
    return fetch_nzx_prices([ticker]).get(ticker)
