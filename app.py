from __future__ import annotations

import streamlit as st

from portfolio import load_portfolio
from services.calculations import build_portfolio_summary
from services.snapshot import HISTORY_PATH, load_history


st.set_page_config(page_title="VIP Wealth Dashboard", layout="wide")

st.title("VIP Wealth Dashboard")
st.caption("NZX portfolio value, estimated dividends, and passive income progress.")

portfolio = load_portfolio()
summary = build_portfolio_summary(portfolio)
history = load_history(HISTORY_PATH)

total_value = summary["total_portfolio_value"]
annual_dividends = summary["annual_dividend_income"]
after_tax_income = summary["after_tax_dividend_income"]
fire_target = summary["fire_target_after_tax_income"]
fire_progress = summary["fire_progress_percent"]
holdings = summary["holdings"]

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Portfolio Value", f"${total_value:,.2f}")
metric_2.metric("Annual Dividends", f"${annual_dividends:,.2f}")
metric_3.metric("After-Tax Income", f"${after_tax_income:,.2f}")

st.subheader("Passive Income Goal")
st.progress(min(fire_progress / 100, 1.0))
st.write(f"{fire_progress:.1f}% of the ${fire_target:,.0f} after-tax income goal")

st.subheader("Holdings")
display_holdings = holdings.copy()
display_holdings = display_holdings.rename(
    columns={
        "ticker": "Ticker",
        "shares": "Shares",
        "price": "Price",
        "value": "Value",
        "dividend_yield": "Dividend Yield",
        "annual_dividend_income": "Annual Dividends",
        "after_tax_dividend_income": "After-Tax Dividends",
    }
)
st.dataframe(
    display_holdings,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Shares": st.column_config.NumberColumn(format="%d"),
        "Price": st.column_config.NumberColumn(format="$%.3f"),
        "Value": st.column_config.NumberColumn(format="$%.2f"),
        "Dividend Yield": st.column_config.NumberColumn(format="%.2f%%"),
        "Annual Dividends": st.column_config.NumberColumn(format="$%.2f"),
        "After-Tax Dividends": st.column_config.NumberColumn(format="$%.2f"),
    },
)

st.subheader("Portfolio Value History")
if history.empty:
    st.info("No history yet. Run the daily snapshot once to create the first data point.")
else:
    chart_data = history[["date", "total_portfolio_value"]].copy()
    chart_data["date"] = chart_data["date"].astype(str)
    chart_data = chart_data.set_index("date")
    st.line_chart(chart_data)

with st.expander("Important note"):
    st.write(
        "This dashboard is a simple tracking tool, not personalised financial advice. "
        "Prices come from Yahoo Finance via yFinance and dividend yields are editable estimates."
    )
