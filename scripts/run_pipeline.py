import logging
from tickerflow.config import load_settings
from tickerflow.extract import fetch_quote

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()]
)

def main():
    settings = load_settings()
    quote = fetch_quote(symbol="AMD", api_key=settings.api_key)
    print(quote)

if __name__ == "__main__":
    main()