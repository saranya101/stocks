def run_backtest(
    stock,
    starting_cash=10000,
    fast_col="SMA20",
    slow_col="SMA50",
    rsi_sell=80,
    stop_loss=0.05
):
    cash = starting_cash
    shares = 0
    buy_price = 0

    trades = []
    equity_curve = []
    peak_value = starting_cash
    max_drawdown = 0

    for i in range(50, len(stock)):
        row = stock.iloc[i]

        date = str(row["Date"])
        close = row["Close"]
        sma20 = row[fast_col]
        sma50 = row[slow_col]
        rsi = row["RSI"]

        current_value = cash + (shares * close)

        if current_value > peak_value:
            peak_value = current_value

        drawdown = (peak_value - current_value) / peak_value

        if drawdown > max_drawdown:
            max_drawdown = drawdown

        equity_curve.append({
            "date": date,
            "value": current_value
        })

        if sma20 > sma50 and rsi < 70 and shares == 0:
            shares = cash / close
            buy_price = close
            cash = 0

            trades.append({
                "date": date,
                "type": "BUY",
                "price": close
            })

        elif shares > 0 and close < buy_price * (1 - stop_loss):
            cash = shares * close
            shares = 0

            trades.append({
                "date": date,
                "type": "SELL",
                "price": close,
                "reason": "STOP LOSS"
            })

        elif shares > 0 and (sma20 < sma50 or rsi > rsi_sell):
            cash = shares * close
            shares = 0

            trades.append({
                "date": date,
                "type": "SELL",
                "price": close,
                "reason": "SIGNAL EXIT"
            })

    final_price = stock.iloc[-1]["Close"]
    final_value = cash + (shares * final_price)

    total_return = ((final_value - starting_cash) / starting_cash) * 100

    wins = 0
    completed_trades = 0

    for i in range(0, len(trades) - 1, 2):
        buy = trades[i]
        sell = trades[i + 1]

        if buy["type"] == "BUY" and sell["type"] == "SELL":
            completed_trades += 1

            if sell["price"] > buy["price"]:
                wins += 1

    win_rate = 0

    if completed_trades > 0:
        win_rate = (wins / completed_trades) * 100

    return {
        "starting_cash": starting_cash,
        "final_value": final_value,
        "total_return": total_return,
        "max_drawdown": max_drawdown * 100,
        "total_trades": completed_trades,
        "win_rate": win_rate,
        "trades": trades,
        "equity_curve": equity_curve
    }