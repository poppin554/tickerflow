import logging
import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

def get_pnl_report(db_url: str):
    #Core functions
    engine = create_engine(db_url)
    query = """WITH latest_quotes AS (
    SELECT symbol, price, fetched_at,
           ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY fetched_at DESC) AS rn
    FROM raw_quotes
    )
    SELECT
        h.symbol,
        h.quantity,
        h.avg_cost,
        lq.price AS current_price,
        lq.fetched_at AS price_as_of,
        (lq.price - h.avg_cost) * h.quantity AS unrealized_pnl,
        ROUND(((lq.price - h.avg_cost) / h.avg_cost) * 100, 2) AS pnl_percent
    FROM holdings h
    JOIN latest_quotes lq ON lq.symbol = h.symbol AND lq.rn = 1
    ORDER BY unrealized_pnl DESC;"""
    #End of core function
    try:
        pnl_df = pd.read_sql(query,engine)
        logger.info(f"{len(pnl_df)} generated in PnL report.")
        return pnl_df
    except Exception as error:
        logger.exception(f"Failed to generate PnL report") 
        #instead of logger.error because logger exception includes traceback .
        raise
    finally:
        engine.dispose()


