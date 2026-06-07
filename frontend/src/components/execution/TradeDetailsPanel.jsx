function money(value) {
  return value || value === 0 ? `$${Number(value).toFixed(2)}` : "—";
}

export default function TradeDetailsPanel({ trade }) {
  if (!trade) return null;

  const recommendationClass = trade.recommendation
    ?.toLowerCase()
    .replaceAll(" ", "-");

  return (
    <section className="trade-command-card">
      <div className="trade-command-header">
        <div>
          <p className="eyebrow">SELECTED TRADE</p>
          <h1>{trade.ticker}</h1>

          <div className="trade-badges">
            <span className={`trade-badge ${recommendationClass}`}>
              {trade.recommendation || "WATCH"}
            </span>

            <span className="trade-badge muted-badge">
              {trade.direction || "—"}
            </span>

            <span className="trade-badge grade-badge">
              Grade {trade.grade || "—"}
            </span>
          </div>
        </div>

        <div className="conviction-block">
          <span>Conviction</span>
          <strong>{trade.conviction ?? "—"}</strong>
          <small>/100</small>
        </div>
      </div>

      <div className="trade-setup-panel">
        <div className="setup-main">
          <p>Trade Setup</p>

          <div className="setup-row">
            <span>Entry</span>
            <strong>{money(trade.entry_price)}</strong>
          </div>

          <div className="setup-row">
            <span>Stop Loss</span>
            <strong>{money(trade.stop_loss)}</strong>
          </div>

          <div className="setup-row">
            <span>Target</span>
            <strong>{money(trade.take_profit)}</strong>
          </div>
        </div>

        <div className="setup-side">
          <div>
            <span>Risk / Reward</span>
            <strong>{trade.risk_reward ?? "—"}</strong>
          </div>

          <div>
            <span>Expected Hold</span>
            <strong>
              {trade.expected_hold_days ? `${trade.expected_hold_days}d` : "—"}
            </strong>
          </div>

          <div>
            <span>Position</span>
            <strong>{money(trade.position_value)}</strong>
          </div>

          <div>
            <span>Shares</span>
            <strong>{trade.shares ?? "—"}</strong>
          </div>
        </div>
      </div>

      <div className="trade-reasons">
        <h3>Why This Trade</h3>

        <div className="reasons-list">
          {(trade.reasons || []).map((reason, index) => (
            <div key={index} className="reason-item">
              <span>✓</span>
              <p>{reason}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}