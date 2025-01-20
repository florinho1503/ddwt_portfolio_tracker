
import yfinance as yf
import requests
from bs4 import BeautifulSoup

def fetch_historical_data(stock_ticker):
    """Function to get historical price data of a stock (wij gebruiken alleen open/close)"""
    stock = yf.Ticker(stock_ticker)
    data = stock.history(period="1y")  # Adjust period as needed
    return data[['Close']]  # Return closing prices

