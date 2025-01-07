import sqlite3
import pandas as pd
from datetime import datetime
from data_fetching import fetch_historical_data, get_live_price
import matplotlib.pyplot as plt


class Portfolio:
    def __init__(self, db_path="portfolio.db"):
        self.db_path = db_path
        self._initialize_database()
        self.historical_data = {}  # Cache for historical price data

    def _initialize_database(self):
        """Create the database and transactions table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            stock_ticker TEXT,
                            quantity INTEGER,
                            price REAL,
                            date TEXT,
                            transaction_type TEXT
                          )''')
        conn.commit()
        conn.close()

    def add_transaction(self, stock_ticker, quantity, price, date, transaction_type):
        """Add a transaction to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO transactions (stock_ticker, quantity, price, date, transaction_type)
                          VALUES (?, ?, ?, ?, ?)''',
                       (stock_ticker, quantity, price, date, transaction_type))
        conn.commit()
        conn.close()

    def get_transactions(self):
        """View all transactions in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        conn.close()
        return transactions

    def get_live_portfolio_value(self):
        """Calculate the current live value of the portfolio based on holdings."""
        holdings = self._calculate_holdings()
        total_value = 0
        for stock, qty in holdings.items():
            if qty > 0:
                live_price = get_live_price(stock)
                total_value += qty * live_price
        return total_value

    def _calculate_holdings(self):
        """Calculate the current holdings based on transactions."""
        holdings = {}
        transactions = self.get_transactions()
        for _, stock_ticker, quantity, _, _, transaction_type in transactions:
            if stock_ticker not in holdings:
                holdings[stock_ticker] = 0
            if transaction_type == "buy":
                holdings[stock_ticker] += quantity
            elif transaction_type == "sell":
                holdings[stock_ticker] -= quantity
        return holdings

    def plot_portfolio_performance(self):
        transactions = self.get_transactions()
        stock_tickers = list(set([t[1] for t in transactions]))  # Get unique stock tickers

        # Fetch historical data for each stock
        historical_data = {}
        for stock_ticker in stock_tickers:
            historical_data[stock_ticker] = fetch_historical_data(stock_ticker)['Close']
            # Convert historical data index to tz-naive
            historical_data[stock_ticker].index = historical_data[stock_ticker].index.tz_localize(None)
            print(f"Historical data for {stock_ticker}:")
            print(historical_data[stock_ticker].tail())  # Print the last few rows of historical data

        # Create a DataFrame to store portfolio value over time
        date_range = pd.date_range(start=min([t[4] for t in transactions]), end=pd.Timestamp.today())
        portfolio_df = pd.DataFrame(index=date_range, columns=["Portfolio Value"])
        portfolio_df["Portfolio Value"] = None  # Set to None for proper forward filling

        # Initialize holdings dictionary
        holdings = {stock: 0 for stock in stock_tickers}

        # Iterate through the date range to calculate portfolio value day by day
        for current_date in portfolio_df.index:
            # Process transactions on the current date
            for transaction in transactions:
                stock_ticker, quantity, price, date, transaction_type = transaction[1:]
                transaction_date = pd.Timestamp(date).tz_localize(None)
                if transaction_date == current_date:
                    if transaction_type == "buy":
                        holdings[stock_ticker] += quantity
                    elif transaction_type == "sell":
                        holdings[stock_ticker] -= quantity
                    print(f"Processed transaction on {current_date}: {transaction}")
                    print(f"Updated holdings: {holdings}")

            # Calculate portfolio value for the current date
            portfolio_value = 0
            for stock, qty in holdings.items():
                if stock in historical_data and current_date in historical_data[stock].index:
                    historical_price = historical_data[stock].loc[current_date]
                    portfolio_value += qty * historical_price

            # Update portfolio value only if it's a trading day
            if portfolio_value > 0:
                portfolio_df.loc[current_date, "Portfolio Value"] = portfolio_value

        # Forward-fill the portfolio value for non-trading days (e.g., weekends)
        portfolio_df["Portfolio Value"] = portfolio_df["Portfolio Value"].ffill()

        # Debug: Print final portfolio DataFrame
        print("Final portfolio value DataFrame:")
        print(portfolio_df.tail())

        # Plot the portfolio performance
        portfolio_df.plot(title="Portfolio Performance Over Time")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value")
        plt.show()

