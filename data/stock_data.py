import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period="6mo"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    df = df[['Close', 'Volume']]
    df.dropna(inplace=True)
    return df
    