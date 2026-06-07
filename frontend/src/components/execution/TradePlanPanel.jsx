export default function TradePlanPanel({ trade }) {
  return (
    <section className="dashboard-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">EXECUTION</p>
          <h2>Trade Plan Actions</h2>
        </div>
      </div>

      <div className="trade-actions">
        <button className="small-primary">Create Trade Plan</button>
        <button className="small-primary">Paper Trade</button>
        <button className="small-primary">Reject</button>
      </div>
    </section>
  );
}