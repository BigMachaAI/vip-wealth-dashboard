from __future__ import annotations

from datetime import date
from pathlib import Path
import json

import pandas as pd

from portfolio import DATA_DIR, load_portfolio
from services.calculations import build_portfolio_summary
from services.nzx_prices import fetch_nzx_prices


HISTORY_PATH = DATA_DIR / "history.csv"

HISTORY_COLUMNS = [
    "date",
    "total_portfolio_value",
    "dividend_income",
    "after_tax_income",
]


def load_history(path: Path = HISTORY_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    df = pd.read_csv(path)

    for col in HISTORY_COLUMNS:
        if col not in df.columns:
            df[col] = None

    return df[HISTORY_COLUMNS]


def debug_portfolio_flow():
    """
    FULL TRACE: portfolio → prices → summary
    """

    print("\n==============================")
    print("🔍 SNAPSHOT DEBUG MODE START")
    print("==============================\n")

    # 1. Load portfolio
    portfolio = load_portfolio()
    print("📦 RAW PORTFOLIO:")
    print(portfolio)

    # 2. Extract tickers (best effort)
    try:
        tickers = list(portfolio["ticker"].unique())
    except Exception as e:
        print("❌ Failed to extract tickers:", e)
        tickers = []

    print("\n📊 TICKERS:")
    print(tickers)

    # 3. DIRECT PRICE TEST (bypass everything)
    print("\n💰 DIRECT NZX PRICE TEST:")
    prices = fetch_nzx_prices(tickers)
    print(json.dumps(prices, indent=2))

    zero_count = sum(1 for v in prices.values() if v == 0)
    print(f"\n⚠️ Zero prices: {zero_count} / {len(prices)}")

    # 4. Build full summary (your real pipeline)
    print("\n🧮 BUILDING SUMMARY:")
    summary = build_portfolio_summary(portfolio)

    print(json.dumps(summary, indent=2))

    # 5. Diagnose failure point
    total_value = summary.get("total_portfolio_value")

    print("\n📉 FINAL CHECK:")
    print("Total portfolio value:", total_value)

    if not total_value or total_value <= 0:
        print("\n❌ FAILURE DETECTED: Portfolio value is zero or invalid")
        print("👉 This is NOT a snapshot problem")
        print("👉 This is upstream pricing or calculations issue")

    print("\n==============================")
    print("🔍 SNAPSHOT DEBUG MODE END")
    print("==============================\n")

    return summary


def save_daily_snapshot(path: Path = HISTORY_PATH) -> pd.DataFrame:
    """
    IMPORTANT:
    In debug mode we still write history, but we DO NOT block execution.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    summary = debug_portfolio_flow()

    history = load_history(path)
    today = date.today().isoformat()

    new_row = {
        "date": today,
        "total_portfolio_value": round(summary.get("total_portfolio_value", 0) or 0, 2),
        "dividend_income": round(summary.get("annual_dividend_income", 0) or 0, 2),
        "after_tax_income": round(summary.get("after_tax_dividend_income", 0) or 0, 2),
    }

    if not history.empty:
        history = history[history["date"].astype(str) != today]

    updated = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)
    updated = updated.sort_values("date")

    updated.to_csv(path, index=False)

    return updated


if __name__ == "__main__":
    updated_history = save_daily_snapshot()
    latest = updated_history.iloc[-1].to_dict()

    print("\n📊 SNAPSHOT SAVED (DEBUG MODE)")
    print(f"Date: {latest['date']}")
    print(f"Portfolio value: ${latest['total_portfolio_value']:,.2f}")
    print(f"After-tax income: ${latest['after_tax_income']:,.2f}")
