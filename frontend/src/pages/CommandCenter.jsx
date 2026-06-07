import API from "../api/api";
import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from "recharts";

function CommandCenter() {
  const [watchlist, setWatchlist] = useState([]);
  const [newTicker, setNewTicker] = useState("");
  const [newsModalOpen, setNewsModalOpen] = useState(false);

  const [universe, setUniverse] = useState("us_largecap");
  const [scanLimit, setScanLimit] = useState(50);
  const [scanMode, setScanMode] = useState("fast");
  const [fast, setFast] = useState(5);
  const [slow, setSlow] = useState(30);
  const [rsiSell, setRsiSell] = useState(70);
  const [stopLoss, setStopLoss] = useState(0.03);

  const [opportunities, setOpportunities] = useState([]);
  const [selected, setSelected] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [chartPeriod, setChartPeriod] = useState("1mo");
  const [loading, setLoading] = useState(false);

  const [scanStatus, setScanStatus] = useState({
    running: false,
    current: "",
    completed: 0,
    total: 0,
  });

  const firstClose = chartData[0]?.close || 0;
  const lastClose = chartData[chartData.length - 1]?.close || 0;
  const chartChange = firstClose ? lastClose - firstClose : 0;
  const chartChangePct = firstClose ? (chartChange / firstClose) * 100 : 0;

  const scanPercent =
    scanStatus.total > 0 ? (scanStatus.completed / scanStatus.total) * 100 : 0;

  function loadWatchlist() {
    API.get("/watchlist").then((res) => {
      setWatchlist(res.data.watchlist || []);
    });
  }

  function loadChart(ticker, period = chartPeriod) {
    API.get(`/stock-chart/${ticker}?period=${period}`).then((res) => {
      setChartData(res.data.prices || []);
    });
  }

  function addTicker(tickerValue = newTicker) {
    if (!tickerValue.trim()) return;

    API.post(`/watchlist/add?ticker=${tickerValue.toUpperCase()}`).then(() => {
      setNewTicker("");
      loadWatchlist();
    });
  }

  function removeTicker(ticker) {
    API.delete(`/watchlist/remove/${ticker}`).then(() => {
      loadWatchlist();
    });
  }

  function selectStock(stock) {
    setSelected(stock);
    loadChart(stock.ticker);
  }

  function selectWatchlistTicker(ticker) {
    const savedResult = opportunities.find((stock) => stock.ticker === ticker);

    if (savedResult) {
      selectStock(savedResult);
      return;
    }

    setSelected({
      ticker,
      signal: "WATCHLIST",
      confidence: 0,
      risk_level: "UNKNOWN",
      price: 0,
      rsi: 0,
      backtest_return: 0,
      max_drawdown: 0,
      win_rate: 0,
      news_label: "NOT SCANNED",
      reasons: [],
      news_articles: [],
    });

    loadChart(ticker);
  }

  async function runScan() {
    setLoading(true);

    try {
      let tickers = watchlist;

      if (universe !== "watchlist") {
        const universeRes = await API.get(
          `/universe?universe=${universe}&limit=${scanLimit}`,
        );

        tickers = universeRes.data.tickers || [];
      }

      if (tickers.length === 0) {
        alert("No tickers available.");
        setLoading(false);
        return;
      }

      const res = await API.get(
        `/ai-opportunities?tickers=${tickers.join(",")}&fast=${fast}&slow=${slow}&rsi_sell=${rsiSell}&stop_loss=${stopLoss}&scan_mode=${scanMode}`,
      );

      const data = res.data.top_opportunities || [];
      setOpportunities(data);

      if (data.length > 0) {
        selectStock(data[0]);
      }
    } catch (err) {
      console.error(err);
      alert("Scan failed.");
    }

    setLoading(false);
  }

  useEffect(() => {
    API.get("/settings")
      .then((res) => {
        const s = res.data;

        setUniverse(s.universe || "us_largecap");
        setScanMode(s.scanMode || "fast");
        setScanLimit(s.scanLimit || 50);
        setFast(s.fast || 5);
        setSlow(s.slow || 30);
        setRsiSell(s.rsiSell || 70);
        setStopLoss(s.stopLoss || 0.03);
      })
      .catch(console.error);

    loadWatchlist();

    API.get("/latest-market-scan")
      .then((res) => {
        const data = res.data.opportunities || [];
        setOpportunities(data);

        if (data.length > 0) {
          selectStock(data[0]);
        }
      })
      .catch(console.error);

    const statusInterval = setInterval(async () => {
      try {
        const res = await API.get("/scan-status");
        setScanStatus(res.data);
      } catch (err) {
        console.error(err);
      }
    }, 1000);

    return () => clearInterval(statusInterval);
  }, []);

  const topPick = opportunities[0];

  return (
    <div className="dashboard-page">
      <section className="dashboard-hero">
        <div>
          <p className="eyebrow">QUANTOS</p>
          <h1>My Investments</h1>
          <p className="muted">
            Your watchlist, strongest signals, and AI-discovered opportunities
            in one clean view.
          </p>
        </div>

        <div className="hero-stats">
          <div>
            <span>Watchlist</span>
            <strong>{watchlist.length}</strong>
          </div>

          <div>
            <span>Top Pick</span>
            <strong>{topPick?.ticker || "—"}</strong>
          </div>

          <div>
            <span>AI Score</span>
            <strong>{topPick?.confidence || 0}/100</strong>
          </div>
        </div>
      </section>

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">WATCHLIST</p>
            <h2>Stocks You Track</h2>
          </div>

          <div className="ticker-add-row compact-add">
            <input
              value={newTicker}
              placeholder="AAPL"
              onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
            />
            <button onClick={() => addTicker()}>Add</button>
          </div>
        </div>

        <div className="watchlist-grid">
          {watchlist.map((ticker) => {
            const data = opportunities.find((item) => item.ticker === ticker);

            return (
              <button
                className={`watchlist-card ${
                  selected?.ticker === ticker ? "active" : ""
                }`}
                key={ticker}
                onClick={() => selectWatchlistTicker(ticker)}
              >
                <div>
                  <strong>{ticker}</strong>
                  <p>{data?.signal || "Not scanned"}</p>
                </div>

                <div>
                  <span>
                    {data?.confidence ? `${data.confidence}/100` : "—"}
                  </span>
                  <small>{data?.risk_level || "Watchlist"}</small>
                </div>

                <button
                  className="remove-watch"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeTicker(ticker);
                  }}
                >
                  ×
                </button>
              </button>
            );
          })}
        </div>
      </section>

      <section className="dashboard-card">
        {selected ? (
          <>
            <div className="detail-hero">
              <div>
                <p className="eyebrow">SELECTED STOCK</p>
                <h1>{selected.ticker}</h1>
                <h3
                  className={
                    selected.signal.includes("BULLISH")
                      ? "bullish"
                      : selected.signal.includes("BEARISH")
                        ? "bearish"
                        : "warning"
                  }
                >
                  {selected.signal}
                </h3>
              </div>

              <div className="big-score">
                {selected.confidence}
                <span>/100</span>
              </div>
            </div>

            <div className="terminal-card">
              <div className="chart-header">
                <div>
                  <h3>Price Chart</h3>
                  <p className={chartChange >= 0 ? "chart-gain" : "chart-loss"}>
                    {chartChange >= 0 ? "+" : ""}${chartChange.toFixed(2)} ·{" "}
                    {chartChangePct.toFixed(2)}%
                  </p>
                </div>

                <div className="chart-tabs">
                  {["5d", "1mo", "3mo", "6mo", "1y"].map((period) => (
                    <button
                      key={period}
                      className={chartPeriod === period ? "active" : ""}
                      onClick={() => {
                        setChartPeriod(period);
                        loadChart(selected.ticker, period);
                      }}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>

              <div className="chart-box">
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="date" hide />
                    <YAxis domain={["auto", "auto"]} hide />
                    <RechartsTooltip
                      contentStyle={{
                        background: "#020617",
                        border: "1px solid rgba(148,163,184,.2)",
                        borderRadius: "12px",
                        color: "#e5e7eb",
                      }}
                      formatter={(value, name) => [
                        `$${Number(value).toFixed(2)}`,
                        name.toUpperCase(),
                      ]}
                    />
                    <Line
                      type="monotone"
                      dataKey="close"
                      stroke={chartChange >= 0 ? "#22c55e" : "#ef4444"}
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="sma20"
                      stroke="#60a5fa"
                      strokeWidth={1.6}
                      dot={false}
                      connectNulls
                    />
                    <Line
                      type="monotone"
                      dataKey="sma50"
                      stroke="#f59e0b"
                      strokeWidth={1.6}
                      dot={false}
                      connectNulls
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="terminal-stats">
              <div>
                <p>Price</p>
                <strong>${selected.price.toFixed(2)}</strong>
              </div>
              <div>
                <p>RSI</p>
                <strong>{selected.rsi.toFixed(2)}</strong>
              </div>
              <div>
                <p>Backtest</p>
                <strong>{selected.backtest_return.toFixed(2)}%</strong>
              </div>
              <div>
                <p>Drawdown</p>
                <strong>{selected.max_drawdown.toFixed(2)}%</strong>
              </div>
              <div>
                <p>Win Rate</p>
                <strong>{selected.win_rate.toFixed(2)}%</strong>
              </div>
              <div
                className="clickable-stat"
                onClick={() => setNewsModalOpen(true)}
              >
                <p>News</p>
                <strong>{selected.news_label || "NEUTRAL"}</strong>
                <small>View catalyst details</small>
              </div>
            </div>
          </>
        ) : (
          <p className="muted">Select a stock to view analysis.</p>
        )}
      </section>

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <p className="eyebrow">DISCOVER</p>
            <h2>AI Suggested Opportunities</h2>
          </div>

          <button className="small-primary" onClick={runScan}>
            {loading ? "Scanning..." : "Run Discovery"}
          </button>
        </div>

        {scanStatus.running && (
          <div className="scan-progress-card">
            <div className="scan-progress-header">
              <strong>Scanning Market</strong>
              <span>
                {scanStatus.completed}/{scanStatus.total}
              </span>
            </div>

            <div className="scan-progress-bar">
              <div
                className="scan-progress-fill"
                style={{ width: `${scanPercent}%` }}
              />
            </div>

            <p className="scan-current">
              Currently analyzing: {scanStatus.current}
            </p>
          </div>
        )}

        <div className="discover-grid">
          {opportunities.map((stock, index) => {
            const alreadyAdded = watchlist.includes(stock.ticker);

            return (
              <button
                key={stock.ticker}
                className={`discover-card ${
                  selected?.ticker === stock.ticker ? "active" : ""
                }`}
                onClick={() => selectStock(stock)}
              >
                <span className="rank-badge">#{index + 1}</span>

                <div>
                  <strong>{stock.ticker}</strong>
                  <p>{stock.signal}</p>
                </div>

                <div className="discover-score">
                  <span>{stock.confidence}/100</span>
                  <small>{stock.risk_level} risk</small>
                </div>

                {!alreadyAdded && (
                  <button
                    className="add-watch"
                    onClick={(e) => {
                      e.stopPropagation();
                      addTicker(stock.ticker);
                    }}
                  >
                    Add
                  </button>
                )}
              </button>
            );
          })}
        </div>
      </section>
      {newsModalOpen && selected && (
  <div className="modal-backdrop" onClick={() => setNewsModalOpen(false)}>
    <div className="news-modal" onClick={(e) => e.stopPropagation()}>
      <div className="modal-header">
        <div>
          <p className="eyebrow">NEWS INTELLIGENCE</p>
          <h2>{selected.ticker}</h2>
        </div>

        <button onClick={() => setNewsModalOpen(false)}>×</button>
      </div>

      <div className="news-summary">
        <div>
          <span>Label</span>
          <strong>{selected.news_label || "NEUTRAL"}</strong>
        </div>

        <div>
          <span>News Score</span>
          <strong>{selected.news_score?.toFixed(2) || 0}</strong>
        </div>

        <div>
          <span>Confidence</span>
          <strong>{selected.news_confidence || 0}%</strong>
        </div>
      </div>

      {selected.news_articles?.length > 0 ? (
        <div className="news-modal-list">
          {selected.news_articles.map((article, index) => (
            <div className="news-modal-item" key={index}>
              <div className="news-modal-item-header">
                <div>
                  <h3>{article.title}</h3>
                  <p>
                    {article.source} · {article.event_type} ·{" "}
                    {article.trade_relevance}
                  </p>
                </div>

                <span>
                  {article.ai_weighted_impact
                    ? `${article.ai_weighted_impact > 0 ? "+" : ""}${article.ai_weighted_impact}`
                    : article.ai_impact_score || 0}
                </span>
              </div>

              <p className="news-reason">{article.ai_reason}</p>

              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noreferrer"
                  className="article-link"
                >
                  Open original article →
                </a>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">
          No high-confidence article details were found for this scan.
        </p>
      )}
    </div>
  </div>
)}
    </div>
  );
}

export default CommandCenter;
