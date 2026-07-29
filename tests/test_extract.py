from unittest.mock import patch, Mock
from tickerflow.extract import fetch_quote

def test_fetch_quote_success():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "Global Quote": {"01. symbol": "AMD", "05. price": "494.95"}
    }
    fake_response.raise_for_status = Mock()  # does nothing, simulating "no error"

    with patch("tickerflow.extract.requests.get", return_value=fake_response):
        result = fetch_quote("AMD", api_key="fake_key_for_testing")

    assert result["01. symbol"] == "AMD"
    assert result["05. price"] == "494.95"

def test_fetch_quote_handles_rate_limit_message():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"Information": "rate limit exceeded"}
    fake_response.raise_for_status = Mock()

    with patch("tickerflow.extract.requests.get", return_value=fake_response):
        result = fetch_quote("AMD", api_key="fake_key_for_testing")

    assert result == {}  # your code should return {} on missing "Global Quote"