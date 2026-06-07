import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker, period="1y", interval="1d"):
    try:
        stock = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False
        )

        if stock is None or stock.empty:
            return None

        if isinstance(stock.columns, pd.MultiIndex):
            stock.columns = stock.columns.get_level_values(0)

        stock = stock.reset_index()

        return stock

    except Exception as e:
        print(f"{ticker} fetch error:", e)
        return None