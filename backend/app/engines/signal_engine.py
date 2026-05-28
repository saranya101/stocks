import pandas as pd
import yfinance as yf


def calculate_rsi(
    series,
    period=14
):

    delta = series.diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(period)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(period)
        .mean()
    )

    rs = gain / loss

    return 100 - (
        100 / (1 + rs)
    )


def calculate_signal(
    ticker,
    timeframe="5m"
):

    stock = yf.download(
        ticker,
        period="5d",
        interval=timeframe,
        progress=False,
        auto_adjust=True
    )

    if stock.empty:
        return None

    close = stock["Close"]

    sma_fast = close.rolling(9).mean()
    sma_slow = close.rolling(21).mean()

    rsi = calculate_rsi(close)

    latest_price = float(close.iloc[-1])

    latest_fast = float(
        sma_fast.iloc[-1]
    )

    latest_slow = float(
        sma_slow.iloc[-1]
    )

    latest_rsi = float(
        rsi.iloc[-1]
    )

    confidence = 50

    reasons = []

    # TREND

    if latest_fast > latest_slow:

        confidence += 20

        reasons.append(
            "Bullish trend structure."
        )

    else:

        confidence -= 20

        reasons.append(
            "Bearish trend structure."
        )

    # RSI

    if 45 <= latest_rsi <= 65:

        confidence += 10

        reasons.append(
            "Healthy momentum."
        )

    elif latest_rsi > 75:

        confidence -= 15

        reasons.append(
            "Overbought conditions."
        )

    elif latest_rsi < 30:

        confidence += 5

        reasons.append(
            "Oversold bounce potential."
        )

    # VOLUME

    recent_volume = (
        stock["Volume"]
        .tail(10)
        .mean()
    )

    latest_volume = float(
        stock["Volume"].iloc[-1]
    )

    if latest_volume > recent_volume * 1.5:

        confidence += 10

        reasons.append(
            "Strong volume confirmation."
        )

    confidence = max(
        0,
        min(100, confidence)
    )

    # FINAL SIGNAL

    if confidence >= 80:

        signal = "VERY BULLISH"

    elif confidence >= 65:

        signal = "BULLISH"

    elif confidence >= 45:

        signal = "NEUTRAL"

    elif confidence >= 30:

        signal = "BEARISH"

    else:

        signal = "VERY BEARISH"

    return {
        "ticker": ticker.upper(),
        "timeframe": timeframe,
        "signal": signal,
        "confidence": confidence,
        "price": latest_price,
        "rsi": round(latest_rsi, 2),
        "sma_fast": round(latest_fast, 2),
        "sma_slow": round(latest_slow, 2),
        "reasons": reasons
    }