from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"
PORTFOLIO_PATH = DATA_DIR / "portfolio.csv"


def load_portfolio(path: Path = PORTFOLIO_PATH) -> pd.DataFrame:
    """Load the user's portfolio from CSV and normalize basic fields."""
    if not path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {path}")

    portfolio = pd.read_csv(path)
    required_columns = {"ticker", "shares"}
    missing_columns = required_columns - set(portfolio.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Portfolio CSV is missing required columns: {missing}")

    portfolio = portfolio.copy()
    portfolio["ticker"] = portfolio["ticker"].astype(str).str.upper().str.strip()
    portfolio["shares"] = pd.to_numeric(portfolio["shares"], errors="coerce").fillna(0)
    portfolio = portfolio[portfolio["ticker"] != ""]
    return portfolio
