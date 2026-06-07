import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";
import API from "../api/api";
import "./Backtest.css";

function formatDate(date) {
  return String(date).split(" ")[0];
}

function formatMoney(value) {
  return `$${Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
}
function formatPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function buildPositionTradePairs(trades = []) {
  const pairs = [];

  for (let i = 0; i < trades.length - 1; i++) {
    const buy = trades[i];
    const sell = trades[i + 1];

    if (buy.type === "BUY" && sell.type === "SELL") {
      pairs.push({
        buyDate: buy.date,
        buyPrice: buy.price,
        sellDate: sell.date,
        sellPrice: sell.price,
        reason: sell.reason || "SIGNAL EXIT",
        returnPct: ((sell.price - buy.price) / buy.price) * 100,
      });
    }
  }

  return pairs;
}

function buildTradePairs(trades = []) {
  const pairs = [];

  for (let i = 0; i < trades.length - 1; i++) {
    const buy = trades[i];
    const sell = trades[i + 1];

    if (buy.type === "BUY" && sell.type === "SELL") {
      const buyDate = new Date(buy.date);
      const sellDate = new Date(sell.date);

      const daysHeld = Math.max(
        1,
        Math.round((sellDate - buyDate) / (1000 * 60 * 60 * 24)),
      );

      pairs.push({
        buyDate: buy.date,
        sellDate: sell.date,
        buyPrice: buy.price,
        sellPrice: sell.price,
        reason: sell.reason || "SIGNAL EXIT",
        daysHeld,
        returnPct: ((sell.price - buy.price) / buy.price) * 100,
      });
    }
  }

  return pairs;
}

function buildPortfolioTrades(positions = []) {
  const rows = [];

  positions.forEach((position) => {
    const trades = position.trades || [];

    trades.forEach((trade) => {
      rows.push({
        ticker: position.ticker,
        weight: position.weight,
        ...trade,
      });
    });
  });

  return rows.sort((a, b) => new Date(a.date) - new Date(b.date));
}

function MetricCard({ label, value }) {
  return (
    <div className="bt-metric-card">
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  );
}

function FieldLabel({ children, tooltip }) {
  return (
    <label className="hover-label">
      {children}
      <span className="hover-label-popover">{tooltip}</span>
    </label>
  );
}

function Backtest() {
  const [activeTab, setActiveTab] = useState("single");
  const [compareTicker, setCompareTicker] = useState("AAPL");
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [heatmapData, setHeatmapData] = useState(null);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  const [portfolioTickers, setPortfolioTickers] = useState(
    "AAPL,MSFT,NVDA,GOOGL",
  );
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2026-01-01");
  const [portfolioWeights, setPortfolioWeights] = useState(
    "0.25,0.25,0.25,0.25",
  );
  const [portfolioData, setPortfolioData] = useState(null);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [selectedTradeTicker, setSelectedTradeTicker] = useState(null);

  const [compareStrategies, setCompareStrategies] = useState([
    {
      name: "Strategy A",
      fast: "20",
      slow: "50",
      rsi_sell: "80",
      stop_loss: "0.05",
    },
    {
      name: "Strategy B",
      fast: "10",
      slow: "30",
      rsi_sell: "75",
      stop_loss: "0.03",
    },
  ]);
  function updateCompareStrategy(index, field, value) {
    setCompareStrategies((prev) =>
      prev.map((strategy, i) =>
        i === index ? { ...strategy, [field]: value } : strategy,
      ),
    );
  }

  const [ticker, setTicker] = useState("AAPL");
  const [useGlobalSettings, setUseGlobalSettings] = useState(true);
  const sortedCompareResults = useMemo(() => {
    return [...(compareData?.results || [])].sort(
      (a, b) => b.total_return - a.total_return,
    );
  }, [compareData]);

  const compareWinner = sortedCompareResults[0];
  const compareRunnerUp = sortedCompareResults[1];

  const compareChartData = useMemo(() => {
    if (!sortedCompareResults.length) return [];

    const strategyA = sortedCompareResults[0];
    const strategyB = sortedCompareResults[1];

    const strategyBByDate = {};
    (strategyB?.equity_curve || []).forEach((point) => {
      strategyBByDate[formatDate(point.date)] = point.value;
    });

    return (strategyA?.equity_curve || []).map((point) => {
      const date = formatDate(point.date);

      return {
        date,
        strategyA: point.value,
        strategyB: strategyBByDate[date] || null,
      };
    });
  }, [sortedCompareResults]);
  const heatmapMatrix = useMemo(() => {
    const results = heatmapData?.results || [];

    const fastValues = [...new Set(results.map((r) => r.strategy.fast))].sort(
      (a, b) => a - b,
    );

    const slowValues = [...new Set(results.map((r) => r.strategy.slow))].sort(
      (a, b) => a - b,
    );

    const matrix = fastValues.map((fast) => {
      const row = { fast };

      slowValues.forEach((slow) => {
        const match = results.find(
          (r) => r.strategy.fast === fast && r.strategy.slow === slow,
        );

        row[slow] = match ? match.total_return : null;
      });

      return row;
    });

    return { fastValues, slowValues, matrix };
  }, [heatmapData]);

  function getHeatmapCellClass(value) {
    if (value === null || value === undefined) return "bt-heatmap-empty";
    if (value >= 30) return "bt-heatmap-strong";
    if (value >= 10) return "bt-heatmap-good";
    if (value >= 0) return "bt-heatmap-flat";
    return "bt-heatmap-bad";
  }

  function getStrategyScore(item) {
    const alpha = Number(item.alpha || 0);
    const winRate = Number(item.win_rate || 0);
    const profitFactor = Number(item.profit_factor || 0);
    const drawdown = Number(item.max_drawdown || 0);

    return (
      alpha * 0.4 + winRate * 0.2 + profitFactor * 10 * 0.3 - drawdown * 0.1
    );
  }
  const [fast, setFast] = useState("20");
  const [slow, setSlow] = useState("50");
  const [rsiSell, setRsiSell] = useState("80");
  const [stopLoss, setStopLoss] = useState("0.05");

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const tradePairs = useMemo(() => buildTradePairs(data?.trades), [data]);
  const portfolioTrades = useMemo(
    () => buildPortfolioTrades(portfolioData?.positions || []),
    [portfolioData],
  );
  const portfolioChartData = useMemo(() => {
    if (!portfolioData?.equity_curve) return [];

    const buyHoldByDate = {};

    (portfolioData.buy_hold_curve || []).forEach((point) => {
      buyHoldByDate[formatDate(point.date)] = point.value;
    });

    const result = portfolioData.equity_curve.map((point) => {
      const date = formatDate(point.date);

      return {
        date,
        value: point.value,
        buyHold: buyHoldByDate[date] || null,
      };
    });

    console.log("PORTFOLIO CHART DATA", result.slice(0, 10));

    return result;
  }, [portfolioData]);

  const portfolioTradeMarkers = useMemo(() => {
    if (!portfolioData?.equity_curve || !portfolioData?.positions) return [];

    const valueByDate = {};
    portfolioData.equity_curve.forEach((point) => {
      valueByDate[formatDate(point.date)] = point.value;
    });

    const markers = [];

    portfolioData.positions.forEach((position) => {
      (position.trades || []).forEach((trade) => {
        const date = formatDate(trade.date);

        if (valueByDate[date]) {
          markers.push({
            date,
            value: valueByDate[date],
            type: trade.type,
            ticker: position.ticker,
          });
        }
      });
    });

    return markers;
  }, [portfolioData]);
  const selectedPosition = useMemo(() => {
    if (!selectedTradeTicker) return null;

    return portfolioData?.positions?.find(
      (position) => position.ticker === selectedTradeTicker,
    );
  }, [selectedTradeTicker, portfolioData]);
  const selectedTradePairs = useMemo(() => {
    if (!selectedPosition) return [];

    return buildPositionTradePairs(selectedPosition.trades || []);
  }, [selectedPosition]);
  const chartData = useMemo(() => {
    if (!data?.equity_curve) return [];

    return data.equity_curve.map((point, index) => ({
      date: formatDate(point.date),
      strategy: point.value,
      buyHold: data.buy_hold_curve?.[index]?.value || null,
    }));
  }, [data]);

  const exitStats = useMemo(() => {
    const stats = {};

    tradePairs.forEach((trade) => {
      const reason = trade.reason || "UNKNOWN";

      if (!stats[reason]) {
        stats[reason] = {
          count: 0,
          totalReturn: 0,
        };
      }

      stats[reason].count += 1;
      stats[reason].totalReturn += trade.returnPct;
    });

    return Object.entries(stats).map(([reason, value]) => ({
      reason,
      count: value.count,
      avgReturn: value.totalReturn / value.count,
    }));
  }, [tradePairs]);

  const tradeStats = useMemo(() => {
    const winners = tradePairs.filter((t) => t.returnPct > 0);
    const losers = tradePairs.filter((t) => t.returnPct < 0);

    const totalWins = winners.reduce((sum, t) => sum + t.returnPct, 0);
    const totalLosses = Math.abs(
      losers.reduce((sum, t) => sum + t.returnPct, 0),
    );

    return {
      avgWinner: winners.length ? totalWins / winners.length : 0,
      avgLoser: losers.length ? totalLosses / losers.length : 0,
      profitFactor: totalLosses ? totalWins / totalLosses : totalWins,
    };
  }, [tradePairs]);

  useEffect(() => {
    API.get("/settings")
      .then((res) => {
        const s = res.data;

        setFast(String(s.fast || 20));
        setSlow(String(s.slow || 50));
        setRsiSell(String(s.rsiSell || 80));
        setStopLoss(String(s.stopLoss || 0.05));
      })
      .catch(console.error);
  }, []);

  async function runBacktest() {
    if (!ticker.trim()) return;

    const fastValue = parseInt(fast);
    const slowValue = parseInt(slow);
    const rsiValue = parseInt(rsiSell);
    const stopValue = parseFloat(stopLoss);

    if (
      Number.isNaN(fastValue) ||
      Number.isNaN(slowValue) ||
      Number.isNaN(rsiValue) ||
      Number.isNaN(stopValue)
    ) {
      alert("Please fill in all strategy settings correctly.");
      return;
    }

    setLoading(true);

    try {
      const query = new URLSearchParams({
        fast: fastValue,

        slow: slowValue,

        rsi_sell: rsiValue,

        stop_loss: stopValue,

        start_date: startDate,

        end_date: endDate,
      });

      const res = await API.get(
        `/backtest/${ticker.toUpperCase()}?${query.toString()}`,
      );

      if (res.data?.error) {
        alert(res.data.error);
        setData(null);
      } else {
        setData(res.data);
      }
    } catch (err) {
      console.error(err);
      alert("Backtest failed.");
    }

    setLoading(false);
  }

  async function runPortfolioBacktest() {
    if (!portfolioTickers.trim()) return;

    const fastValue = parseInt(fast);
    const slowValue = parseInt(slow);
    const rsiValue = parseInt(rsiSell);
    const stopValue = parseFloat(stopLoss);

    setPortfolioLoading(true);

    try {
      const res = await API.get(
        `/portfolio-backtest?tickers=${portfolioTickers}&weights=${portfolioWeights}&fast=${fastValue}&slow=${slowValue}&rsi_sell=${rsiValue}&stop_loss=${stopValue}`,
      );
      console.log("PORTFOLIO DATA:", res.data);
      console.log("POSITIONS:", res.data.positions);

      if (res.data?.error) {
        alert(res.data.error);
        setPortfolioData(null);
      } else {
        setPortfolioData(res.data);
      }
    } catch (err) {
      console.error(err);
      alert("Portfolio backtest failed.");
    }

    setPortfolioLoading(false);
  }
  async function runHeatmap() {
    if (!compareTicker.trim()) return;

    setHeatmapLoading(true);

    try {
      const res = await API.get(
        `/backtest-heatmap/${compareTicker.toUpperCase()}`,
      );

      if (res.data?.error) {
        alert(res.data.error);
        setHeatmapData(null);
      } else {
        setHeatmapData(res.data);
      }
    } catch (err) {
      console.error(err);
      alert("Heatmap failed.");
    }

    setHeatmapLoading(false);
  }
  async function runStrategyCompare() {
    if (!compareTicker.trim()) return;

    setCompareLoading(true);

    try {
      const query = new URLSearchParams({
        strategies: JSON.stringify(compareStrategies),
      });

      const res = await API.get(
        `/backtest-compare/${compareTicker.toUpperCase()}?${query.toString()}`,
      );

      if (res.data?.error) {
        alert(res.data.error);
        setCompareData(null);
      } else {
        setCompareData(res.data);
      }
    } catch (err) {
      console.error(err);
      alert("Strategy comparison failed.");
    }

    setCompareLoading(false);
  }

  return (
    <div className="backtest-page">
      <section className="bt-hero">
        <div>
          <p className="eyebrow">QUANTOS RESEARCH</p>
          <h1>Backtesting Lab</h1>
          <p className="muted">
            Test whether your strategy would have worked before trusting it with
            real money.
          </p>
        </div>

        {activeTab === "single" && (
          <button className="bt-run-btn" onClick={runBacktest}>
            {loading ? "Running..." : "Run Backtest"}
          </button>
        )}
      </section>

      <div className="bt-tabs">
        <button
          className={activeTab === "single" ? "active" : ""}
          onClick={() => setActiveTab("single")}
        >
          Single Stock
        </button>

        <button
          className={activeTab === "portfolio" ? "active" : ""}
          onClick={() => setActiveTab("portfolio")}
        >
          Portfolio
        </button>
        <button
          className={activeTab === "compare" ? "active" : ""}
          onClick={() => setActiveTab("compare")}
        >
          Strategy Compare
        </button>
      </div>
      {activeTab === "compare" && (
        <>
          <section className="bt-card">
            <div className="bt-section-header">
              <div>
                <p className="eyebrow">STRATEGY LAB</p>
                <h2>Strategy Comparison</h2>
                <p className="muted">
                  Compare different SMA / RSI / Stop Loss combinations on the
                  same stock.
                </p>
              </div>

              <div className="bt-action-row">
                <button className="bt-run-btn" onClick={runStrategyCompare}>
                  {compareLoading ? "Running..." : "Compare Strategies"}
                </button>

                <button
                  className="bt-run-btn bt-secondary-btn"
                  onClick={runHeatmap}
                >
                  {heatmapLoading ? "Running..." : "Run Heatmap"}
                </button>
              </div>
            </div>

            <div className="bt-config-grid">
              <div>
                <label>Ticker</label>
                <input
                  value={compareTicker}
                  onChange={(e) =>
                    setCompareTicker(e.target.value.toUpperCase())
                  }
                  placeholder="AAPL"
                />
              </div>
            </div>

            <div className="bt-compare-strategy-grid">
              {compareStrategies.map((strategy, index) => (
                <div className="bt-compare-strategy-card" key={index}>
                  <h3>{strategy.name}</h3>

                  <label>Name</label>
                  <input
                    value={strategy.name}
                    onChange={(e) =>
                      updateCompareStrategy(index, "name", e.target.value)
                    }
                  />

                  <label>Fast SMA</label>
                  <input
                    value={strategy.fast}
                    onChange={(e) =>
                      updateCompareStrategy(index, "fast", e.target.value)
                    }
                  />

                  <label>Slow SMA</label>
                  <input
                    value={strategy.slow}
                    onChange={(e) =>
                      updateCompareStrategy(index, "slow", e.target.value)
                    }
                  />

                  <label>RSI Exit</label>
                  <input
                    value={strategy.rsi_sell}
                    onChange={(e) =>
                      updateCompareStrategy(index, "rsi_sell", e.target.value)
                    }
                  />

                  <label>Stop Loss</label>
                  <input
                    value={strategy.stop_loss}
                    onChange={(e) =>
                      updateCompareStrategy(index, "stop_loss", e.target.value)
                    }
                  />
                </div>
              ))}
            </div>
          </section>

          {compareData && (
            <section className="bt-card">
              <div className="bt-section-header">
                <div>
                  <p className="eyebrow">RESULTS</p>
                  <h2>{compareData.ticker} Strategy Rankings</h2>
                </div>
              </div>
              {compareWinner && compareRunnerUp && (
                <div className="bt-verdict-card">
                  <h3>Winner: {compareWinner.name || "Strategy 1"}</h3>

                  <p className="bt-positive">
                    ✓ {compareWinner.name} returned{" "}
                    {compareWinner.total_return.toFixed(2)}%, compared to{" "}
                    {compareRunnerUp.name} at{" "}
                    {compareRunnerUp.total_return.toFixed(2)}%.
                  </p>

                  <p>
                    Drawdown: {compareWinner.max_drawdown.toFixed(2)}% vs{" "}
                    {compareRunnerUp.max_drawdown.toFixed(2)}%.
                  </p>
                </div>
              )}

              <div className="bt-section-header bt-compare-header">
                <div>
                  <p className="eyebrow">EQUITY CURVE</p>

                  <h2>Strategy A vs Strategy B Growth</h2>
                </div>
              </div>

              <div className="bt-chart-box">
                <ResponsiveContainer width="100%" height={360}>
                  <LineChart data={compareChartData}>
                    <XAxis dataKey="date" hide />

                    <YAxis domain={["auto", "auto"]} hide />

                    <Tooltip
                      contentStyle={{
                        background: "#020617",

                        border: "1px solid rgba(148,163,184,.2)",

                        borderRadius: "12px",

                        color: "#e5e7eb",
                      }}
                      formatter={(value, name) => [formatMoney(value), name]}
                    />

                    <Line
                      type="monotone"
                      dataKey="strategyA"
                      name={sortedCompareResults[0]?.name || "Strategy A"}
                      stroke="#22c55e"
                      strokeWidth={2.4}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="strategyB"
                      name={sortedCompareResults[1]?.name || "Strategy B"}
                      stroke="#60a5fa"
                      strokeWidth={2.4}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bt-table-wrap">
                <table className="bt-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Score</th>
                      <th>Fast SMA</th>
                      <th>Slow SMA</th>
                      <th>RSI Exit</th>
                      <th>Stop Loss</th>
                      <th>Total Return</th>
                      <th>Profit Factor</th>
                      <th>Drawdown</th>
                      <th>Win Rate</th>
                      <th>Avg Hold</th>
                      <th>Trades</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sortedCompareResults.slice(0, 2).map((item, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>{getStrategyScore(item).toFixed(1)}</td>

                        <td>{item.strategy.fast}</td>
                        <td>{item.strategy.slow}</td>
                        <td>{item.strategy.rsi_sell}</td>
                        <td>{(item.strategy.stop_loss * 100).toFixed(0)}%</td>
                        <td
                          className={
                            item.total_return >= 0
                              ? "bt-positive"
                              : "bt-negative"
                          }
                        >
                          {item.total_return.toFixed(2)}%
                        </td>
                        <td>{Number(item.profit_factor || 0).toFixed(2)}</td>
                        <td>{item.max_drawdown.toFixed(2)}%</td>
                        <td>{item.win_rate.toFixed(1)}%</td>
                        <td>
                          {Number(item.average_days_held || 0).toFixed(1)} days
                        </td>
                        <td>{item.total_trades}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="bt-section-header bt-compare-header">
                <div>
                  <p className="eyebrow">SIDE BY SIDE</p>
                  <h2>Strategy Comparison Matrix</h2>
                </div>
              </div>

              <div className="bt-table-wrap">
                <table className="bt-table bt-comparison-table">
                  <thead>
                    <tr>
                      <th>Metric</th>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <th key={index}>
                          {item.name || `Strategy ${index + 1}`}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    <tr>
                      <td>Total Return</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td
                          key={index}
                          className={
                            item.total_return >= 0
                              ? "bt-positive"
                              : "bt-negative"
                          }
                        >
                          {formatPercent(item.total_return)}
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Buy & Hold</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index}>
                          {formatPercent(item.buy_hold_return)}
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Alpha</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td
                          key={index}
                          className={
                            item.alpha >= 0 ? "bt-positive" : "bt-negative"
                          }
                        >
                          {formatPercent(item.alpha)}
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Max Drawdown</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index}>{formatPercent(item.max_drawdown)}</td>
                      ))}
                    </tr>

                    <tr>
                      <td>Win Rate</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index}>{formatPercent(item.win_rate)}</td>
                      ))}
                    </tr>
                    <tr>
                      <td>Profit Factor</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index}>
                          {Number(item.profit_factor || 0).toFixed(2)}
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Avg Days Held</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index}>
                          {Number(item.average_days_held || 0).toFixed(1)} days
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Largest Win</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index} className="bt-positive">
                          {formatPercent(item.largest_win)}
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Largest Loss</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index} className="bt-negative">
                          {formatPercent(item.largest_loss)}
                        </td>
                      ))}
                    </tr>

                    <tr>
                      <td>Total Trades</td>
                      {sortedCompareResults.slice(0, 2).map((item, index) => (
                        <td key={index}>{item.total_trades}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>
          )}
          {heatmapData && (
            <section className="bt-card">
              <div className="bt-section-header">
                <div>
                  <p className="eyebrow">ROBUSTNESS TEST</p>
                  <h2>{heatmapData.ticker} Parameter Sensitivity Heatmap</h2>
                  <p className="muted">
                    Shows whether the strategy works across many SMA
                    combinations or only one lucky setting.
                  </p>
                </div>
              </div>

              <div className="bt-table-wrap">
                <table className="bt-table bt-heatmap-table">
                  <thead>
                    <tr>
                      <th>Fast \ Slow</th>
                      {heatmapMatrix.slowValues.map((slow) => (
                        <th key={slow}>{slow}</th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {heatmapMatrix.matrix.map((row) => (
                      <tr key={row.fast}>
                        <td>{row.fast}</td>

                        {heatmapMatrix.slowValues.map((slow) => {
                          const value = row[slow];

                          return (
                            <td
                              key={slow}
                              className={getHeatmapCellClass(value)}
                            >
                              {value === null || value === undefined
                                ? "-"
                                : `${value.toFixed(1)}%`}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
      {activeTab === "single" && (
        <>
          <section className="bt-card">
            <div className="bt-config-grid">
              <div>
                <label>Ticker</label>
                <input
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  placeholder="AAPL"
                />
              </div>
              <div>
                <label>Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>

              <div>
                <label>End Date</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>

              <div className="bt-toggle-wrap">
                <label>Settings Mode</label>
                <button
                  className={
                    useGlobalSettings ? "bt-toggle active" : "bt-toggle"
                  }
                  onClick={() => setUseGlobalSettings(!useGlobalSettings)}
                >
                  {useGlobalSettings
                    ? "Using Global Settings"
                    : "Custom Settings"}
                </button>
              </div>

              <div>
                <FieldLabel tooltip="The short-term moving average. Lower values react faster but can create more false signals.">
                  Fast SMA
                </FieldLabel>
                <input
                  disabled={useGlobalSettings}
                  value={fast}
                  onChange={(e) => setFast(e.target.value)}
                />
              </div>

              <div>
                <FieldLabel tooltip="The long-term moving average. The strategy compares Fast SMA against this to identify trend direction.">
                  Slow SMA
                </FieldLabel>
                <input
                  disabled={useGlobalSettings}
                  value={slow}
                  onChange={(e) => setSlow(e.target.value)}
                />
              </div>

              <div>
                <FieldLabel tooltip="The RSI level where the strategy exits a trade. Higher values usually let trades run longer.">
                  RSI Exit
                </FieldLabel>
                <input
                  disabled={useGlobalSettings}
                  value={rsiSell}
                  onChange={(e) => setRsiSell(e.target.value)}
                />
              </div>

              <div>
                <FieldLabel tooltip="The maximum loss allowed before selling. 0.03 means a 3% stop loss.">
                  Stop Loss
                </FieldLabel>
                <input
                  disabled={useGlobalSettings}
                  type="text"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(e.target.value)}
                  placeholder="0.03"
                />
              </div>
            </div>
          </section>

          {data && (
            <>
              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">RESULTS</p>
                    <h2>{data.ticker} Strategy Performance</h2>
                  </div>

                  <span className="bt-strategy-pill">
                    {data.strategy.fast_sma} SMA / {data.strategy.slow_sma} SMA
                    · RSI {data.strategy.rsi_sell} · Stop{" "}
                    {(data.strategy.stop_loss * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="bt-metrics-grid">
                  <MetricCard
                    label="Total Return"
                    value={`${data.total_return.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Buy & Hold"
                    value={`${data.buy_hold_return.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Alpha"
                    value={`${data.alpha.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Final Value"
                    value={formatMoney(data.final_value)}
                  />

                  <MetricCard
                    label="Win Rate"
                    value={`${data.win_rate.toFixed(1)}%`}
                  />

                  <MetricCard
                    label="Max Drawdown"
                    value={`${data.max_drawdown.toFixed(1)}%`}
                  />

                  <MetricCard label="Trades" value={data.total_trades} />

                  <MetricCard
                    label="Starting Cash"
                    value={formatMoney(data.starting_cash)}
                  />

                  <MetricCard
                    label="Profit Factor"
                    value={tradeStats.profitFactor.toFixed(2)}
                  />

                  <MetricCard
                    label="Avg Winner"
                    value={`${tradeStats.avgWinner.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Avg Loser"
                    value={`-${tradeStats.avgLoser.toFixed(2)}%`}
                  />
                </div>

                <div className="bt-verdict-card">
                  <h3>Strategy Verdict</h3>

                  {data.alpha > 0 ? (
                    <p className="bt-positive">
                      ✓ This strategy outperformed Buy & Hold by{" "}
                      {data.alpha.toFixed(2)}%.
                    </p>
                  ) : (
                    <p className="bt-negative">
                      ✗ This strategy underperformed Buy & Hold by{" "}
                      {Math.abs(data.alpha).toFixed(2)}%.
                    </p>
                  )}

                  <p>
                    Profit Factor: {tradeStats.profitFactor.toFixed(2)}
                    {tradeStats.profitFactor > 1.5
                      ? " (Strong)"
                      : tradeStats.profitFactor > 1
                        ? " (Profitable)"
                        : " (Weak)"}
                  </p>

                  <p>
                    Max Drawdown: {data.max_drawdown.toFixed(1)}%
                    {data.max_drawdown < 10
                      ? " (Low Risk)"
                      : data.max_drawdown < 20
                        ? " (Moderate Risk)"
                        : " (High Risk)"}
                  </p>
                </div>
              </section>

              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">EQUITY CURVE</p>
                    <h2>Portfolio Growth</h2>
                  </div>
                </div>

                <div className="bt-chart-box">
                  <ResponsiveContainer width="100%" height={360}>
                    <LineChart data={chartData}>
                      <XAxis dataKey="date" hide />
                      <YAxis domain={["auto", "auto"]} hide />
                      <Tooltip
                        contentStyle={{
                          background: "#020617",
                          border: "1px solid rgba(148,163,184,.2)",
                          borderRadius: "12px",
                          color: "#e5e7eb",
                        }}
                        formatter={(value, name) => [formatMoney(value), name]}
                      />

                      <Line
                        type="monotone"
                        dataKey="strategy"
                        name="Strategy"
                        stroke="#22c55e"
                        strokeWidth={2.4}
                        dot={false}
                      />

                      <Line
                        type="monotone"
                        dataKey="buyHold"
                        name="Buy & Hold"
                        stroke="#60a5fa"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">EXIT ANALYSIS</p>
                    <h2>Why Trades Closed</h2>
                  </div>
                </div>

                <div className="bt-exit-grid">
                  {exitStats.map((item) => (
                    <div className="bt-exit-card" key={item.reason}>
                      <p>{item.reason}</p>
                      <strong>{item.count} trades </strong>
                      <span
                        className={
                          item.avgReturn >= 0 ? "bt-positive" : "bt-negative"
                        }
                      >
                        Avg Return {item.avgReturn.toFixed(2)}%
                      </span>
                    </div>
                  ))}
                </div>
              </section>

              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">TRADES</p>
                    <h2>Trade History</h2>
                  </div>
                </div>

                <div className="bt-table-wrap">
                  <table className="bt-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Buy Date</th>
                        <th>Buy Price</th>
                        <th>Sell Date</th>
                        <th>Sell Price</th>
                        <th>Days</th>
                        <th>Return</th>
                        <th>Exit Reason</th>
                      </tr>
                    </thead>

                    <tbody>
                      {tradePairs.map((trade, index) => (
                        <tr key={index}>
                          <td>{index + 1}</td>
                          <td>{formatDate(trade.buyDate)}</td>
                          <td>${trade.buyPrice.toFixed(2)}</td>
                          <td>{formatDate(trade.sellDate)}</td>
                          <td>${trade.sellPrice.toFixed(2)}</td>
                          <td>{trade.daysHeld}</td>
                          <td
                            className={
                              trade.returnPct >= 0
                                ? "bt-positive"
                                : "bt-negative"
                            }
                          >
                            {trade.returnPct.toFixed(2)}%
                          </td>
                          <td>{trade.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">TIMELINE</p>
                    <h2>Trade Journey</h2>
                  </div>
                </div>

                <div className="bt-timeline">
                  {tradePairs.map((trade, index) => (
                    <div className="bt-trade-card" key={index}>
                      <div>
                        <span className="bt-buy">BUY</span>
                        <strong>${trade.buyPrice.toFixed(2)}</strong>
                        <p>{formatDate(trade.buyDate)}</p>
                      </div>

                      <div className="bt-arrow">→</div>

                      <div>
                        <span className="bt-sell">SELL</span>
                        <strong>${trade.sellPrice.toFixed(2)}</strong>
                        <p>{formatDate(trade.sellDate)}</p>
                      </div>

                      <div>
                        <span
                          className={
                            trade.returnPct >= 0 ? "bt-positive" : "bt-negative"
                          }
                        >
                          {trade.returnPct.toFixed(2)}%
                        </span>
                        <p>{trade.reason}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </>
      )}

      {activeTab === "portfolio" && (
        <>
          <section className="bt-card">
            <div className="bt-section-header">
              <div>
                <p className="eyebrow">PORTFOLIO TEST</p>
                <h2>Portfolio Backtest</h2>
                <p className="muted">
                  Test the same strategy across a basket of stocks with custom
                  weights.
                </p>
              </div>

              <button className="bt-run-btn" onClick={runPortfolioBacktest}>
                {portfolioLoading ? "Running..." : "Run Portfolio"}
              </button>
            </div>

            <div className="bt-config-grid">
              <div>
                <FieldLabel tooltip="Comma-separated list of tickers to include in the portfolio.">
                  Tickers
                </FieldLabel>
                <input
                  value={portfolioTickers}
                  onChange={(e) =>
                    setPortfolioTickers(e.target.value.toUpperCase())
                  }
                  placeholder="AAPL,MSFT,NVDA,GOOGL"
                />
              </div>

              <div>
                <FieldLabel tooltip="Comma-separated weights. They must add up to 1. Example: 0.25,0.25,0.25,0.25">
                  Weights
                </FieldLabel>
                <input
                  value={portfolioWeights}
                  onChange={(e) => setPortfolioWeights(e.target.value)}
                  placeholder="0.25,0.25,0.25,0.25"
                />
              </div>

              <div>
                <FieldLabel tooltip="The short-term moving average used across all tickers.">
                  Fast SMA
                </FieldLabel>
                <input value={fast} onChange={(e) => setFast(e.target.value)} />
              </div>

              <div>
                <FieldLabel tooltip="The long-term moving average used across all tickers.">
                  Slow SMA
                </FieldLabel>
                <input value={slow} onChange={(e) => setSlow(e.target.value)} />
              </div>

              <div>
                <FieldLabel tooltip="The RSI level where each stock strategy exits.">
                  RSI Exit
                </FieldLabel>
                <input
                  value={rsiSell}
                  onChange={(e) => setRsiSell(e.target.value)}
                />
              </div>

              <div>
                <FieldLabel tooltip="Maximum loss per stock before exiting. 0.03 means 3%.">
                  Stop Loss
                </FieldLabel>
                <input
                  value={stopLoss}
                  onChange={(e) => setStopLoss(e.target.value)}
                />
              </div>
            </div>
          </section>

          {portfolioData && (
            <>
              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">PORTFOLIO RESULTS</p>
                    <h2>Portfolio Performance</h2>
                  </div>
                </div>

                <div className="bt-metrics-grid">
                  <MetricCard
                    label="Final Value"
                    value={formatMoney(portfolioData.final_value ?? 0)}
                  />

                  <MetricCard
                    label="Total Return"
                    value={`${portfolioData.portfolio_return.toFixed(2)}%`}
                  />
                  <MetricCard
                    label="Buy & Hold"
                    value={`${portfolioData.buy_hold_return.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Alpha"
                    value={`${portfolioData.alpha.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Average Drawdown"
                    value={`${portfolioData.average_drawdown.toFixed(2)}%`}
                  />

                  <MetricCard
                    label="Average Win Rate"
                    value={`${portfolioData.average_win_rate.toFixed(1)}%`}
                  />

                  <MetricCard
                    label="Sharpe Ratio"
                    value={portfolioData.risk_metrics.sharpe.toFixed(2)}
                  />

                  <MetricCard
                    label="Sortino Ratio"
                    value={portfolioData.risk_metrics.sortino.toFixed(2)}
                  />

                  <MetricCard
                    label="Calmar Ratio"
                    value={portfolioData.risk_metrics.calmar.toFixed(2)}
                  />
                </div>
                <div className="bt-verdict-card">
                  <h3>Portfolio Verdict</h3>

                  {portfolioData.alpha > 0 ? (
                    <p className="bt-positive">
                      ✓ Strategy outperformed Buy & Hold by{" "}
                      {portfolioData.alpha.toFixed(2)}%.
                    </p>
                  ) : (
                    <p className="bt-negative">
                      ✗ Strategy underperformed Buy & Hold by{" "}
                      {Math.abs(portfolioData.alpha).toFixed(2)}%.
                    </p>
                  )}

                  <p>
                    Sharpe Ratio: {portfolioData.risk_metrics.sharpe.toFixed(2)}
                    {portfolioData.risk_metrics.sharpe >= 1.5
                      ? " (Strong risk-adjusted return)"
                      : portfolioData.risk_metrics.sharpe >= 1
                        ? " (Good)"
                        : " (Weak)"}
                  </p>
                </div>
              </section>

              <section className="bt-card">
                <div className="bt-section-header">
                  <div>
                    <p className="eyebrow">PORTFOLIO CURVE</p>
                    <h2>Portfolio Growth</h2>
                  </div>
                </div>
                <section className="bt-card">
                  <div className="bt-section-header">
                    <div>
                      <p className="eyebrow">HOLDINGS</p>
                      <h2>Portfolio Breakdown</h2>
                    </div>
                  </div>

                  <div className="bt-table-wrap">
                    <table className="bt-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Ticker</th>
                          <th>Weight</th>
                          <th>Allocated Cash</th>
                          <th>Final Value</th>
                          <th>Total Return</th>
                          <th>Drawdown</th>
                          <th>Win Rate</th>
                          <th>Trades</th>
                        </tr>
                      </thead>

                      <tbody>
                        {(portfolioData.positions || []).map(
                          (position, index) => (
                            <tr key={position.ticker}>
                              <td>{index + 1}</td>
                              <td>{position.ticker}</td>
                              <td>
                                {((position.weight || 0) * 100).toFixed(0)}%
                              </td>
                              <td>{formatMoney(position.allocated_cash)}</td>
                              <td>{formatMoney(position.final_value)}</td>
                              <td
                                className={
                                  position.total_return >= 0
                                    ? "bt-positive"
                                    : "bt-negative"
                                }
                              >
                                {position.total_return.toFixed(2)}%
                              </td>
                              <td>
                                {position.max_drawdown?.toFixed(2) ?? "0.00"}%
                              </td>
                              <td>{position.win_rate?.toFixed(1) ?? "0.0"}%</td>
                              <td>{position.total_trades ?? 0}</td>
                            </tr>
                          ),
                        )}
                      </tbody>
                    </table>
                  </div>
                </section>
                <section className="bt-card">
                  <div className="bt-section-header">
                    <div>
                      <p className="eyebrow">PORTFOLIO TRADES</p>
                      <h2>Trades by Stock</h2>
                    </div>
                  </div>

                  <div className="bt-exit-grid">
                    {(portfolioData.positions || []).map((position) => (
                      <button
                        className="bt-exit-card bt-clickable-card"
                        key={position.ticker}
                        onClick={() => setSelectedTradeTicker(position.ticker)}
                      >
                        <p>{position.ticker}</p>
                        <strong>{position.total_trades} trades </strong>
                        <span
                          className={
                            position.total_return >= 0
                              ? "bt-positive"
                              : "bt-negative"
                          }
                        >
                          {position.total_return.toFixed(2)}% return
                        </span>
                      </button>
                    ))}
                  </div>
                </section>
                <div className="bt-chart-legend">
                  <span>
                    <i className="bt-legend-dot bt-legend-green"></i>
                    Strategy Portfolio
                  </span>

                  <span>
                    <i className="bt-legend-dot bt-legend-blue"></i>
                    Buy & Hold Portfolio
                  </span>
                  <span>
                    <i className="bt-legend-dot bt-legend-green"></i>
                    Buy Trade
                  </span>

                  <span>
                    <i className="bt-legend-dot bt-legend-red"></i>
                    Sell Trade
                  </span>
                </div>
                <div className="bt-chart-box">
                  <ResponsiveContainer width="100%" height={360}>
                    <LineChart data={portfolioChartData}>
                      <XAxis dataKey="date" hide />
                      <YAxis domain={["auto", "auto"]} hide />
                      <Tooltip
                        contentStyle={{
                          background: "#020617",
                          border: "1px solid rgba(148,163,184,.2)",
                          borderRadius: "12px",
                          color: "#e5e7eb",
                        }}
                        formatter={(value) => [formatMoney(value), "Portfolio"]}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        name="Portfolio"
                        stroke="#22c55e"
                        strokeWidth={2.4}
                        dot={false}
                      />
                      <Line
                        type="monotone"
                        dataKey="buyHold"
                        name="Buy & Hold"
                        stroke="#60a5fa"
                        strokeWidth={2}
                        dot={false}
                      />
                      {portfolioTradeMarkers.map((marker, index) => (
                        <ReferenceDot
                          key={`${marker.ticker}-${marker.date}-${index}`}
                          x={marker.date}
                          y={marker.value}
                          r={4}
                          fill={marker.type === "BUY" ? "#22c55e" : "#ef4444"}
                          stroke="none"
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>
            </>
          )}
        </>
      )}
      {selectedPosition && (
        <div
          className="bt-modal-backdrop"
          onClick={() => setSelectedTradeTicker(null)}
        >
          <div className="bt-modal" onClick={(e) => e.stopPropagation()}>
            <div className="bt-modal-header">
              <div>
                <p className="eyebrow">TRADE DETAILS</p>
                <h2>{selectedPosition.ticker} Trades </h2>
              </div>

              <button
                className="bt-modal-close"
                onClick={() => setSelectedTradeTicker(null)}
              >
                ×
              </button>
            </div>
            <div className="bt-metrics-grid bt-modal-metrics">
              <MetricCard
                label="Return"
                value={`${selectedPosition.total_return.toFixed(2)}%`}
              />

              <MetricCard
                label="Win Rate"
                value={`${selectedPosition.win_rate.toFixed(1)}%`}
              />

              <MetricCard
                label="Max Drawdown"
                value={`${selectedPosition.max_drawdown.toFixed(2)}%`}
              />

              <MetricCard
                label="Completed Trades"
                value={selectedTradePairs.length}
              />
            </div>

            <div className="bt-table-wrap">
              <table className="bt-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Buy Date</th>
                    <th>Buy Price</th>
                    <th>Sell Date</th>
                    <th>Sell Price</th>
                    <th>Return</th>
                    <th>Exit Reason</th>
                  </tr>
                </thead>

                <tbody>
                  {selectedTradePairs.map((trade, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>

                      <td>{formatDate(trade.buyDate)}</td>

                      <td>${Number(trade.buyPrice).toFixed(2)}</td>

                      <td>{formatDate(trade.sellDate)}</td>

                      <td>${Number(trade.sellPrice).toFixed(2)}</td>

                      <td
                        className={
                          trade.returnPct >= 0 ? "bt-positive" : "bt-negative"
                        }
                      >
                        {trade.returnPct.toFixed(2)}%
                      </td>

                      <td>{trade.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Backtest;
