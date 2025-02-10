# Portfolio Tracker
The Portfolio Tracker is a financial web application that allows users to manage their stock/crypto portfolio, track historical data, and visualize performance through graphs. 

It also includes a home page with various articles on the latest financial news, and current prices of indices and significant movers.

## Installation and running application
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/florinho1503/ddwt_portfolio_tracker
   cd ddwt_portfolio_tracker
2. **Set up virtual environment**:
  python3 -m venv venv
  source venv/bin/activate (for Windows: venv\Scripts\activate)
3. **Install dependencies**:
  pip install -r requirements.txt
4. **Run the app**:
  flask run

In the image below, you can see an example of a portfolio. We can add a transaction by
filling out the empty row with our new transaction data, and click add. We can also remove previous rows,
or **edit** previous rows, simply by **clicking on one of the cells** in the table, changing
its value and save the changes. 

![Portfolio](app/static/images/portfolio_example.png)


# Portfolio Tracker API

## Authentication:

HTTP basic authentication is used in this api.
Include username and password in your request as shown in the following request


Replace 'http://127.0.0.1:5000' if the site is deployed on another URL


**Example Request with Authentication**:
```bash
curl -u username:password http://127.0.0.1:5000/api/portfolio
```

---

## Endpoints

### 1. Getting a summary of your current portfolio

- **URL:** `/api/portfolio`
- **Method:** `GET`


**Example Response:**
```json
{
  "portfolio_id": 1,
  "total_value": 12500.50,
  "transaction_count": 4
}
```

### 2. Viewing your transaction history

- **URL:** `/api/portfolio/transactions`
- **Method:** `GET`


**Example Response:**
```json
[
  {
    "date": "2025-01-14",
    "id": 36,
    "price": 1500.0,
    "quantity": 2.0,
    "stock_ticker": "GOOG",
    "transaction_type": "BUY"
  },
  {
    "date": "2025-01-14",
    "id": 37,
    "price": 1500.0,
    "quantity": 2.0,
    "stock_ticker": "AAPL",
    "transaction_type": "BUY"
  },
]
```


### 3. View current holdings

- **URL:** `/api/portfolio/holdings`
- **Method:** `GET`

**Example Response:**
```json
{
  "AAPL": 10,
  "TSLA": 5
}
```


### 4. Add a Transaction

- **URL:** `/api/portfolio/transaction`
- **Method:** `POST`


**Example request:**
```json
{
  "stock_ticker": "TSLA",
  "quantity": 2,
  "price": 1500.00,
  "date": "2025-01-14",
  "transaction_type": "BUY"
}
```









