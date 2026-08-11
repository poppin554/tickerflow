FROM apache/airflow:3.0.0

COPY requirements.txt /requirements.txt
RUN grep -v "^yfinance" /requirements.txt > /tmp/requirements-no-yfinance.txt && \
    pip install --no-cache-dir -r /tmp/requirements-no-yfinance.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.0/constraints-3.12.txt"

RUN pip install --no-cache-dir yfinance==1.5.2