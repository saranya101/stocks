import { useState } from "react";
import API from "../api/api";
import PortfolioChart from "../components/PortfolioChart";

function App() {
  const [tickers, setTickers] = useState("AAPL,GOOGL,SPY,QQQ");
  const [weights, setWeights] = useState("0.4,0.3,0.2,0.1");
  const [fast, setFast] = useState(5);
  const [slow, setSlow] = useState(30);
  const [rsiSell, setRsiSell] = useState(70);
  const [stopLoss, setStopLoss] = useState(0.03);
  const [startingCash, setStartingCash] = useState(10000);

  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(false);

  function runPortfolioBacktest() {
    setLoading(true);
    setPortfolio(null);

    API.get(
      `/portfolio-backtest?tickers=${tickers}&weights=${weights}&fast=${fast}&slow=${slow}&rsi_sell=${rsiSell}&stop_loss=${stopLoss}&starting_cash=${startingCash}`
    )
      .then((response) => {
        setPortfolio(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>AI Quant Portfolio Backtester</h1>

      <div>
        <label>Tickers</label>
        <br />
        <input
          value={tickers}
          onChange={(e) => setTickers(e.target.value.toUpperCase())}
          style={{ width: "400px", padding: "8px" }}
        />
      </div>

      <br />

      <div>
        <label>Weights</label>
        <br />
        <input
          value={weights}
          onChange={(e) => setWeights(e.target.value)}
          style={{ width: "400px", padding: "8px" }}
        />
      </div>

      <br />

      <div>
        <label>Fast SMA</label>
        <br />
        <input
          type="number"
          value={fast}
          onChange={(e) => setFast(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>Slow SMA</label>
        <br />
        <input
          type="number"
          value={slow}
          onChange={(e) => setSlow(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>RSI Sell</label>
        <br />
        <input
          type="number"
          value={rsiSell}
          onChange={(e) => setRsiSell(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>Stop Loss</label>
        <br />
        <input
          type="number"
          step="0.01"
          value={stopLoss}
          onChange={(e) => setStopLoss(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>Starting Cash</label>
        <br />
        <input
          type="number"
          value={startingCash}
          onChange={(e) => setStartingCash(e.target.value)}
        />
      </div>

      <br />

      <button onClick={runPortfolioBacktest}>
        Run Portfolio Backtest
      </button>

      {loading && <h2>Running backtest...</h2>}

      {portfolio && (
        <div>
          <h2>Portfolio Result</h2>

          <p>Final Value: ${portfolio.final_value.toFixed(2)}</p>
          <p>Portfolio Return: {portfolio.portfolio_return.toFixed(2)}%</p>
          <p>Average Drawdown: {portfolio.average_drawdown.toFixed(2)}%</p>
          <p>Average Win Rate: {portfolio.average_win_rate.toFixed(2)}%</p>
          {portfolio.risk_metrics && (
          <div>
            <h3>Portfolio Equity Curve</h3>
            <PortfolioChart data={portfolio.equity_curve} />
            <h3>Risk Metrics</h3>

            <p>Sharpe Ratio: {portfolio.risk_metrics.sharpe.toFixed(2)}</p>
            <p>Sortino Ratio: {portfolio.risk_metrics.sortino.toFixed(2)}</p>
            <p>Calmar Ratio: {portfolio.risk_metrics.calmar.toFixed(2)}</p>
          </div>
        )}

          <h3>Positions</h3>

          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Allocated Cash</th>
                <th>Final Value</th>
                <th>Return</th>
                <th>Drawdown</th>
                <th>Win Rate</th>
                <th>Trades</th>
              </tr>
            </thead>

            <tbody>
              {portfolio.positions.map((position) => (
                <tr key={position.ticker}>
                  <td>{position.ticker}</td>
                  <td>${position.allocated_cash.toFixed(2)}</td>
                  <td>${position.final_value.toFixed(2)}</td>
                  <td>{position.total_return.toFixed(2)}%</td>
                  <td>{position.max_drawdown.toFixed(2)}%</td>
                  <td>{position.win_rate.toFixed(2)}%</td>
                  <td>{position.total_trades}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;