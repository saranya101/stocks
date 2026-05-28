import requests
import pandas as pd
from io import StringIO

def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tables = pd.read_html(StringIO(response.text))

    table = tables[0]

    tickers = table["Symbol"].tolist()
    tickers = [ticker.replace(".", "-") for ticker in tickers]

    return tickers