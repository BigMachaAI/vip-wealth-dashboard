import os
import requests

API_KEY = os.getenv("NZXPLORER_API_KEY")

BASE_URL = "https://api.nzxplorer.com/v1"


def fetch_bulk_quotes(tickers: list[str]) -> dict[str, float]:
    """
    Safe stub implementation until we confirm real NZXplorer API format.
    This prevents import crashes and restores pipeline stability.
    """

    if not API_KEY:
        print("[NZXplorer] Missing API key")
        return {}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    # NOTE: we intentionally try a simple GET first for debugging stability
    try:
        resp = requests.get(
            f"{BASE_URL}/quotes",
            params={"symbols": ",".join(tickers)},
            headers=headers,
            timeout=10,
        )

        print("[NZXplorer DEBUG] status:", resp.status_code)
        print("[NZXplorer DEBUG] body:", resp.text[:500])

        if resp.status_code != 200:
            return {}

        data = resp.json()

        prices = {}

        for item in data.get("data", data):
            symbol = item.get("symbol") or item.get("ticker")
            price = item.get("last_price") or item.get("price")

            if symbol and price:
                prices[symbol.upper()] = float(price)

        return prices

    except Exception as e:
        print("[NZXplorer ERROR]", str(e))
        return {}
