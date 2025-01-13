import sqlite3
import pandas as pd
from .data_fetching import fetch_historical_data, get_live_price
import matplotlib.pyplot as plt
import os
from flask import current_app
from app.models import Transaction, Portfolio


class PortfolioAnalyzer:
    def __init__(self, user_id):
        """
        Initialize the PortfolioAnalyzer for a specific user.

        Args:
            user_id (int): The ID of the user whose portfolio will be analyzed.
        """
        self.user_id = user_id
        self.transactions = self.get_user_transactions()
        self.portfolio_df = None

    def get_user_transactions(self):
        """Fetch transactions for the user's portfolio using SQLAlchemy."""
        portfolio = Portfolio.query.filter_by(user_id=self.user_id).first()

        if not portfolio:
            return []  # Return an empty list if the portfolio doesn't exist

        return Transaction.query.filter_by(portfolio_id=portfolio.portfolio_id).all()

    def calculate_current_holdings(self):
        """Calculate the user's portfolio value over time."""
        if not self.transactions:
            print("No transactions found for this user.")
            return None

        # Extract unique stock tickers
        stock_tickers = list(set(t.stock_ticker for t in self.transactions))

        # Fetch historical data for each stock
        historical_data = {}
        for stock_ticker in stock_tickers:
            historical_data[stock_ticker] = fetch_historical_data(stock_ticker)['Close']
            historical_data[stock_ticker].index = historical_data[stock_ticker].index.tz_localize(None)

        # Create a DataFrame to store portfolio value over time
        date_range = pd.date_range(
            start=min(pd.Timestamp(t.date) for t in self.transactions),
            end=pd.Timestamp.today()
        )
        self.portfolio_df = pd.DataFrame(index=date_range, columns=["Portfolio Value"] + stock_tickers)
        self.portfolio_df["Portfolio Value"] = None  # Set to None for forward-filling

        # Initialize holdings
        holdings = {stock: 0 for stock in stock_tickers}

        for current_date in self.portfolio_df.index:
            # Process transactions for the current date
            for transaction in self.transactions:
                transaction_date = pd.Timestamp(transaction.date).tz_localize(None)
                if transaction_date == current_date:
                    if transaction.transaction_type.lower() == "buy":
                        holdings[transaction.stock_ticker] += transaction.quantity
                    elif transaction.transaction_type.lower() == "sell":
                        holdings[transaction.stock_ticker] -= transaction.quantity

            # Calculate portfolio value for the current date
            portfolio_value = 0
            for stock, qty in holdings.items():
                if stock in historical_data and current_date in historical_data[stock].index:
                    historical_price = historical_data[stock].loc[current_date]
                    portfolio_value += qty * historical_price
                    self.portfolio_df.loc[current_date, stock] = qty

            if portfolio_value > 0:
                self.portfolio_df.loc[current_date, "Portfolio Value"] = portfolio_value

        # Forward-fill holdings for non-trading days
        self.portfolio_df.fillna(method="ffill", inplace=True)
        return self.portfolio_df

    def plot_portfolio_performance(self, user_id):
        """Plot the portfolio performance for the given user, including individual holdings."""
        # Calculate current holdings
        portfolio_df = self.calculate_current_holdings()

        if portfolio_df is None:
            return None  # No transactions to plot

        # Create a new figure and axis
        fig, ax = plt.subplots()

        # Plot the total portfolio value
        portfolio_df["Portfolio Value"].plot(ax=ax, label="Total Portfolio Value", linewidth=2)

        # Plot individual stock holdings
        for stock in portfolio_df.columns:
            if stock != "Portfolio Value":
                # Fetch historical data
                historical_data = fetch_historical_data(stock)['Close']
                # Convert historical data index to tz-naive
                historical_data.index = historical_data.index.tz_localize(None)

                aligned_data = historical_data.reindex(portfolio_df.index, method="ffill")

                (portfolio_df[stock] * aligned_data).fillna(0).plot(
                    ax=ax, label=f"{stock} Value", linewidth=1.5
                )
        # Add labels and title

        # Add labels and title
        ax.set_title("Portfolio Performance Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend()
        plt.tight_layout()

        # Save the plot to the static directory
        static_dir = os.path.join(current_app.root_path, "static")
        os.makedirs(static_dir, exist_ok=True)  # Create the directory if it doesn't exist
        plot_path = os.path.join(static_dir, f"portfolio_performance_{user_id}.png")

        # Save the plot
        plt.savefig(plot_path)
        plt.close()
        return f"portfolio_performance_{user_id}.png"
