1. Ingest live price of Fortune 100 companies (AMD, AAPL, MSFT) using API from alpha vantage, api key here (https://www.alphavantage.co/support/#api-key)
2. Fetch live price using run_pipeline.py (change ticker as needed)
3. Create tables from psql of the stock price vs portfolio holding. 
4. Returned parquet file to load into postgres sql. 
4.