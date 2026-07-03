from __future__ import annotations


# Estimated gross cash dividend yields for the MVP.
# Edit these numbers when you want to update assumptions.
# Example: 0.055 means 5.5% annual dividend yield.
DIVIDEND_YIELDS = {
    "CNU": 0.055,
    "EBO": 0.035,
    "HLG": 0.075,
    "MCY": 0.070,
    "MFT": 0.035,
    "SKC": 0.020,
    "WHS": 0.030,
    "AIA": 0.025,
    "ATM": 0.000,
    "CEN": 0.055,
    "KMD": 0.000,
    "FPH": 0.015,
    "SPK": 0.070,
    "RYM": 0.000,
    "SUM": 0.020,
}

EFFECTIVE_DIVIDEND_TAX_RATE = 0.15
IMPUTATION_BENEFIT_NOTE = "Simplified MVP model assumes imputation benefit and 15% effective total tax."


def get_dividend_yield(ticker: str) -> float:
    return DIVIDEND_YIELDS.get(str(ticker).upper().strip(), 0.0)


def estimate_annual_dividend(value: float, dividend_yield: float) -> float:
    return float(value) * float(dividend_yield)


def estimate_after_tax_dividend(dividend_income: float) -> float:
    return float(dividend_income) * (1 - EFFECTIVE_DIVIDEND_TAX_RATE)
