import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    api_key: str
    db_host: str = 'localhost'
    db_port: int = 5432

def load_settings() -> Settings:
    return Settings(
        api_key=os.environ["MARKET_API_KEY"],  # crashes loudly if missing — good
        db_host=os.environ.get("DB_HOST", "localhost"),
    )
