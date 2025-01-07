from portfolio import Portfolio

# Create a Portfolio instance
my_portfolio = Portfolio()

# Add transactions
# my_portfolio.add_transaction("AAPL", 10, 150, "2025-01-02", "buy")
# my_portfolio.add_transaction("TSLA", 5, 200, "2025-01-02", "buy")
# my_portfolio.add_transaction("META", 5, 160, "2025-01-02", "buy")

# View transactions
transactions = my_portfolio.get_transactions()
print("Transactions:")
for transaction in transactions:
    print(transaction)

# Get live portfolio value
live_value = my_portfolio.get_live_portfolio_value()
print(f"Live Portfolio Value: ${live_value:,.2f}")

# Plot historical portfolio performance
my_portfolio.plot_portfolio_performance()
