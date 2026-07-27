import logging
import requests
from time import sleep

logger = logging.getLogger(__name__)

def fetch_quote(symbol: str, api_key: str, max_retries: int = 3) -> dict:
    url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # raises on 4xx/5xx
            data = response.json()

            if "Global Quote" not in data:
                # API returned 200 but no real data — e.g. bad symbol or rate limit note
                logger.warning(f"No quote data for {symbol}: {data}")
                return {}

            logger.info(f"Fetched quote for {symbol}")
            return data["Global Quote"]

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {symbol}, attempt {attempt}/{max_retries}")
            sleep(2 ** attempt)  # exponential backoff: 2s, 4s, 8s
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {symbol}: {e}")
            break  # don't retry on non-timeout errors (e.g. 401 auth failure)

    logger.error(f"Failed to fetch {symbol} after {max_retries} attempts")
    return {}