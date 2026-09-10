# Tickerflow

> A Dockerized market-data pipeline that fetches equity quotes with provider fallback, stores price data in PostgreSQL, and calculates portfolio profit and loss.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-data-336791)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)

Tickerflow demonstrates a practical data-engineering workflow for financial data:

- Fetch live equity quotes from Alpha Vantage
- Fall back to `yfinance` when the primary provider is rate-limited or unavailable
- Save raw data to Parquet
- Load quote history into PostgreSQL
- Join quotes with holdings to calculate near-real-time P&L
- Schedule the workflow with Airflow

> This project is for education and portfolio tracking only. It does not execute trades or provide investment advice.

## Architecture

```mermaid
graph LR
    A[Alpha Vantage] --> E[Extract]
    Y[yfinance<br/>fallback] --> E
    E --> P[Parquet<br/>landing zone]
    P --> D[(PostgreSQL)]
    D --> R[P&L report]
    S[Airflow<br/>scheduler] -.triggers.-> E
```

# Quick Start
Prerequisites
- Docker Desktop
- [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key)

## Run
```
git clone https://github.com/poppin554/tickerflow.git
cd tickerflow

cp .env.example .env
```

### Add Alpha Vantage key to .env
```
MARKET_API_KEY=your_key_here
```

### Start the pipeline and database
```
docker compose up --build
```

### On a successful run, Tickerflow will
- Fetch quotes for AMD, AAPL and MSFT
- Save raw quotes into parquet files
- Load quote records into PostgreSQL
- Print a portfolio PnL table to the console

## What happens when provider (AlphaVantage) fails
- If API key limits are reached with AlphaVantage, Tickerflow will fallback to yfinance for financial data.
- This makes the pipeline more resilient, whilst keeping provider failures visible in logs

# Project Structure
```
tickerflow/
├── airflow/                 # Airflow DAG and container setup
├── db/
│   └── init.sql             # PostgreSQL schema initialization
├── scripts/
│   ├── run_pipeline.py      # Pipeline entry point
│   └── manual_load_check.py # Load mock data for local checks
├── src/tickerflow/
│   ├── extract.py           # Quote fetching and Parquet output
│   ├── load.py              # PostgreSQL loading
│   ├── transform.py         # P&L transformation logic
│   └── config.py            # Environment configuration
├── tests/                   # Mocked extraction tests
├── docker-compose.yml
└── README.md
```

## Verify the data
- PostgreSQL database is exposed locally on port ```5432```
- The ```raw_quotes``` fetched by the designated API key can be found on psql or DBeaver. A successful pipeline run creates recent rows with a ```fetched_at``` timestamp

## Testing
- Tests run against mocked provider responses to validate pipeline logic without consuming API quota
```
pip install -r requirements.txt
pytest tests/ -v
```
## Current Capabilities
- ✅ Market quote extraction
- ✅ Primary-provider and fallback-provider logic
- ✅ Parquet landing zone
- ✅ PostgreSQL loading
- ✅ Portfolio P&L query
- ✅ Dockerized local environment
- ✅ Airflow orchestration
- ✅ Automated tests and CI

## Roadmap
- Show portfolio holdings through an application interface
- Historical portfolio performance
- Data-freshness and provider health-checks
- Support for additional market-data sources and user-configurable symbols
- Cloud deployment

## Limitations
- Alpha Vantage's free tier API key has request limits
- ```yfinance``` is an unofficial source and may change without notice
- Current pipeline only runs a fixed symbol
- Tickerflow currently reports PnL only in console, planned web dashboard interface.

## Design Decisions
> Choices that were made during the process of building tickerflow
**Why land raw data in Parquet before loading to Postgres?**
- Extraction and loading are decoupled on purpose. If the DB load step fails, the raw fetch isn't lost — it's already on disk in a typed, columnar format. This also mirrors a common real-world pattern (raw landing zone → warehouse) rather than writing straight from the API response into a database table.

**Why fall back to yfinance instead of just retrying Alpha Vantage?**
- Alpha Vantage's free tier cap (25 requests/day) is a hard limit, not a transient error — retrying with backoff wouldn't help. A second provider keeps the pipeline running end-to-end instead of failing outright, while the fallback event is still logged so the failure stays visible rather than silent.

**Why compute P&L in SQL instead of pandas?**
- The join between `raw_quotes` and `holdings` happens where the data already lives, instead of pulling both tables into memory to merge in Python. It also keeps the transformation logic testable and inspectable as a standalone query, independent of the extraction code.

**Why Airflow instead of a cron job or a simple scheduler loop?**
- The pipeline needed per-symbol task isolation (one symbol failing shouldn't block the others), explicit data handoff between tasks (XCom), and a `TriggerRule.ALL_DONE` PnL report that runs regardless of individual task outcomes. A cron job can't express that dependency graph or give per-task retry/observability — Airflow is the tool actually used for this in production DE work.

**Why Docker Compose instead of a single container?**
- Postgres and the pipeline are separate services with independent lifecycles (the DB should persist and start before the pipeline runs against it). Compose also matches how these are architected in practice, rather than bundling everything into one image.
