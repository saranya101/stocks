import { useEffect, useState } from "react";
import API from "../api/api";

function ControlField({ label, help, children }) {
  return (
    <div className="control-field">
      <div className="control-label">
        <span>{label}</span>
        <span className="tooltip" title={help}>?</span>
      </div>
      {children}
      <p className="control-help">{help}</p>
    </div>
  );
}

function Dashboard() {
  const [tickers, setTickers] = useState("AAPL,GOOGL,NVDA,MSFT,TSLA,AMZN,META,SPY,QQQ");
  const [fast, setFast] = useState(5);
  const [slow, setSlow] = useState(30);
  const [rsiSell, setRsiSell] = useState(70);
  const [stopLoss, setStopLoss] = useState(0.03);

  const [trendWeight, setTrendWeight] = useState(15);
  const [momentumWeight, setMomentumWeight] = useState(10);
  const [backtestWeight, setBacktestWeight] = useState(15);
  const [riskPenalty, setRiskPenalty] = useState(15);
  const [winRateWeight, setWinRateWeight] = useState(10);
  const [rsiDangerLevel, setRsiDangerLevel] = useState(80);
  const [maxDrawdownAllowed, setMaxDrawdownAllowed] = useState(20);

  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);

  function loadOpportunities() {
    setLoading(true);

    API.get(
      `/ai-opportunities?tickers=${tickers}&fast=${fast}&slow=${slow}&rsi_sell=${rsiSell}&stop_loss=${stopLoss}&trend_weight=${trendWeight}&momentum_weight=${momentumWeight}&backtest_weight=${backtestWeight}&risk_penalty=${riskPenalty}&win_rate_weight=${winRateWeight}&rsi_danger_level=${rsiDangerLevel}&max_drawdown_allowed=${maxDrawdownAllowed}`
    )
      .then((response) => {
        setOpportunities(response.data.top_opportunities);
        setLoading(false);
      })
      .catch((error) => {
        console.error(error);
        setLoading(false);
      });
  }

  useEffect(() => {
    loadOpportunities();
  }, []);

  const veryBullish = opportunities.filter((s) => s.signal === "VERY BULLISH");
  const bullish = opportunities.filter((s) => s.signal === "BULLISH");
  const bearish = opportunities.filter((s) => s.signal.includes("BEARISH"));
  const best = opportunities[0];

  return (
    <div className="command-page">
      <section className="command-hero">
        <div>
          <p className="eyebrow">AI MARKET INTELLIGENCE</p>
          <h1>Command Center</h1>
          <p className="hero-subtitle">
            Custom watchlist scanning, confidence scoring, risk filtering, and backtest-backed trade intelligence.
          </p>
        </div>

        {best && (
          <div className="hero-best">
            <p>Top Opportunity</p>
            <h2>{best.ticker}</h2>
            <span className={best.signal.includes("BULLISH") ? "bullish" : "bearish"}>
              {best.signal} · {best.confidence}/100
            </span>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Scan Configuration</h2>

        <div className="control-grid">
          <ControlField label="Watchlist" help="The stocks the AI should scan. Separate tickers with commas.">
            <input value={tickers} onChange={(e) => setTickers(e.target.value.toUpperCase())} />
          </ControlField>

          <ControlField label="Fast Trend SMA" help="Short-term trend sensitivity. Lower = reacts faster.">
            <input type="number" value={fast} onChange={(e) => setFast(e.target.value)} />
          </ControlField>

          <ControlField label="Slow Trend SMA" help="Longer-term trend confirmation. Higher = smoother signals.">
            <input type="number" value={slow} onChange={(e) => setSlow(e.target.value)} />
          </ControlField>

          <ControlField label="RSI Exit Level" help="RSI level where the strategy treats a stock as overheated.">
            <input type="number" value={rsiSell} onChange={(e) => setRsiSell(e.target.value)} />
          </ControlField>

          <ControlField label="Stop Loss" help="Maximum allowed loss per trade before forced exit. 0.03 = 3%.">
            <input type="number" step="0.01" value={stopLoss} onChange={(e) => setStopLoss(e.target.value)} />
          </ControlField>
        </div>

        <h2 style={{ marginTop: 28 }}>AI Brain Weights</h2>

        <div className="control-grid">
          <ControlField label="Trend Importance" help="How much bullish/bearish trend affects confidence.">
            <input type="number" value={trendWeight} onChange={(e) => setTrendWeight(e.target.value)} />
          </ControlField>

          <ControlField label="Momentum Importance" help="How much RSI/momentum health affects confidence.">
            <input type="number" value={momentumWeight} onChange={(e) => setMomentumWeight(e.target.value)} />
          </ControlField>

          <ControlField label="Backtest Importance" help="How much historical strategy performance affects confidence.">
            <input type="number" value={backtestWeight} onChange={(e) => setBacktestWeight(e.target.value)} />
          </ControlField>

          <ControlField label="Risk Penalty" help="How strongly the AI punishes overbought RSI and high drawdown.">
            <input type="number" value={riskPenalty} onChange={(e) => setRiskPenalty(e.target.value)} />
          </ControlField>

          <ControlField label="Win Rate Importance" help="How much winning consistency affects confidence.">
            <input type="number" value={winRateWeight} onChange={(e) => setWinRateWeight(e.target.value)} />
          </ControlField>

          <ControlField label="RSI Danger Level" help="Above this RSI, the AI treats the stock as overextended.">
            <input type="number" value={rsiDangerLevel} onChange={(e) => setRsiDangerLevel(e.target.value)} />
          </ControlField>

          <ControlField label="Max Drawdown Allowed" help="Above this drawdown, the AI increases risk warning.">
            <input type="number" value={maxDrawdownAllowed} onChange={(e) => setMaxDrawdownAllowed(e.target.value)} />
          </ControlField>
        </div>

        <button className="primary-action" onClick={loadOpportunities}>
          {loading ? "Scanning..." : "Run AI Market Scan"}
        </button>
      </section>

      <div className="metric-row">
        <div className="metric"><p>Very Bullish</p><h2 className="bullish">{veryBullish.length}</h2></div>
        <div className="metric"><p>Bullish</p><h2 className="bullish">{bullish.length}</h2></div>
        <div className="metric"><p>Bearish</p><h2 className="bearish">{bearish.length}</h2></div>
        <div className="metric"><p>Analyzed</p><h2>{opportunities.length}</h2></div>
      </div>

      <section className="opportunity-grid">
        {opportunities.map((stock) => (
          <div className="opportunity-card" key={stock.ticker}>
            <div className="opportunity-top">
              <div>
                <p className="ticker-label">Ticker</p>
                <h2>{stock.ticker}</h2>
              </div>
              <div className="confidence-score">{stock.confidence}/100</div>
            </div>

            <h3 className={stock.signal.includes("BULLISH") ? "bullish" : stock.signal.includes("BEARISH") ? "bearish" : "warning"}>
              {stock.signal}
            </h3>

            <div className="confidence-bar">
              <div className="confidence-fill" style={{ width: `${stock.confidence}%` }} />
            </div>

            <div className="stats-grid">
              <p>Price <strong>${stock.price.toFixed(2)}</strong></p>
              <p>Risk <strong>{stock.risk_level}</strong></p>
              <p>RSI <strong>{stock.rsi.toFixed(2)}</strong></p>
              <p>Backtest <strong>{stock.backtest_return.toFixed(2)}%</strong></p>
              <p>Drawdown <strong>{stock.max_drawdown.toFixed(2)}%</strong></p>
              <p>Win Rate <strong>{stock.win_rate.toFixed(2)}%</strong></p>
            </div>

            <div className="reason-list">
              {stock.reasons.map((reason, index) => (
                <span className="pill" key={index}>{reason}</span>
              ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

export default Dashboard;