import yfinance as yf


def fetch_historical_data(stock_ticker):
    """Function to get historical price data of a stock (wij gebruiken alleen open/close)"""
    stock = yf.Ticker(stock_ticker)
    data = stock.history(period="1y")
    return data[['Close']]

