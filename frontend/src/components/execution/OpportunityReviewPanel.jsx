import StockChart from "../StockChart";
import ReviewPriceChart from "./ReviewPriceChart";
import DecisionMemo from "./DecisionMemo";
import API from "../../api/api";

function getReasoning(trade) {
  const conviction = Number(trade.conviction || 0);
  const technical = Number(trade.technical_score || 0);
  const backtest = Number(trade.backtest_score || 0);
  const volume = Number(trade.volume_score || 0);
  const rsi = Number(trade.rsi || 0);

  const strengthLabel =
    conviction >= 80
      ? "high-conviction"
      : conviction >= 70
        ? "strong"
        : "watchlist-quality";

  return `${trade.ticker} is currently classified as a ${strengthLabel} setup because price action, momentum, and volume are aligned.

The technical score is ${technical}/100, suggesting the trend structure is supportive. Backtest quality is ${backtest}/100, which means the strategy has shown acceptable historical behaviour for this setup. Volume confirmation is ${volume}/100, helping validate that the move is not purely random.

RSI is currently ${rsi.toFixed(1)}, which gives context on momentum. The planned setup offers a ${trade.risk_reward}:1 risk/reward profile, with an expected hold period of ${trade.expected_hold_days} days.

This does not mean “buy blindly”. It means QuantOS has identified the trade as worth review, with defined entry, stop, target, and position sizing before execution.`;
}

export default function OpportunityReviewPanel({ trade, market = "us" }) {
  if (!trade) return null;
  async function createTradePlan() {
    try {
      const res = await API.post("/trade-plans", {
        market,
        trade,
      });

      alert(`Trade plan created for ${res.data.ticker}`);
    } catch (err) {
      console.error(err);
      alert("Failed to create trade plan.");
    }
  }
  return (
    <section className="opportunity-review-card">
      <div className="review-header">
        <div>
          <p className="eyebrow">OPPORTUNITY REVIEW</p>
          <h2>{trade.ticker}</h2>

          <p className="company-name">{trade.company_name || trade.ticker}</p>

          <div className="company-meta">
            {trade.direction && <span>{trade.direction}</span>}
            {trade.industry && <span>{trade.industry}</span>}
            {trade.sector && <span>{trade.sector}</span>}
            {trade.market_cap && <span>{trade.market_cap}</span>}
            {trade.grade && <span>Grade {trade.grade}</span>}
          </div>

          <div className="company-links">
            {trade.yahoo_url && (
              <a href={trade.yahoo_url} target="_blank" rel="noreferrer">
                Yahoo Finance →
              </a>
            )}

            {trade.website && (
              <a href={trade.website} target="_blank" rel="noreferrer">
                Company Website →
              </a>
            )}
          </div>

          <div className="review-tags">
            <span>{trade.recommendation}</span>
            <span>{trade.direction}</span>
            <span>Grade {trade.grade}</span>
          </div>
        </div>

        <div className="review-conviction">
          <small>Conviction</small>
          <strong>{trade.conviction}</strong>
        </div>
      </div>
      <ReviewPriceChart
        ticker={trade.ticker}
        entry={trade.entry_price}
        target={trade.take_profit}
        stop={trade.stop_loss}
      />
      <DecisionMemo trade={trade} />

      <div className="review-grid">
        <div className="review-section review-thesis">
          <h3>Why QuantOS Likes This</h3>

          <p className="thesis-summary">
            {trade.ticker} ranks highly because multiple signals are aligned
            instead of relying on one indicator.
          </p>

          {(trade.reasons || []).map((reason, index) => (
            <div key={index} className="review-reason">
              <span>✓</span>
              <p>{reason}</p>
            </div>
          ))}
        </div>

        <div className="review-section">
          <h3>Technical Intelligence</h3>

          <div className="metric-row">
            <span>Technical Score</span>
            <strong>{trade.technical_score}</strong>
          </div>

          <div className="metric-row">
            <span>Backtest Score</span>
            <strong>{trade.backtest_score}</strong>
          </div>

          <div className="metric-row">
            <span>Volume Score</span>
            <strong>{trade.volume_score}</strong>
          </div>

          <div className="metric-row">
            <span>RSI</span>
            <strong>{trade.rsi}</strong>
          </div>
        </div>

        <div className="review-section">
          <h3>Trade Plan</h3>

          <div className="metric-row">
            <span>Entry</span>
            <strong>${trade.entry_price}</strong>
          </div>

          <div className="metric-row">
            <span>Stop</span>
            <strong>${trade.stop_loss}</strong>
          </div>

          <div className="metric-row">
            <span>Target</span>
            <strong>${trade.take_profit}</strong>
          </div>

          <div className="metric-row">
            <span>Risk Reward</span>
            <strong>{trade.risk_reward}:1</strong>
          </div>
        </div>

        <div className="review-section">
          <h3>AI Reasoning</h3>

          <p className="reasoning-text">{getReasoning(trade)}</p>
        </div>
      </div>

      <div className="review-actions">
        <button className="approve-btn" onClick={createTradePlan}>
          Create Trade Plan
        </button>

        <button className="watch-btn">Watchlist</button>

        <button className="reject-btn">Reject</button>
      </div>
    </section>
  );
}
