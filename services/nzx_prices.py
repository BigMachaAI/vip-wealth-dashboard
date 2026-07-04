# services/nzx_prices.py

import os
import time
import random
import requests
from typing import Dict, List, Optional

BASE_URL = "https://nzxplorer.co.nz/api/v1"

_CACHE: Dict[str, float] = {}


# =========================
# BACKOFF (anti-rate-limit)
# =========================
def _smart_sleep():
    time.sleep(0.5 + random.random() * 0.5)


# =========================
# LOW LEVEL API CALL
# =========================
def _fetch_from_nzxplorer(ticker: str) -> Optional[float]:
    url = f"{BASE_URL}/prices/{ticker}?format=llm"

    headers = {
        "X-API-Key": os.getenv("NZXPLORER_API_KEY", ""),
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        print(f"[NZXplorer] Network error for {ticker}: {e}")
        return None

    if r.status_code == 403:
        print(f"[NZXplorer] 403 blocked for {ticker}")
        return None

    if r.status_code == 429:
        print(f"[NZXplorer] rate limited for {ticker}")
        return None

    if r.status_code != 200:
        print(f"[NZXplorer] bad response {r.status_code} for {ticker}")
        return None

    try:
        data = r.json()
        price = data.get("price")
        return float(price) if price is not None else None
    except Exception:
        print(f"[NZXplorer] JSON parse error for {ticker}")
        return None


# =========================
# SINGLE TICKER
# =========================
def get_price(ticker: str) -> Optional[float]:
    if not isinstance(ticker, str):
        raise TypeError(f"ticker must be str, got {type(ticker)}")

    ticker = ticker.strip().upper()

    if ticker in _CACHE:
        return _CACHE[ticker]

    _smart_sleep()

    price = _fetch_from_nzxplorer(ticker)

    if price is not None and price > 0:
        _CACHE[ticker] = price
        return price

    return None


# =========================
# BATCH PRICES
# =========================
def get_prices(tickers: List[str]) -> Dict[str, Optional[float]]:
    if not isinstance(tickers, list):
        raise TypeError("tickers must be a list")

    results = {}

    for t in tickers:
        results[t] = get_price(t)

    return results


# =========================
# BACKWARD COMPATIBILITY
# =========================
def fetch_nzx_prices(tickers):
    return get_prices(tickers)
