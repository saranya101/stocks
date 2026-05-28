import { useState } from "react";
import API from "../api/api";

function TopPerformers() {
  const [limit, setLimit] = useState(50);

  const [fast, setFast] = useState(5);
  const [slow, setSlow] = useState(30);
  const [rsiSell, setRsiSell] = useState(70);
  const [stopLoss, setStopLoss] = useState(0.03);

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  function runScan() {
    setLoading(true);

    API.get(
      `/top-performers?limit=${limit}&fast=${fast}&slow=${slow}&rsi_sell=${rsiSell}&stop_loss=${stopLoss}`
    )
      .then((response) => {
        setResults(response.data.top_performers);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }

  return (
    <div style={{ padding: "30px" }}>
      <h1>Top Performers</h1>

      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        <input
          type="number"
          value={limit}
          onChange={(e) => setLimit(e.target.value)}
          placeholder="Stocks to scan"
        />

        <input
          type="number"
          value={fast}
          onChange={(e) => setFast(e.target.value)}
          placeholder="Fast SMA"
        />

        <input
          type="number"
          value={slow}
          onChange={(e) => setSlow(e.target.value)}
          placeholder="Slow SMA"
        />

        <input
          type="number"
          value={rsiSell}
          onChange={(e) => setRsiSell(e.target.value)}
          placeholder="RSI Sell"
        />

        <input
          type="number"
          step="0.01"
          value={stopLoss}
          onChange={(e) => setStopLoss(e.target.value)}
          placeholder="Stop Loss"
        />

        <button onClick={runScan}>
          Run Scan
        </button>
      </div>

      <br />

      {loading && <h2>Scanning market...</h2>}

      {results.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Return</th>
              <th>Drawdown</th>
              <th>Win Rate</th>
              <th>Trades</th>
            </tr>
          </thead>

          <tbody>
            {results.map((stock) => (
              <tr key={stock.ticker}>
                <td>{stock.ticker}</td>
                <td>{stock.total_return.toFixed(2)}%</td>
                <td>{stock.max_drawdown.toFixed(2)}%</td>
                <td>{stock.win_rate.toFixed(2)}%</td>
                <td>{stock.total_trades}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default TopPerformers;