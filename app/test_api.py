import requests
from requests.auth import HTTPBasicAuth

# This file was used to test the API during the development process. It has been left in the project directory in case
# the grader wants to test out the API functionality. Other tools such as httpie or curl can also be utilized to test
# our API, for that please refer to the API documentation on Github.

# Please enter register account information here
username = 'test'
password = '123'

BASE_URL = "http://127.0.0.1:5000"

def test_get_portfolio_summary():
    response = requests.get(f"{BASE_URL}/api/portfolio", auth=HTTPBasicAuth(username, password))
    assert response.status_code == 200
    print(response.json())

def test_get_transactions():
    response = requests.get(f"{BASE_URL}/api/portfolio/transactions", auth=HTTPBasicAuth(username, password))
    assert response.status_code == 200
    print(response.json())

def test_get_holdings():
    response = requests.get(f"{BASE_URL}/api/portfolio/holdings", auth=HTTPBasicAuth(username, password))
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
        auth=HTTPBasicAuth(username, password)
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201

test_get_portfolio_summary()
test_get_transactions()
test_get_holdings()
test_add_transaction()
