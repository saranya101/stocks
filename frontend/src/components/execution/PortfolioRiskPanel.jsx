export default function PortfolioRiskPanel() {
  return (
    <section className="dashboard-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">RISK ENGINE</p>
          <h2>Portfolio Risk</h2>
        </div>
      </div>

      <div className="terminal-stats">
        <div><p>Max Risk / Trade</p><strong>1%</strong></div>
        <div><p>Daily Loss Limit</p><strong>3%</strong></div>
        <div><p>Open Trades</p><strong>0</strong></div>
        <div><p>Risk Status</p><strong>Clear</strong></div>
      </div>
    </section>
  );
}