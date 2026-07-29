# scripts/test_load_manual.py
import logging
from tickerflow.config import load_settings
from tickerflow.extract import save_to_parquet
from tickerflow.load import load_to_postgres

logging.basicConfig(level=logging.INFO)

fake_quotes = [
    {
        "01. symbol": "AMD", "05. price": "494.9500", "06. volume": "31800253",
        "symbol_requested": "AMD", "fetched_at": "2026-07-29T10:00:00+00:00",
    },
    {
        "01. symbol": "AAPL", "05. price": "336.9100", "06. volume": "49604297",
        "symbol_requested": "AAPL", "fetched_at": "2026-07-29T10:00:00+00:00",
    },
]

settings = load_settings()
filepath = save_to_parquet(fake_quotes)
load_to_postgres(filepath, settings.db_url)
print(f"Loaded fake data via {filepath}")