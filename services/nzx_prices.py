from __future__ import annotations

import contextlib
import io
import logging
import pandas as pd
import yfinance as yf

from .nzxplorer_client import fetch_bulk_quotes

logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def to_yfinance_ticker(ticker: str) -> str:
    clean = str(ticker).upper().strip()
    return clean if clean.endswith(".NZ") else f"{clean}.NZ"


def fetch_yahoo_price(ticker: str) -> float:
    try:
        yf_ticker = yf.Ticker(to_yfinance_ticker(ticker))

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            hist = yf_ticker.history(period="1mo", interval="1d")

        if hist.empty or "Close" not in hist:
            return 0.0

        return float(hist["Close"].dropna().iloc[-1])

    except Exception:
        return 0.0


def fetch_nzx_prices(tickers: list[str]) -> dict[str, float]:
    clean = list(dict.fromkeys(t.upper().strip() for t in tickers if t))
    prices = {t: 0.0 for t in clean}

    # 🥇 NZXplorer primary
    try:
        nzx_data = fetch_bulk_quotes(clean)

        for k, v in nzx_data.items():
            if k in prices:
                prices[k] = v
    except Exception:
        nzx_data = {}

    # 🥈 Yahoo fallback
    missing = [t for t, v in prices.items() if v == 0.0]

    for t in missing:
        prices[t] = fetch_yahoo_price(t)

    return prices
