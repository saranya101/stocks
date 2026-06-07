export default function TradeThesisPanel({ trade }) {
  return (
    <section className="dashboard-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">AI TRADE THESIS</p>
          <h2>Why this trade?</h2>
        </div>
      </div>

      <div className="terminal-stats">
        <div><p>Technical</p><strong>{trade.technical_score}</strong></div>
        <div><p>Backtest</p><strong>{trade.backtest_score}</strong></div>
        <div><p>News</p><strong>{trade.news_score}</strong></div>
        <div><p>Volume</p><strong>{trade.volume_score}</strong></div>
      </div>

      <div className="thesis-list">
        {(trade.reasons || []).map((reason) => (
          <p key={reason}>✓ {reason}</p>
        ))}
      </div>
    </section>
  );
}