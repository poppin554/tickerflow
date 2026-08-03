CREATE TABLE holdings(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    quantity NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    avg_cost NUMERIC(12,4) NOT NULL DEFAULT 0.0000
);

CREATE TABLE raw_quotes(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price NUMERIC(12,4) NOT NULL DEFAULT 0.0000,
    volume INT NOT NULL DEFAULT 0.0000,
    fetched_at TIMESTAMP
);

INSERT INTO holdings (symbol, quantity, avg_cost) VALUES ('AMD', 23.7, 465.93);
INSERT INTO holdings (symbol, quantity, avg_cost) VALUES ('AAPL', 15, 320.00);
INSERT INTO holdings (symbol, quantity, avg_cost) VALUES ('MSFT', 30, 390.54);