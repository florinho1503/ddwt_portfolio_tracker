import yfinance as yf
import requests
from bs4 import BeautifulSoup

def fetch_historical_data(stock_ticker):
    """Function to get historical price data of a stock (wij gebruiken alleen open/close)"""
    stock = yf.Ticker(stock_ticker)
    data = stock.history(period="1y")  # Adjust period as needed
    print(data)
    return data[['Close']]  # Return closing prices

fetch_historical_data("ADYEN.AS")


def get_live_price(stock_ticker):
    """voor live data scrapen we de website van yahoofinance, want dit kan niet (gratis) via de api"""

    url = f"https://finance.yahoo.com/quote/{stock_ticker}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
    price = price_tag.text.replace(",", "")
    return price


# Example usage
price = get_live_price('ADYEN.AS')
print(price)



