import requests

BASE_URL = "http://127.0.0.1:5000"
SESSION_COOKIE = {"session": ".eJzNU0tLxDAQ_ivZnBdJ2ua1_0DwIOJFRJbpZNIt1kaSdEXE_25WL74OgohLDmEm8z1mwjzxbZgg7yjzzfUTZ6Ve_I5yhoH4mp9PBJnYFAc2zqxEBoj1kZXdmNl9rTnhN8_rr7gLGsZcEpQxziwvr6CwTKvvq89jKiFOY2SYCAr5d5DpccU-uDgaxdN5D9Po2ZIpzXBHLKY6kpwfYvJHY_IsDuMPpK7iwnawJ9YTzQfGoarFpfyO9TLBnAHfuq3snxr4b9DR_sYfjeBmXZc9Ud7xTUkL1Wj0fMMRwUipnWhkkFb40AYPAZQGQRq1a0gDYOtk10vbCdXoVlnRN0G1NqigTNeCeg0MKYvknFOi7a1TOnTWVXZ03mgS1kgyTtm2HidR9OgRpa_et4cdenMja4g5hW2JtzTXhAiEnfUV0QlnfaehN_pglWRo-840CoNCNPz5BVwUmcY.Z4fEJA.Dq-TFvOGH2gqblBTgDY8PVD06VU"}

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
