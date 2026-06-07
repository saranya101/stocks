function money(value) {
  return value || value === 0 ? `$${Number(value).toFixed(2)}` : "—";
}

function pct(value) {
  return value || value === 0 ? `${Number(value).toFixed(1)}%` : "—";
}

function getStrength(conviction) {
  if (conviction >= 82) return "institutional-quality";
  if (conviction >= 72) return "high-quality";
  if (conviction >= 60) return "watchlist-worthy";
  return "low-conviction";
}

export default function DecisionMemo({ trade }) {
  if (!trade) return null;

  const conviction = Number(trade.conviction || 0);
  const technical = Number(trade.technical_score || 0);
  const backtest = Number(trade.backtest_score || 0);
  const volume = Number(trade.volume_score || 0);
  const news = Number(trade.news_score || 0);

  return (
    <section className="decision-memo">
      <div className="memo-header">
        <div>
          <p className="eyebrow">QUANTOS DECISION MEMO</p>
          <h3>{trade.ticker} Trade Review</h3>
        </div>

        <span className="memo-pill">{trade.recommendation}</span>
      </div>

      <p className="memo-summary">
        QuantOS classifies {trade.ticker} as a{" "}
        <strong>{getStrength(conviction)}</strong> setup with a conviction score
        of <strong>{conviction}/100</strong>. The setup is supported by technical
        strength, backtest quality, volume confirmation, and a defined risk plan.
      </p>

      <div className="memo-grid">
        <div>
          <span>Entry Zone</span>
          <strong>{money(trade.entry_price)}</strong>
        </div>

        <div>
          <span>Stop Loss</span>
          <strong>{money(trade.stop_loss)}</strong>
        </div>

        <div>
          <span>Target</span>
          <strong>{money(trade.take_profit)}</strong>
        </div>

        <div>
          <span>Risk Reward</span>
          <strong>{trade.risk_reward}:1</strong>
        </div>
      </div>

      <div className="memo-section">
        <h4>Why this setup is ranked</h4>

        <ul>
          <li>
            Technical score is <strong>{technical}/100</strong>, showing the
            current trend structure is favourable.
          </li>
          <li>
            Backtest score is <strong>{backtest}/100</strong>, giving historical
            support to the setup quality.
          </li>
          <li>
            Volume score is <strong>{volume}/100</strong>, showing whether
            participation confirms the move.
          </li>
          <li>
            News score is <strong>{news}/100</strong>, acting as a catalyst
            adjustment rather than the main driver.
          </li>
        </ul>
      </div>

      <div className="memo-section">
        <h4>Suggested action</h4>

        <p>
          Review price behaviour near <strong>{money(trade.entry_price)}</strong>.
          If the setup remains valid, risk is capped at{" "}
          <strong>{money(trade.risk_amount)}</strong> with{" "}
          <strong>{trade.shares}</strong> shares based on the current stop.
          Invalidation occurs if price breaks below{" "}
          <strong>{money(trade.stop_loss)}</strong>.
        </p>
      </div>
    </section>
  );
}