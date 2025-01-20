import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:5000"


def test_get_portfolio_summary():
    response = requests.get(f"{BASE_URL}/api/portfolio", auth=HTTPBasicAuth('test', '123'))
    assert response.status_code == 200
    print(response.json())


def test_get_transactions():
    response = requests.get(f"{BASE_URL}/api/portfolio/transactions", auth=HTTPBasicAuth('test', '123'))
    assert response.status_code == 200
    print(response.json())


def test_get_holdings():
    response = requests.get(f"{BASE_URL}/api/portfolio/holdings", auth=HTTPBasicAuth('test', '123'))
    assert response.status_code == 200
    print(response.json())


def test_add_transaction():
    data = {
        "stock_ticker": "TSLA",
        "quantity": 2,
        "price": 1500.00,
        "date": "2025-01-14",
        "transaction_type": "BUY"
    }
    response = requests.post(
        f"{BASE_URL}/api/portfolio/transaction",
        json=data,
        auth=HTTPBasicAuth('test', '123')
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201

test_get_portfolio_summary()
test_get_transactions()
test_get_holdings()
test_add_transaction()
