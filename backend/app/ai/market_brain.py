def classify_signal(confidence):
    if confidence >= 80:
        return "VERY BULLISH"
    elif confidence >= 65:
        return "BULLISH"
    elif confidence >= 50:
        return "NEUTRAL / WATCH"
    elif confidence >= 35:
        return "BEARISH"
    else:
        return "VERY BEARISH"


def classify_risk(rsi, max_drawdown, rsi_danger_level=80, max_drawdown_allowed=20):
    if rsi > rsi_danger_level or max_drawdown > max_drawdown_allowed:
        return "HIGH"
    elif rsi > 70 or max_drawdown > 15:
        return "MEDIUM"
    else:
        return "LOW"


def analyze_stock_intelligence(
    ticker,
    close,
    sma_fast,
    sma_slow,
    rsi,
    backtest_return,
    max_drawdown,
    win_rate,
    news_score=0,
    news_label="NEUTRAL NEWS",
    trend_weight=15,
    momentum_weight=10,
    backtest_weight=15,
    risk_penalty=15,
    win_rate_weight=10,
    news_weight=10,
    rsi_danger_level=80,
    max_drawdown_allowed=20
):
    confidence = 50
    reasons = []

    if sma_fast > sma_slow:
        confidence += trend_weight
        reasons.append("Trend is bullish.")
    else:
        confidence -= trend_weight
        reasons.append("Trend is bearish.")

    if 40 <= rsi <= 65:
        confidence += momentum_weight
        reasons.append("RSI is healthy.")
    elif rsi > rsi_danger_level:
        confidence -= risk_penalty
        reasons.append("RSI is overextended.")
    elif rsi < 30:
        confidence += momentum_weight / 2
        reasons.append("RSI is oversold.")

    if backtest_return > 30:
        confidence += backtest_weight
        reasons.append("Backtest return is strong.")
    elif backtest_return > 10:
        confidence += backtest_weight / 2
        reasons.append("Backtest return is positive.")
    else:
        confidence -= backtest_weight / 2
        reasons.append("Backtest return is weak.")

    if max_drawdown < 10:
        confidence += risk_penalty / 2
        reasons.append("Drawdown is controlled.")
    elif max_drawdown > max_drawdown_allowed:
        confidence -= risk_penalty
        reasons.append("Drawdown is too high.")

    if win_rate > 60:
        confidence += win_rate_weight
        reasons.append("Win rate is strong.")
    elif win_rate < 40:
        confidence -= win_rate_weight
        reasons.append("Win rate is weak.")

        news_adjustment = (news_score / 50) * news_weight

    confidence += news_adjustment

    if news_score > 15:
        reasons.append("News sentiment is bullish.")
    elif news_score < -15:
        reasons.append("News sentiment is bearish.")
    else:
        reasons.append("News sentiment is neutral.")

    confidence = round(max(0, min(100, confidence)), 2)

    return {
        "ticker": ticker,
        "confidence": confidence,
        "signal": classify_signal(confidence),
        "risk_level": classify_risk(
            rsi,
            max_drawdown,
            rsi_danger_level,
            max_drawdown_allowed
        ),
        "news_score": news_score,
        "news_label": news_label,
        "reasons": reasons
    }