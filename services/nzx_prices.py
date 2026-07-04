from __future__ import annotations

import contextlib
import io
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


def _latest_close(close_prices: pd.Series) -> float:
    close_prices = close_prices.dropna()
    if close_prices.empty:
        return 0.0

    price = close_prices.iloc[-1]
    if pd.isna(price):
        return 0.0

    return float(price)


def fetch_nzx_price(ticker: str) -> float:
    """Fetch the latest available NZX close price. Return 0.0 if anything fails."""
    yahoo_ticker = to_yfinance_ticker(ticker)

    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            history = yf.Ticker(yahoo_ticker).history(
                period="5d",
                interval="1d",
                auto_adjust=False,
                raise_errors=False,
            )
    except Exception:
        return 0.0

    if history.empty or "Close" not in history:
        return 0.0

    return _latest_close(history["Close"])


def fetch_nzx_prices(tickers: list[str]) -> dict[str, float]:
    """Fetch prices in one batch, with per-ticker fallback for resilience."""
    clean_tickers = list(dict.fromkeys(str(ticker).upper().strip() for ticker in tickers))
    prices: dict[str, float] = {ticker: 0.0 for ticker in clean_tickers if ticker}
    yahoo_to_clean = {to_yfinance_ticker(ticker): ticker for ticker in prices}

    if not prices:
        return prices

    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            data = yf.download(
                tickers=list(yahoo_to_clean),
                period="5d",
                interval="1d",
                auto_adjust=False,
                group_by="ticker",
                progress=False,
                threads=False,
                timeout=30,
            )
    except Exception:
        data = pd.DataFrame()

    if not data.empty:
        for yahoo_ticker, clean_ticker in yahoo_to_clean.items():
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    if yahoo_ticker in data.columns.get_level_values(0):
                        prices[clean_ticker] = _latest_close(data[(yahoo_ticker, "Close")])
                elif "Close" in data:
                    prices[clean_ticker] = _latest_close(data["Close"])
            except Exception:
                prices[clean_ticker] = 0.0

    for ticker in tickers:
        clean_ticker = str(ticker).upper().strip()
        if prices.get(clean_ticker, 0.0) == 0.0:
            prices[clean_ticker] = fetch_nzx_price(clean_ticker)
    return prices
