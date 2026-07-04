import os
import requests

API_KEY = os.getenv("NZXPLORER_API_KEY")

BASE_URL = "https://nzxplorer.co.nz/api/v1"


def fetch_price(ticker: str) -> float:
    """
    Single ticker price fetch (reliable endpoint based on docs)
    """

    if not API_KEY:
        print("[NZXplorer] Missing API key")
        return 0.0

    url = f"{BASE_URL}/prices/{ticker}"

    headers = {
        "X-API-Key": API_KEY
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code != 200:
            print(f"[NZXplorer] Error {resp.status_code} for {ticker}")
            return 0.0

        data = resp.json()

        # supports both standard + LLM format
        if isinstance(data, dict):
            if "price" in data:
                return float(data["price"])
            if "data" in data and "price" in data["data"]:
                return float(data["data"]["price"])

        return 0.0

    except Exception as e:
        print("[NZXplorer ERROR]", ticker, str(e))
        return 0.0


def fetch_bulk_quotes(tickers: list[str]) -> dict[str, float]:
    """
    Safe pseudo-bulk (API does not clearly guarantee bulk endpoint in docs)
    """

    results = {}

    for t in tickers:
        results[t] = fetch_price(t)

    return results
