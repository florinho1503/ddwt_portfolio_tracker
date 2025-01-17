import requests

BASE_URL = "http://127.0.0.1:5000"
SESSION_COOKIE = {"session": ".eJxtjtFKxTAMhl9l9npIuy5pu2fwQsQ7OYwsTXeGc4N1E-Rw3t3quVGUQMKf5Ev-i-rTTPksWXUvF1Xtpag3yZlGUbV6knHK-0b7tC5VPpjLJB3zXfU4C2Wp5nWspuVena71X_hhHadf1P9rzxstmfj2gt4l_kDmjy_oVBeXm-Sz6vbtkKKmqDrFTM4YDLoxyXgdk02REgGSFmQMjSAR22DawfhWQ4MWvB6aBNYnSOBaS_AtnIBnCSGAtoMPgKn1oVznEB2K9s6IC-BtiWBYDxyZTSze-yPLdnPji-S8pX5fX2UpDVN8WVtuSNKAQ4wuJCwJg1iLCBp5aA036voJ55R3Yg.Z4qAWA.Lx_Xo8ky6ICI9XU8vncJ-WPApaI"}

def test_get_portfolio_summary():
    response = requests.get(f"{BASE_URL}/api/portfolio", cookies=SESSION_COOKIE)
    assert response.status_code == 200
    print(response.json())

def test_get_transactions():
    response = requests.get(f"{BASE_URL}/api/portfolio/transactions", cookies=SESSION_COOKIE)
    assert response.status_code == 200
    print(response.json())

def test_get_holdings():
    response = requests.get(f"{BASE_URL}/api/portfolio/holdings", cookies=SESSION_COOKIE)
    assert response.status_code == 200
    print(response.json())

def test_add_transaction():
    data = {
        "stock_ticker": "GOOG",
        "quantity": 2,
        "price": 1500.00,
        "date": "2025-01-14",
        "transaction_type": "BUY"
    }
    response = requests.post(
        f"{BASE_URL}/api/portfolio/transaction",
        json=data,
        cookies=SESSION_COOKIE
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    print(response.json())


test_get_portfolio_summary()
test_get_transactions()
test_get_holdings()
test_add_transaction()
