import os
import requests

API_KEY = os.getenv("NZXPLORER_API_KEY")

BASE_URL = "https://api.nzxplorer.com/v1"


def debug_request(path: str, method="GET", params=None, json=None):
    url = f"{BASE_URL}{path}"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    print("\n==============================")
    print("NZXplorer DEBUG CALL")
    print("URL:", url)
    print("METHOD:", method)
    print("PARAMS:", params)
    print("JSON:", json)

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=15)
        else:
            resp = requests.post(url, headers=headers, json=json, timeout=15)

        print("STATUS:", resp.status_code)
        print("RESPONSE HEADERS:", dict(resp.headers))
        print("RESPONSE BODY (trimmed):")
        print(resp.text[:1000])
        print("==============================\n")

        return resp

    except Exception as e:
        print("REQUEST FAILED:", str(e))
        return None


def test_endpoints(tickers):
    """
    Try multiple likely NZXplorer patterns and print everything.
    """

    print("\n🚀 STARTING NZXPLORER DIAGNOSTIC TEST\n")

    # Test 1: base quotes endpoint (GET)
    debug_request("/quotes", method="GET", params={"symbols": ",".join(tickers)})

    # Test 2: prices endpoint (GET)
    debug_request("/prices", method="GET", params={"symbols": ",".join(tickers)})

    # Test 3: market quotes (GET)
    debug_request("/market/quotes", method="GET", params={"symbols": ",".join(tickers)})

    # Test 4: POST variant
    debug_request("/quotes", method="POST", json={"symbols": tickers})

    print("\n🚀 END DIAGNOSTIC\n")
