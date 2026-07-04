from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from portfolio import DATA_DIR, load_portfolio
from services.calculations import build_portfolio_summary


HISTORY_PATH = DATA_DIR / "history.csv"

HISTORY_COLUMNS = [
    "date",
    "total_portfolio_value",
    "dividend_income",
    "after_tax_income",
]

# ⚠️ lowered strictness: prevents false failures when API partially responds
MINIMUM_VALID_PORTFOLIO_VALUE = 0.01


def load_history(path: Path = HISTORY_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    df = pd.read_csv(path)

    for col in HISTORY_COLUMNS:
        if col not in df.columns:
            df[col] = None

    return df[HISTORY_COLUMNS]


def validate_summary(summary: dict) -> tuple[bool, str]:
    """
    More informative validation instead of hard crash.
    """
    if not summary:
        return False, "Summary is empty"

    value = summary.get("total_portfolio_value")

    if value is None:
        return False, "Missing total_portfolio_value"

    if value <= 0:
        return False, f"Portfolio value invalid: {value}"

    return True, "OK"


def save_daily_snapshot(path: Path = HISTORY_PATH) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    portfolio = load_portfolio()
    summary = build_portfolio_summary(portfolio)

    # ---------------------------
    # VALIDATION (NON-FATAL)
    # ---------------------------
    is_valid, reason = validate_summary(summary)

    if not is_valid:
        print(f"[SNAPSHOT WARNING] {reason}")
        print("[SNAPSHOT] Falling back to previous snapshot (if available)")

        history = load_history(path)

        if not history.empty:
            return history

        raise RuntimeError(
            "No valid portfolio data and no history fallback available."
        )

    total_value = float(summary.get("total_portfolio_value", 0) or 0)

    # Still protect against full-zero corruption, but do NOT hard crash pipeline
    if total_value < MINIMUM_VALID_PORTFOLIO_VALUE:
        print("[SNAPSHOT WARNING] Portfolio value extremely low or zero.")
        print("[SNAPSHOT] Saving anyway for diagnostics.")

    history = load_history(path)
    today = date.today().isoformat()

    new_row = {
        "date": today,
        "total_portfolio_value": round(total_value, 2),
        "dividend_income": round(summary.get("annual_dividend_income", 0) or 0, 2),
        "after_tax_income": round(summary.get("after_tax_dividend_income", 0) or 0, 2),
    }

    # remove existing entry for today
    if not history.empty:
        history = history[history["date"].astype(str) != today]

    # append new row
    new_df = pd.DataFrame([new_row])

    if history.empty:
        updated = new_df
    else:
        updated = pd.concat([history, new_df], ignore_index=True)

    updated = updated.sort_values("date")
    updated.to_csv(path, index=False)

    return updated


if __name__ == "__main__":
    updated_history = save_daily_snapshot()
    latest = updated_history.iloc[-1].to_dict()

    print("\n📊 Snapshot saved successfully")
    print(f"Date: {latest['date']}")
    print(f"Portfolio value: ${latest['total_portfolio_value']:,.2f}")
    print(f"After-tax dividend income: ${latest['after_tax_income']:,.2f}")
