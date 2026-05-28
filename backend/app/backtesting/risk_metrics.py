import math

def calculate_risk_metrics(equity_curve):
    if len(equity_curve) < 2:
        return {
            "sharpe": 0,
            "sortino": 0,
            "calmar": 0
        }

    daily_returns = []

    for i in range(1, len(equity_curve)):
        yesterday = equity_curve[i - 1]["value"]
        today = equity_curve[i]["value"]

        if yesterday != 0:
            daily_returns.append((today - yesterday) / yesterday)

    if len(daily_returns) == 0:
        return {
            "sharpe": 0,
            "sortino": 0,
            "calmar": 0
        }

    average_daily_return = sum(daily_returns) / len(daily_returns)

    variance = sum(
        (r - average_daily_return) ** 2
        for r in daily_returns
    ) / len(daily_returns)

    volatility = math.sqrt(variance)

    downside_returns = [
        r for r in daily_returns
        if r < 0
    ]

    if len(downside_returns) > 0:
        downside_variance = sum(
            r ** 2 for r in downside_returns
        ) / len(downside_returns)

        downside_volatility = math.sqrt(downside_variance)
    else:
        downside_volatility = 0

    annual_return = average_daily_return * 252
    annual_volatility = volatility * math.sqrt(252)
    annual_downside_volatility = downside_volatility * math.sqrt(252)

    sharpe = 0
    if annual_volatility != 0:
        sharpe = annual_return / annual_volatility

    sortino = 0
    if annual_downside_volatility != 0:
        sortino = annual_return / annual_downside_volatility

    values = [point["value"] for point in equity_curve]

    start_value = values[0]
    end_value = values[-1]

    total_return = (end_value - start_value) / start_value

    peak = values[0]
    max_drawdown = 0

    for value in values:
        if value > peak:
            peak = value

        drawdown = (peak - value) / peak

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    calmar = 0
    if max_drawdown != 0:
        calmar = total_return / max_drawdown

    return {
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar
    }