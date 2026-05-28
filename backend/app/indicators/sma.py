def calculate_sma(data, window):
    return data.rolling(window).mean()