import logging
import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__) #module level logger so logs identify which module generated what.

def load_to_postgres(filepath: str, db_url: str, table_name: str="raw_quotes"):
    df = pd.read_parquet(filepath)
    df_clean = pd.DataFrame({
        "symbol": df["symbol_requested"],
        "price": df["05. price"].astype(float),
        "volume": df["06. volume"].astype(int),
        "fetched_at": pd.to_datetime(df["fetched_at"]),
    })


    engine = create_engine(db_url)
    try:
        df_clean.to_sql(table_name, engine, if_exists="append", index=False)
        logger.info(f"Loaded {len(df_clean)} rows into {table_name}")
        return len(df_clean)
    except Exception as error:
        logger.exception(f"Failed to load {filepath} into {table_name}")
        raise
    finally:
        engine.dispose()