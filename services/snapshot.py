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
MINIMUM_VALID_PORTFOLIO_VALUE = 1.0


def load_history(path: Path = HISTORY_PATH) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    history = pd.read_csv(path)
    for column in HISTORY_COLUMNS:
        if column not in history.columns:
            history[column] = None
    return history[HISTORY_COLUMNS]


def save_daily_snapshot(path: Path = HISTORY_PATH) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    portfolio = load_portfolio()
    summary = build_portfolio_summary(portfolio)
    if summary["total_portfolio_value"] < MINIMUM_VALID_PORTFOLIO_VALUE:
        raise RuntimeError(
            "No live prices were fetched. Refusing to save an all-zero portfolio snapshot."
        )

    history = load_history(path)
    today = date.today().isoformat()

    new_row = {
        "date": today,
        "total_portfolio_value": round(summary["total_portfolio_value"], 2),
        "dividend_income": round(summary["annual_dividend_income"], 2),
        "after_tax_income": round(summary["after_tax_dividend_income"], 2),
    }

    history = history[history["date"].astype(str) != today]
    new_history_row = pd.DataFrame([new_row])
    history = new_history_row if history.empty else pd.concat([history, new_history_row], ignore_index=True)
    history = history.sort_values("date")
    history.to_csv(path, index=False)
    return history


if __name__ == "__main__":
    updated_history = save_daily_snapshot()
    latest = updated_history.iloc[-1].to_dict()
    print(f"Snapshot saved for {latest['date']}")
    print(f"Portfolio value: ${latest['total_portfolio_value']:,.2f}")
    print(f"After-tax dividend income: ${latest['after_tax_income']:,.2f}")
