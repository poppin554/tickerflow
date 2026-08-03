#  Tickerflow

Tickerflow is a data engineering project that ingests live stock market data, stores portfolio holdings, and calculates near real-time profit and loss (PnL) metrics. Built with Python, PostgreSQL, and automated data pipelines, the project demonstrates data ingestion, transformation, database management, and analytics workflows.
I built Tickerflow as part of my transition into Data Engineering after completing a Master's in Aerospace Engineering and working as an automotive CAE Engineer.

## Getting Started

### Tech Stack
**Language/Libraries:** Python, pandas, SQLAlchemy, requests, python-dotenv, pytest, yfinance
**Infrastructure:** PostgreSQL, Docker, Docker Compose

### Setup and running it

* Clone the repo
* Copy .env.example to .env and fill in the real values
* For MARKET_API_KEY: 
* Get a free Alpha Vantage API key at https://www.alphavantage.co/support/#api-key (no credit card required) and set it as MARKET_API_KEY in .env.
* run "docker-compose up --build"
* Verify Postgres data: connect via DBeaver or psql to localhost:5432, database `tickerflow`, and check the `raw_quotes` table for rows with a recent `fetched_at` timestamp
* The pipeline's final console output should show a printed PnL table for AMD, AAPL, and MSFT

* Optional: Run DBeaver to browse the PnL easier.
* data/ generated files are .gitignored. 


## Testing
* Tests runs locally (requires a local venv with "pip install -r requirements.txt")
* run : pytest tests/ -v
* Test used mocked API responses, so they run without using API quota. 
* Expected output:
```
collected 3 items                                                                                                         

tests/test_extract.py::test_fetch_quote_success PASSED                                                              [ 33%]
tests/test_extract.py::test_fetch_quote_raises_on_rate_limit PASSED                                                 [ 66%]
tests/test_extract.py::test_fallback_to_yfinance_on_rate_limit PASSED                                               [100%]
```

## Architecture
  ```
  Alpha Vantage (primary) / yfinance (fallback)
          ↓
      extract.py  →  Parquet landing (data/raw/)
          ↓
      load.py  →  Postgres (raw_quotes table)
          ↓
      transform.py  →  SQL PnL query (joins raw_quotes + holdings)
          ↓
      PnL report (printed to console)
  ```

## Project Structure
tickerflow/
├── src/
│   └── tickerflow/
│       ├── __init__.py
│       ├── extract.py        # pulls data from API
│       ├── transform.py      # cleans/reshapes data
│       ├── load.py           # writes to DB/file
│       └── config.py         # loads settings from env/.env
├── db/                       
│   └── init.sql			  # initialises database in new docker container
├── tests/                    
│   ├── test_transform.py	  # placeholder - not implemented
│   └── test_extract.py		  # pulls fake_data to test pipeline (without API costs)
├── scripts/                  
│   ├── run_pipeline.py       # the actual entry point you execute
│   └── manual_load_check.py  # manually load mock data into Postgres without costing API. 
├── .env.example              # documents required env vars, no real secrets
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt          # all required dependencies to run tickerflow
├── README.md
└── pyproject.toml            # or setup.py, marks src/ as installable


## Status / Roadmap
- ✅ Phase 1: Python fundamentals — project structure, venv, config/secrets, error handling & logging, API integration, Parquet
- ✅ Phase 2: ETL pipeline — Postgres load, SQL transformation, Git workflow, mocked testing
- ✅ Phase 3: Docker — containerized pipeline, Docker Compose (Postgres + pipeline services), automated schema init
- ⏳ Phase 4+: Airflow, data warehouse modeling, cloud deployment, Spark

## Known limitations
* yfinance is not an official API and may break. Tickerflow primarily uses alpha vantage, with free tier api capped at 25 req per day. 
* No scheduled runs until Phase 4

