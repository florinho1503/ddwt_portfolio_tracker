import sqlite3
import pandas as pd
from .data_fetching import fetch_historical_data
import matplotlib.pyplot as plt
import os
from flask import current_app
from app.models import Transaction, Portfolio


class PortfolioAnalyzer:
    def __init__(self, user_id):
        """
        Initialize the PortfolioAnalyzer for a specific user.
        """
        self.user_id = user_id
        self.transactions = self.get_user_transactions()
        self.portfolio_df = None

    def get_user_transactions(self):
        """
        Fetch transactions for the user's portfolio using SQLAlchemy.
        """
        portfolio = Portfolio.query.filter_by(user_id=self.user_id).first()

        if not portfolio:
            return []  # Return an empty list if the portfolio doesn't exist

        return Transaction.query.filter_by(portfolio_id=portfolio.portfolio_id).all()

    def calculate_current_holdings(self):
        """
        Calculate the user's portfolio value over time and current holdings based on value.
        """
        if not self.transactions:
            print("No transactions found for this user.")
            return pd.DataFrame(columns=["Portfolio Value"]), {}

        stock_tickers = list(set(t.stock_ticker for t in self.transactions))

        historical_data = {}
        for stock_ticker in stock_tickers:
            stock_data = fetch_historical_data(stock_ticker)
            if 'Close' not in stock_data:
                raise ValueError(f"Invalid stock ticker: {stock_ticker}")
            historical_data[stock_ticker] = stock_data['Close']
            historical_data[stock_ticker].index = historical_data[stock_ticker].index.tz_localize(None)

        if not historical_data:
            print("No valid historical data found.")
            return pd.DataFrame(columns=["Portfolio Value"]), {}

        date_range = pd.date_range(
            start=min(pd.Timestamp(t.date) for t in self.transactions),
            end=pd.Timestamp.today()
        )
        self.portfolio_df = pd.DataFrame(index=date_range, columns=["Portfolio Value"] + stock_tickers)
        self.portfolio_df["Portfolio Value"] = None

        holdings = {stock: 0 for stock in stock_tickers}
        latest_values = {stock: 0 for stock in stock_tickers}

        for current_date in self.portfolio_df.index:
            for transaction in self.transactions:
                transaction_date = pd.Timestamp(transaction.date).tz_localize(None)
                if transaction_date == current_date:
                    if transaction.transaction_type.lower() == "buy":
                        holdings[transaction.stock_ticker] += transaction.quantity
                    elif transaction.transaction_type.lower() == "sell":
                        holdings[transaction.stock_ticker] -= transaction.quantity

            portfolio_value = 0
            for stock, qty in holdings.items():
                if stock in historical_data:
                    available_data = historical_data[stock][historical_data[stock].index <= current_date]
                    if not available_data.empty:
                        last_closing_price = available_data.iloc[-1]
                        portfolio_value += qty * last_closing_price
                        self.portfolio_df.loc[current_date, stock] = qty
                        latest_values[stock] = qty * last_closing_price

            if portfolio_value > 0:
                self.portfolio_df.loc[current_date, "Portfolio Value"] = portfolio_value

        self.portfolio_df.fillna(method="ffill", inplace=True)
        return self.portfolio_df, latest_values

    def plot_portfolio_performance(self, user_id):
        """
        Plot the portfolio performance for the given user, including individual holdings.
        """

        portfolio_df, _ = self.calculate_current_holdings()

        if portfolio_df is None:
            return None

        fig, ax = plt.subplots()

        portfolio_df["Portfolio Value"].plot(ax=ax, label="Total Portfolio Value", linewidth=2)

        for stock in portfolio_df.columns:
            if stock != "Portfolio Value":
                historical_data = fetch_historical_data(stock)['Close']
                historical_data.index = historical_data.index.tz_localize(None)

                aligned_data = historical_data.reindex(portfolio_df.index, method="ffill")

                (portfolio_df[stock] * aligned_data).fillna(0).plot(
                    ax=ax, label=f"{stock} Value", linewidth=1.5
                )

        ax.set_title("Portfolio Performance Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend()
        plt.tight_layout()

        static_dir = os.path.join(current_app.root_path, "static")
        os.makedirs(static_dir, exist_ok=True)  # Create the directory if it doesn't exist
        plot_path = os.path.join(static_dir, f"portfolio_performance_{user_id}.png")

        plt.savefig(plot_path)
        plt.close()
        return f"portfolio_performance_{user_id}.png"
