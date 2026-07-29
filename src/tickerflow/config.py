import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    api_key: str
    db_host: str = 'localhost'
    db_port: int = 5432
    db_name: str = 'tickerflow'
    db_user: str = 'postgres'
    db_password: str = ''

    @property

    def db_url(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

def load_settings():
    return Settings(
        api_key=os.environ["MARKET_API_KEY"],  # crashes loudly if missing — good
        db_host=os.environ.get("DB_HOST", "localhost"),
        db_password=os.environ.get("DB_PASSWORD",""))