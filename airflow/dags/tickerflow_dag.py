import logging
from datetime import datetime, timezone
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from tickerflow.extract import fetch_quote_with_fallback, save_to_parquet
from tickerflow.load import load_to_postgres
from tickerflow.transform import get_pnl_report
from tickerflow.config import load_settings
logger = logging.getLogger(__name__)
SYMBOLS = ["AAPL", "MSFT", "AMD"]
settings = load_settings()

def fetch_and_save(symbol, api_key):
    quote = fetch_quote_with_fallback(symbol, api_key)
    if not quote:
        return None  # genuine failure — nothing to save, XCom gets None
    quote["symbol_requested"] = symbol
    quote["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return save_to_parquet([quote])

def load_to_postgres_wrapper(**context):
    task_ids =[f"fetch_quote_{s}" for s in SYMBOLS]
    paths = context["ti"].xcom_pull(task_ids=task_ids)
    paths = [p for p in paths if p is not None]
    if not paths:
        logger.info("No files to load, skipping.")
        return

    for path in paths:
        load_to_postgres(path, settings.db_url)
    

with DAG(
    dag_id="tickerflow_dag",
    start_date=datetime(2026, 8, 7),
    schedule="0 */6 * * *",
    catchup=False,
) as dag:

    fetch_tasks = []
    for symbol in SYMBOLS:
        t = PythonOperator(
            task_id=f"fetch_quote_{symbol}",
            python_callable=fetch_and_save,
            op_kwargs={"symbol": symbol, "api_key": settings.api_key},  
        )
        fetch_tasks.append(t)

    postgres = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres_wrapper,
        trigger_rule=TriggerRule.ALL_DONE, 
    )

    transform = PythonOperator(
        task_id="get_pnl_report",
        python_callable=get_pnl_report,
        op_kwargs={"db_url": settings.db_url},
    )

    fetch_tasks >> postgres >> transform 