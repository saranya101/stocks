from app.services.backtest_service import single_backtest
from app.data.market_data import fetch_stock_data


DEFAULT_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA", "AMD"]


def get_trade_opportunities(tickers=None):
    tickers = tickers or DEFAULT_TICKERS
    opportunities = []

    for ticker in tickers:
        ticker = ticker.upper()

        try:
            backtest = single_backtest(
                ticker=ticker,
                fast=10,
                slow=30,
                rsi_sell=75,
                stop_loss=0.03,
            )

            if backtest.get("error"):
                continue

            stock = fetch_stock_data(ticker, period="6mo")

            if stock is None or stock.empty:
                continue

            clean_close = stock["Close"].dropna()

            if clean_close.empty:
                continue

            latest_price = float(clean_close.iloc[-1])

            total_return = float(backtest.get("total_return", 0))
            alpha = float(backtest.get("alpha", 0))
            win_rate = float(backtest.get("win_rate", 0))
            max_drawdown = float(backtest.get("max_drawdown", 0))
            profit_factor = float(backtest.get("profit_factor", 0))

            conviction = calculate_conviction(
                alpha=alpha,
                win_rate=win_rate,
                profit_factor=profit_factor,
                max_drawdown=max_drawdown,
                total_return=total_return,
            )

            stop_loss_price = latest_price * 0.97
            take_profit_price = latest_price * 1.09

            risk = latest_price - stop_loss_price
            reward = take_profit_price - latest_price
            risk_reward = reward / risk if risk > 0 else 0

            signal = get_signal(conviction)

            opportunities.append(
                {
                    "ticker": ticker,
                    "signal": signal,
                    "conviction": round(conviction, 1),
                    "entry": round(latest_price, 2),
                    "stop_loss": round(stop_loss_price, 2),
                    "take_profit": round(take_profit_price, 2),
                    "risk_reward": round(risk_reward, 2),
                    "total_return": round(total_return, 2),
                    "alpha": round(alpha, 2),
                    "win_rate": round(win_rate, 1),
                    "max_drawdown": round(max_drawdown, 2),
                    "profit_factor": round(profit_factor, 2),
                    "reasons": build_reasons(
                        total_return=total_return,
                        alpha=alpha,
                        win_rate=win_rate,
                        max_drawdown=max_drawdown,
                        profit_factor=profit_factor,
                    ),
                }
            )

        except Exception as e:
            print(f"Trade opportunity failed for {ticker}: {e}")
            continue

    return sorted(opportunities, key=lambda x: x["conviction"], reverse=True)


def calculate_conviction(alpha, win_rate, profit_factor, max_drawdown, total_return):
    score = (
        alpha * 0.3
        + total_return * 0.2
        + win_rate * 0.25
        + profit_factor * 10 * 0.2
        - max_drawdown * 0.15
    )

    return max(0, min(100, score))


def get_signal(conviction):
    if conviction >= 70:
        return "BUY"
    if conviction >= 50:
        return "WATCH"
    return "AVOID"


def build_reasons(total_return, alpha, win_rate, max_drawdown, profit_factor):
    reasons = []

    if total_return > 0:
        reasons.append("Strategy profitable in backtest")

    if alpha > 0:
        reasons.append("Outperformed buy & hold")

    if win_rate >= 50:
        reasons.append("Healthy win rate")

    if max_drawdown < 15:
        reasons.append("Controlled drawdown")

    if profit_factor > 1:
        reasons.append("Positive profit factor")

    if not reasons:
        reasons.append("Weak technical/backtest profile")

    return reasons