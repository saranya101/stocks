function formatStatus(status) {
  const labels = {
    MARKET_OPEN: "Market Open",
    MARKET_CLOSED: "Market Closed",
    PREMARKET: "Pre-Market",
    PRE_MARKET: "Pre-Market",
    AFTER_HOURS: "After Hours",
    COMPLETED: "Completed",
    RUNNING: "Scanning",
    FAILED: "Failed",
  };

  return labels[status] || status || "Unknown";
}

function getMarketName(market) {
  switch (market) {
    case "us":
      return "US Equities";
    case "sg":
      return "Singapore";
    case "etf":
      return "ETFs";
    case "crypto":
      return "Crypto";
    default:
      return "Unknown";
  }
}

export default function MarketStatusBanner({ marketState, market }) {
  return (
    <section className="execution-hero">
      <div>
        <p className="eyebrow">EXECUTION CONTROL CENTRE</p>
        <h1>Market Intelligence</h1>
        <p className="muted">
          Scans the market, ranks opportunities, and prepares trade
          plans for review.
        </p>
      </div>

      <div className="execution-hero-stats">
        <div>
          <span>Market</span>
          <strong>{getMarketName(market)}</strong>
        </div>

        <div>
          <span>Market Hours</span>
          <strong>{formatStatus(marketState?.session)}</strong>
        </div>

        <div>
          <span>Scanned</span>
          <strong>{marketState?.total_scanned ?? 0}</strong>
        </div>

        <div>
          <span>Setups</span>
          <strong>{marketState?.opportunities_found ?? 0}</strong>
        </div>

        <div>
          <span>Runtime</span>
          <strong>{marketState?.duration_seconds ?? 0}s</strong>
        </div>
      </div>
    </section>
  );
}