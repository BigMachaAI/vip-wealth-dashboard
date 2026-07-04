import os
import requests

API_KEY = os.getenv("NZXPLORER_API_KEY")
BASE_URL = "https://api.nzxplorer.com/v1"


def fetch_bulk_quotes(tickers: list[str]) -> dict[str, float]:
    if not API_KEY:
        return {}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    endpoints = [
        f"{BASE_URL}/quotes",
        f"{BASE_URL}/prices",
        f"{BASE_URL}/market/quotes",
    ]

    for url in endpoints:
        try:
            resp = requests.post(
                url,
                json={"symbols": tickers},
                headers=headers,
                timeout=10,
            )

            if resp.status_code != 200:
                continue

            data = resp.json()

            prices = {}

            for item in data.get("data", data):
                symbol = item.get("symbol") or item.get("ticker")
                price = item.get("last_price") or item.get("price")

                if symbol and price:
                    prices[symbol.upper()] = float(price)

            if prices:
                return prices

        except Exception:
            continue

    return {}
