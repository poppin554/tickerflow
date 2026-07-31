import logging
import requests
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
import yfinance as yf

logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    pass

def fetch_quote_yfinance(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info  # lighter-weight than .info, fewer fields but faster

        if not info or info.get("lastPrice") is None:
            logger.warning(f"No quote data for {symbol} from yfinance")
            return {}

        logger.info(f"Fetched quote for {symbol} (yfinance)")
        return {
            "01. symbol": symbol,
            "05. price": str(info["lastPrice"]),
            "06. volume": str(info.get("lastVolume", 0)),
            "symbol_requested": symbol,
        }
    except Exception as e:
        logger.error(f"yfinance fetch failed for {symbol}: {e}")
        return {}

def fetch_quote(symbol: str, api_key: str, max_retries: int = 3): #Only ONE ticker
    url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key}

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() 
            data = response.json()

            if "Information" in data and "rate limit" in data["Information"].lower():
                raise RateLimitError(data["Information"])

            if "Global Quote" not in data:
                logger.warning(f"No quote data for {symbol}: {data}")
                return {} #Returning nothing here because I dont want invalid records entering my pipeline. 
            #Maybe can return None

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

def fetchquotes(symbols: list[str], api_key: str): #Multiple tickers
    results = []
    for symbol in symbols:
        quote = fetch_quote_with_fallback(symbol, api_key)
        if quote:
            quote["symbol_requested"] = symbol
            quote["fetched_at"] = datetime.now(timezone.utc).isoformat()
            results.append(quote)
        sleep(12) #5 req/min, 60/5 = 12
    return results

def fetch_quote_with_fallback(symbol: str, api_key: str) -> dict:
    try:
        quote = fetch_quote(symbol, api_key)
        if quote:
            return quote
        return {}  # genuine failure, not rate-limit — don't fall back, just fail
    except RateLimitError:
        logger.warning(f"Alpha Vantage rate-limited — falling back to yfinance for {symbol}")
        return fetch_quote_yfinance(symbol)

def save_to_parquet(quotes: list[dict], output_dir: str = "data/raw"):
    if not quotes:
        logger.warning("No quotes to save, skipping Parquet write")
        return ""
    df = pd.DataFrame(quotes)
    Path(output_dir).mkdir(parents=True, exist_ok = True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filepath = f"{output_dir}/quotes_{timestamp}.parquet"
    df.to_parquet(path= filepath, index=False)
    logger.info(f"Saved {len(quotes)} quotes to {filepath}")
    return filepath