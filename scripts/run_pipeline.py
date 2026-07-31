import logging
from tickerflow.config import load_settings
from tickerflow.extract import fetch_quote
from tickerflow.extract import fetchquotes
from tickerflow.extract import save_to_parquet
from tickerflow.load import load_to_postgres
from tickerflow.transform import get_pnl_report

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()]
)

def main():
    settings = load_settings()
    quotes = fetchquotes(symbols=["AMD","AAPL","MSFT"],api_key=settings.api_key)
    if not quotes:
        logger.error("No quotes fetched — aborting pipeline, nothing to save or load")
        return
    filepath = save_to_parquet(quotes)
    if not filepath:
        logger.error("Parquet save failed — aborting before database load")
        return
    load_to_postgres(filepath,settings.db_url)
    pnl_df = get_pnl_report(settings.db_url)
    print(pnl_df)
    print(f"Saved {len(quotes)} quotes to {filepath}")

if __name__ == "__main__":
    main()