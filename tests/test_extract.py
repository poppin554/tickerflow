from unittest.mock import patch, Mock
from tickerflow.extract import fetch_quote, fetch_quote_with_fallback, RateLimitError
import pytest


def test_fetch_quote_success():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "Global Quote": {"01. symbol": "AMD", "05. price": "494.95"}
    }
    fake_response.raise_for_status = Mock()

    with patch("tickerflow.extract.requests.get", return_value=fake_response):
        result = fetch_quote("AMD", api_key="fake_key_for_testing")

    assert result["01. symbol"] == "AMD"
    assert result["05. price"] == "494.95"


def test_fetch_quote_raises_on_rate_limit():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"Information": "rate limit exceeded"}
    fake_response.raise_for_status = Mock()

    with patch("tickerflow.extract.requests.get", return_value=fake_response):
        with pytest.raises(RateLimitError):
            fetch_quote("AMD", api_key="fake_key_for_testing")


def test_fallback_to_yfinance_on_rate_limit():
    with patch("tickerflow.extract.fetch_quote", side_effect=RateLimitError("rate limit hit")):
        with patch("tickerflow.extract.fetch_quote_yfinance", return_value={"01. symbol": "AMD", "05. price": "500.00"}) as mock_yf:
            result = fetch_quote_with_fallback("AMD", api_key="fake_key")

    mock_yf.assert_called_once_with("AMD")
    assert result["01. symbol"] == "AMD"