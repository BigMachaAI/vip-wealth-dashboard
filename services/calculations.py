# services/calculations.py

from services.nzx_prices import fetch_nzx_prices


def build_portfolio_summary(holdings):
    """
    holdings: DataFrame with columns:
        - ticker
        - shares
    """

    tickers = holdings["ticker"].tolist()

    # ✅ ALWAYS batch fetch prices
    prices = fetch_nzx_prices(tickers)

    total_value = 0
    results = []

    for _, row in holdings.iterrows():
        ticker = row["ticker"]
        shares = row["shares"]

        price = prices.get(ticker)

        if price is None:
            print(f"[WARN] Missing price for {ticker}")
            continue

        value = shares * price
        total_value += value

        results.append({
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "value": value
        })

    return {
        "total_value": total_value,
        "holdings": results,
        "missing_count": len(tickers) - len(results)
    }
