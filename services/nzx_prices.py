from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf


logging.getLogger("yfinance").setLevel(logging.CRITICAL)


def to_yfinance_ticker(ticker: str) -> str:
    """Convert an NZX ticker such as CNU to Yahoo Finance format CNU.NZ."""
    clean_ticker = str(ticker).upper().strip()
    if clean_ticker.endswith(".NZ"):
        return clean_ticker
    return f"{clean_ticker}.NZ"


def fetch_nzx_price(ticker: str) -> float:
    """Fetch the latest available NZX close price. Return 0.0 if anything fails."""
    yahoo_ticker = to_yfinance_ticker(ticker)

    try:
        history = yf.Ticker(yahoo_ticker).history(period="5d", interval="1d", auto_adjust=False)
    except Exception:
        return 0.0

    if history.empty or "Close" not in history:
        return 0.0

    close_prices = history["Close"].dropna()
    if close_prices.empty:
        return 0.0

    price = close_prices.iloc[-1]
    if pd.isna(price):
        return 0.0

    return float(price)


def fetch_nzx_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch prices one ticker at a time so one failed stock cannot break the app."""
    prices: dict[str, float] = {}
    for ticker in tickers:
        clean_ticker = str(ticker).upper().strip()
        prices[clean_ticker] = fetch_nzx_price(clean_ticker)
    return prices
