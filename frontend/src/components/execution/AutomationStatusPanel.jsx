export default function AutomationStatusPanel() {
  return (
    <section className="dashboard-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">AUTOMATION</p>
          <h2>Execution Mode</h2>
        </div>
      </div>

      <div className="terminal-stats">
        <div><p>Paper Mode</p><strong>Enabled</strong></div>
        <div><p>Approval Mode</p><strong>Next</strong></div>
        <div><p>Auto Mode</p><strong>Locked</strong></div>
      </div>
    </section>
  );
}