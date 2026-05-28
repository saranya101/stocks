def run_portfolio_backtest(
    ticker_results,
    starting_cash=10000
):
    portfolio_results = []
    equity_curves = []
    total_final_value = 0

    for item in ticker_results:
        ticker = item["ticker"]
        weight = item["weight"]
        backtest = item["backtest"]

        allocated_cash = starting_cash * weight

        backtest_starting_cash = backtest["starting_cash"]
        return_multiplier = backtest["final_value"] / backtest_starting_cash
        allocated_final_value = allocated_cash * return_multiplier

        total_final_value += allocated_final_value
        equity_curves.append({
            "weight": weight,
            "starting_cash": backtest_starting_cash,
            "curve": backtest["equity_curve"]
        })

        portfolio_results.append({
            "ticker": ticker,
            "weight": weight,
            "allocated_cash": allocated_cash,
            "final_value": allocated_final_value,
            "total_return": ((allocated_final_value - allocated_cash) / allocated_cash) * 100,
            "max_drawdown": backtest["max_drawdown"],
            "win_rate": backtest["win_rate"],
            "total_trades": backtest["total_trades"]
        })

    portfolio_return = ((total_final_value - starting_cash) / starting_cash) * 100

    average_drawdown = sum(
        item["max_drawdown"] for item in portfolio_results
    ) / len(portfolio_results)

    average_win_rate = sum(
        item["win_rate"] for item in portfolio_results
    ) / len(portfolio_results)

    common_dates = None
    curve_by_date = []

    for item in equity_curves:
        dates = {point["date"] for point in item["curve"]}

        if common_dates is None:
            common_dates = dates
        else:
            common_dates = common_dates.intersection(dates)

        curve_by_date.append({
            point["date"]: point["value"]
            for point in item["curve"]
        })

    equity_curve = []

    if common_dates:
        ordered_dates = [
            point["date"]
            for point in equity_curves[0]["curve"]
            if point["date"] in common_dates
        ]

        for date in ordered_dates:
            portfolio_value = 0

            for index, item in enumerate(equity_curves):
                allocated_cash = starting_cash * item["weight"]
                value = curve_by_date[index][date]
                scaled_value = (
                    value / item["starting_cash"]
                ) * allocated_cash
                portfolio_value += scaled_value

            equity_curve.append({
                "date": date,
                "value": portfolio_value
            })

    return {
        "starting_cash": starting_cash,
        "final_value": total_final_value,
        "portfolio_return": portfolio_return,
        "average_drawdown": average_drawdown,
        "average_win_rate": average_win_rate,
        "positions": portfolio_results,
        "equity_curve": equity_curve
    }
