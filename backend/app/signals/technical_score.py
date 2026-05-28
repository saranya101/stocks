def calculate_technical_score(sma20, sma50, rsi):
    score = 0
    reasons = []

    # Trend score
    if sma20 > sma50:
        score += 40
        reasons.append("SMA20 is above SMA50, showing bullish trend.")
    else:
        score -= 30
        reasons.append("SMA20 is below SMA50, showing bearish trend.")

    # RSI score
    if rsi < 30:
        score += 25
        reasons.append("RSI is below 30, stock may be oversold.")
    elif 30 <= rsi <= 70:
        score += 20
        reasons.append("RSI is in a healthy/neutral range.")
    elif 70 < rsi <= 80:
        score -= 10
        reasons.append("RSI is above 70, stock may be overbought.")
    else:
        score -= 30
        reasons.append("RSI is above 80, stock is extremely overbought.")

    return score, reasons