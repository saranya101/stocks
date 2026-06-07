import math
import numpy as np
from app.services.company_profile_service import get_company_profile

def safe_float(value, default=0.0):
    try:
        value = float(value)
    except Exception:
        return default

    if math.isnan(value) or math.isinf(value):
        return default

    return value


def normalize_score(value, default=50):
    return max(0, min(100, safe_float(value, default)))


def calculate_atr(stock, period=14):
    high = stock["High"]
    low = stock["Low"]
    close = stock["Close"]
    prev_close = close.shift(1)

    tr = np.maximum(
        high - low,
        np.maximum(abs(high - prev_close), abs(low - prev_close)),
    )

    atr = tr.rolling(period).mean().iloc[-1]

    return safe_float(atr, safe_float((high - low).mean(), 0))


def calculate_conviction(
    technical_score,
    backtest_score,
    news_score,
    volume_score,
):
    technical_score = normalize_score(technical_score)
    backtest_score = normalize_score(backtest_score)
    news_score = normalize_score(news_score)
    volume_score = normalize_score(volume_score)

    conviction = (
        technical_score * 0.35
        + backtest_score * 0.25
        + volume_score * 0.20
        + news_score * 0.10
    )

    if backtest_score < 45:
        conviction -= 8

    if technical_score < 55:
        conviction -= 10

    if volume_score < 50:
        conviction -= 5

    if technical_score >= 75 and volume_score >= 70:
        conviction += 5

    if technical_score >= 75 and backtest_score >= 70:
        conviction += 5

    return round(max(0, min(100, conviction)), 1)


def calculate_probability(
    technical_score,
    backtest_score,
    news_score,
    volume_score,
):
    technical_score = normalize_score(technical_score)
    backtest_score = normalize_score(backtest_score)
    news_score = normalize_score(news_score)
    volume_score = normalize_score(volume_score)

    probability = (
        technical_score * 0.30
        + backtest_score * 0.35
        + volume_score * 0.20
        + news_score * 0.15
    )

    return round(max(0, min(100, probability)), 1)


def calculate_trade_grade(conviction):
    if conviction >= 88:
        return "A+"

    if conviction >= 82:
        return "A"

    if conviction >= 72:
        return "B+"

    if conviction >= 62:
        return "B"

    if conviction >= 52:
        return "C"

    return "D"


def determine_direction(
    technical_score,
    conviction,
    backtest_score,
    volume_score,
):
    technical_score = normalize_score(technical_score)
    backtest_score = normalize_score(backtest_score)
    volume_score = normalize_score(volume_score)

    if (
        technical_score >= 60
        and conviction >= 60
        and backtest_score >= 40
        and volume_score >= 45
    ):
        return "LONG"

    return "AVOID"


def determine_status(conviction, direction):
    if direction == "AVOID":
        return "IGNORE"

    if conviction >= 72:
        return "READY"

    if conviction >= 60:
        return "WATCH"

    return "IGNORE"


def determine_recommendation(conviction, direction):
    if direction == "AVOID":
        return "AVOID"

    if conviction >= 82:
        return "STRONG BUY"

    if conviction >= 72:
        return "BUY"

    if conviction >= 60:
        return "WATCH"

    return "AVOID"


def calculate_stop_loss(entry_price, atr):
    entry_price = safe_float(entry_price)
    atr = safe_float(atr)

    if entry_price <= 0 or atr <= 0:
        return 0

    return round(entry_price - atr * 2, 2)


def calculate_take_profit(entry_price, stop_loss, rr=3):
    entry_price = safe_float(entry_price)
    stop_loss = safe_float(stop_loss)

    risk = entry_price - stop_loss

    if risk <= 0:
        return 0

    return round(entry_price + risk * rr, 2)


def calculate_risk_reward(entry_price, stop_loss, take_profit):
    entry_price = safe_float(entry_price)
    stop_loss = safe_float(stop_loss)
    take_profit = safe_float(take_profit)

    risk = abs(entry_price - stop_loss)

    if risk <= 0:
        return 0

    reward = abs(take_profit - entry_price)

    return round(reward / risk, 2)


def calculate_position_size(
    entry_price,
    stop_loss,
    account_size=10000,
    risk_per_trade_pct=0.01,
):
    entry_price = safe_float(entry_price)
    stop_loss = safe_float(stop_loss)

    risk_amount = account_size * risk_per_trade_pct
    risk_per_share = abs(entry_price - stop_loss)

    if entry_price <= 0 or risk_per_share <= 0:
        return {
            "shares": 0,
            "risk_amount": round(risk_amount, 2),
            "risk_per_share": 0,
            "position_value": 0,
        }

    shares = int(risk_amount / risk_per_share)

    return {
        "shares": shares,
        "risk_amount": round(risk_amount, 2),
        "risk_per_share": round(risk_per_share, 2),
        "position_value": round(shares * entry_price, 2),
    }


def estimate_hold_days(conviction):
    if conviction >= 82:
        return 30

    if conviction >= 72:
        return 20

    if conviction >= 62:
        return 14

    return 7


def build_opportunity_reasons(
    direction,
    technical_score,
    backtest_score,
    volume_score,
    news_score,
    rsi=None,
):
    reasons = []

    if direction == "AVOID":
        reasons.append("Setup rejected because confirmation quality is not strong enough.")
    else:
        if technical_score >= 75:
            reasons.append("Trend structure is strongly bullish.")
        elif technical_score >= 60:
            reasons.append("Trend structure is moderately bullish.")

        if backtest_score >= 70:
            reasons.append("Backtest quality supports this setup.")
        elif backtest_score < 45:
            reasons.append("Backtest quality is weak, reducing conviction.")

        if volume_score >= 70:
            reasons.append("Volume confirms the move.")
        elif volume_score < 50:
            reasons.append("Volume confirmation is weak.")

        if news_score >= 65:
            reasons.append("News sentiment provides a positive catalyst.")
        elif news_score <= 35:
            reasons.append("News sentiment is a risk factor.")

    if rsi is not None:
        rsi = safe_float(rsi)

        if rsi >= 70:
            reasons.append("RSI is elevated, so entry timing should be reviewed carefully.")
        elif rsi <= 30:
            reasons.append("RSI is oversold, suggesting possible rebound potential.")
        elif 40 <= rsi <= 65:
            reasons.append("RSI is in a healthy momentum zone.")

    if not reasons:
        reasons.append("Setup has mixed signals and should be reviewed carefully.")

    return reasons


def generate_trade_opportunity(
    ticker,
    current_price,
    atr,
    technical_score,
    backtest_score,
    news_score,
    volume_score,
    rsi=None,
):
    current_price = safe_float(current_price)

    technical_score = normalize_score(technical_score)
    backtest_score = normalize_score(backtest_score)
    news_score = normalize_score(news_score)
    volume_score = normalize_score(volume_score)

    conviction = calculate_conviction(
        technical_score,
        backtest_score,
        news_score,
        volume_score,
    )

    probability = calculate_probability(
        technical_score,
        backtest_score,
        news_score,
        volume_score,
    )

    direction = determine_direction(
        technical_score,
        conviction,
        backtest_score,
        volume_score,
    )

    stop_loss = calculate_stop_loss(current_price, atr)
    take_profit = calculate_take_profit(current_price, stop_loss)

    risk_reward = calculate_risk_reward(
        current_price,
        stop_loss,
        take_profit,
    )

    position = calculate_position_size(
        entry_price=current_price,
        stop_loss=stop_loss,
    )

    recommendation = determine_recommendation(
        conviction,
        direction,
    )

    company_profile = get_company_profile(ticker)

    return {
        "ticker": ticker.upper(),

        "company_name": company_profile.get("company_name"),
        "sector": company_profile.get("sector"),
        "industry": company_profile.get("industry"),
        "market_cap": company_profile.get("market_cap"),
        "country": company_profile.get("country"),
        "website": company_profile.get("website"),
        "description": company_profile.get("description"),
        "exchange": company_profile.get("exchange"),
        "currency": company_profile.get("currency"),
        "yahoo_url": company_profile.get("yahoo_url"),

        "direction": direction,
        "conviction": conviction,
        "probability": probability,
        "grade": calculate_trade_grade(conviction),
        "recommendation": recommendation,
        "entry_price": round(current_price, 2),
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "risk_reward": risk_reward,
        "expected_hold_days": estimate_hold_days(conviction),
        "status": determine_status(conviction, direction),
        "shares": position["shares"],
        "risk_amount": position["risk_amount"],
        "risk_per_share": position["risk_per_share"],
        "position_value": position["position_value"],
        "technical_score": round(technical_score, 1),
        "backtest_score": round(backtest_score, 1),
        "news_score": round(news_score, 1),
        "volume_score": round(volume_score, 1),
        "reasons": build_opportunity_reasons(
            direction=direction,
            technical_score=technical_score,
            backtest_score=backtest_score,
            volume_score=volume_score,
            news_score=news_score,
            rsi=rsi,
        ),
    }