export default function OpportunityList({ opportunities, selected, setSelected }) {
  const sorted = [...opportunities].sort(
    (a, b) => (b.conviction || 0) - (a.conviction || 0)
  );

  return (
    <section className="dashboard-card opportunity-panel">
      <div className="opportunity-header">
        <div>
          <p className="eyebrow">TRADE DISCOVERY</p>
          <h2>Ranked Opportunities</h2>
        </div>

        <span>{sorted.length} setups</span>
      </div>

      <div className="opportunity-list">
        {sorted.map((trade, index) => (
          <button
            key={`${trade.ticker}-${index}`}
            className={`opportunity-row ${
              selected?.ticker === trade.ticker ? "active" : ""
            }`}
            onClick={() => setSelected(trade)}
          >
            <div className="rank-pill">#{index + 1}</div>

            <div className="opportunity-main">
              <div>
                <strong>{trade.ticker}</strong>
                <span>{trade.recommendation}</span>
              </div>

              <p>
                {trade.direction} · Grade {trade.grade} · {trade.expected_hold_days}d
              </p>
            </div>

            <div className="opportunity-score">
              <strong>{trade.conviction}</strong>
              <span>/100</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}