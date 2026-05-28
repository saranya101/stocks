import yfinance as yf

def fetch_stock_data(ticker, period="6mo"):

    stock = yf.download(
        ticker,
        period=period,
        progress=False,
        auto_adjust=True
    )

    if stock.empty:
        return None

    # FLATTEN MULTI-INDEX COLUMNS
    if hasattr(stock.columns, "levels"):
        stock.columns = stock.columns.get_level_values(0)

    stock = stock.reset_index()

    return stock