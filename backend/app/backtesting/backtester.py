import pandas as pd


def run_backtest(
    stock,
    starting_cash=10000,
    fast_col="SMA20",
    slow_col="SMA50",
    rsi_sell=80,
    stop_loss=0.05,
):
    cash = float(starting_cash)
    shares = 0
    buy_price = 0
    buy_date = None

    trades = []
    trade_returns = []
    hold_days = []
    equity_curve = []

    peak_value = starting_cash
    max_drawdown = 0

    for i in range(50, len(stock)):
        row = stock.iloc[i]
        prev_row = stock.iloc[i - 1]

        date = str(row["Date"])
        close = float(row["Close"])
        fast_sma = float(row[fast_col])
        slow_sma = float(row[slow_col])
        rsi = float(row["RSI"])

        prev_fast = float(prev_row[fast_col])
        prev_slow = float(prev_row[slow_col])

        current_value = cash + shares * close
        peak_value = max(peak_value, current_value)
        drawdown = (peak_value - current_value) / peak_value
        max_drawdown = max(max_drawdown, drawdown)

        equity_curve.append({
            "date": date,
            "value": float(current_value),
        })

        trend_confirmed = fast_sma > slow_sma
        fresh_cross = prev_fast <= prev_slow and fast_sma > slow_sma
        healthy_rsi = 40 < rsi < 75

        entry_signal = trend_confirmed and healthy_rsi

        if shares == 0 and entry_signal:
            shares = cash / close
            buy_price = close
            buy_date = row["Date"]
            cash = 0

            trades.append({
                "date": date,
                "type": "BUY",
                "price": close,
            })

        elif shares > 0:
            stop_hit = close <= buy_price * (1 - stop_loss)
            signal_exit = fast_sma < slow_sma or rsi >= rsi_sell

            if stop_hit or signal_exit:
                cash = shares * close
                shares = 0

                trade_return = ((close - buy_price) / buy_price) * 100
                trade_returns.append(trade_return)

                days_held = max(
                    1,
                    (pd.to_datetime(row["Date"]) - pd.to_datetime(buy_date)).days,
                )
                hold_days.append(days_held)

                trades.append({
                    "date": date,
                    "type": "SELL",
                    "price": close,
                    "reason": "STOP LOSS" if stop_hit else "SIGNAL EXIT",
                    "return_pct": trade_return,
                    "days_held": days_held,
                })

    final_price = float(stock.iloc[-1]["Close"])

    if shares > 0:
        cash = shares * final_price

        trade_return = ((final_price - buy_price) / buy_price) * 100
        trade_returns.append(trade_return)

        days_held = max(
            1,
            (pd.to_datetime(stock.iloc[-1]["Date"]) - pd.to_datetime(buy_date)).days,
        )
        hold_days.append(days_held)

        trades.append({
            "date": str(stock.iloc[-1]["Date"]),
            "type": "SELL",
            "price": final_price,
            "reason": "END OF TEST",
            "return_pct": trade_return,
            "days_held": days_held,
        })

        shares = 0

    final_value = cash
    total_return = ((final_value - starting_cash) / starting_cash) * 100

    winners = [r for r in trade_returns if r > 0]
    losers = [r for r in trade_returns if r < 0]

    total_wins = sum(winners)
    total_losses = abs(sum(losers))

    completed_trades = len(trade_returns)
    win_rate = (len(winners) / completed_trades) * 100 if completed_trades else 0
    profit_factor = total_wins / total_losses if total_losses > 0 else total_wins

    return {
        "starting_cash": float(starting_cash),
        "final_value": float(final_value),
        "total_return": float(total_return),
        "max_drawdown": float(max_drawdown * 100),
        "total_trades": completed_trades,
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor),
        "average_days_held": float(sum(hold_days) / len(hold_days)) if hold_days else 0,
        "largest_win": float(max(trade_returns)) if trade_returns else 0,
        "largest_loss": float(min(trade_returns)) if trade_returns else 0,
        "trades": trades,
        "equity_curve": equity_curve,
    }