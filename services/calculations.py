from __future__ import annotations

import pandas as pd

from services.dividends import (
    estimate_after_tax_dividend,
    estimate_annual_dividend,
    get_dividend_yield,
)
from services.nzx_prices import fetch_nzx_prices


FIRE_TARGET_AFTER_TAX_INCOME = 50_000.0


def build_portfolio_summary(portfolio: pd.DataFrame) -> dict:
    """Build holdings, valuation, dividends, and FIRE progress from a portfolio."""
    holdings = portfolio.copy()
    prices = fetch_nzx_prices(holdings["ticker"].tolist())

    holdings["price"] = holdings["ticker"].map(prices).fillna(0.0)
    holdings["value"] = holdings["shares"] * holdings["price"]
    holdings["dividend_yield"] = holdings["ticker"].apply(get_dividend_yield)
    holdings["annual_dividend_income"] = holdings.apply(
        lambda row: estimate_annual_dividend(row["value"], row["dividend_yield"]),
        axis=1,
    )
    holdings["after_tax_dividend_income"] = holdings["annual_dividend_income"].apply(
        estimate_after_tax_dividend
    )
    holdings["dividend_yield"] = holdings["dividend_yield"] * 100

    total_value = float(holdings["value"].sum())
    dividend_income = float(holdings["annual_dividend_income"].sum())
    after_tax_income = float(holdings["after_tax_dividend_income"].sum())
    fire_progress = (
        after_tax_income / FIRE_TARGET_AFTER_TAX_INCOME * 100
        if FIRE_TARGET_AFTER_TAX_INCOME
        else 0.0
    )

    return {
        "holdings": holdings,
        "total_portfolio_value": total_value,
        "annual_dividend_income": dividend_income,
        "after_tax_dividend_income": after_tax_income,
        "fire_target_after_tax_income": FIRE_TARGET_AFTER_TAX_INCOME,
        "fire_progress_percent": fire_progress,
    }
