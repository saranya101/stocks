import { useEffect, useState } from "react";
import API from "../api/api";

import MarketStatusBanner from "../components/execution/MarketStatusBanner";
import OpportunityList from "../components/execution/OpportunityList";
import PortfolioRiskPanel from "../components/execution/PortfolioRiskPanel";
import AutomationStatusPanel from "../components/execution/AutomationStatusPanel";
import OpportunityReviewPanel from "../components/execution/OpportunityReviewPanel";

import "./ExecutionCenter.css";

export default function ExecutionCenter() {
  const [marketState, setMarketState] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [selected, setSelected] = useState(null);
  const [market, setMarket] = useState("us");
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(false);

  async function loadData() {
    setLoading(true);

    try {
      const res = await API.get(`/scanner/latest?market=${market}`);

      const data = res.data.opportunities || [];

      setOpportunities(data);
      setSelected(data[0] || null);

      const scanStatus = res.data.scan_status;

      setMarketState({
        session: "MARKET_OPEN", // temporary until backend returns real market_state
        scan_status: scanStatus?.status || "NO_SCAN",
        timestamp: scanStatus?.completed_at || null,
        total_scanned: scanStatus?.total_scanned ?? 0,
        opportunities_found: scanStatus?.opportunities_found ?? 0,
        duration_seconds: scanStatus?.duration_seconds ?? 0,
      });
    } catch (err) {
      console.error(err);
      alert("Failed to load execution centre.");
    }

    setLoading(false);
  }

  async function runScan() {
    setLoading(true);

    try {
      await API.post(`/scanner/run?market=${market}&limit=500&timeframe=5m`);

      await loadData();
    } catch (err) {
      console.error(err);
      alert("Scan failed.");
    }

    setLoading(false);
  }

  useEffect(() => {
    loadData();
  }, [market]);

  const filteredOpportunities = opportunities.filter((item) => {
    if (filter === "all") return true;
    if (filter === "strong_buy") return item.recommendation === "STRONG BUY";
    if (filter === "buy") return item.recommendation === "BUY";
    if (filter === "watch") return item.recommendation === "WATCH";
    if (filter === "high_conviction") return Number(item.conviction) >= 75;
    return true;
  });

  return (
    <div className="execution-page">
      <div className="market-tabs">
        {[
          { key: "us", label: "US Market" },
          { key: "sg", label: "Singapore" },
          { key: "etf", label: "ETFs" },
          { key: "crypto", label: "Crypto" },
        ].map((item) => (
          <button
            key={item.key}
            className={market === item.key ? "active" : ""}
            onClick={() => setMarket(item.key)}
          >
            {item.label}
          </button>
        ))}
        <button className="run-scan-btn" onClick={runScan}>
          {loading ? "Scanning..." : "Run Scan"}
        </button>
      </div>

      <MarketStatusBanner marketState={marketState} market={market} />

      {loading ? (
        <section className="execution-loading">Scanning market...</section>
      ) : (
        <div className="execution-layout">
          <div className="execution-left">
            <section className="dashboard-card scan-summary">
              <h3>Latest Scan</h3>

              <div className="summary-row">
                <span>Status</span>
                <strong>{marketState?.scan_status}</strong>
              </div>

              <div className="summary-row">
                <span>Scanned</span>
                <strong>{marketState?.total_scanned ?? 0}</strong>
              </div>

              <div className="summary-row">
                <span>Opportunities</span>
                <strong>{marketState?.opportunities_found ?? 0}</strong>
              </div>

              <div className="summary-row">
                <span>Last Scan</span>
                <strong>
                  {marketState?.timestamp
                    ? new Date(marketState.timestamp).toLocaleString()
                    : "-"}
                </strong>
              </div>
            </section>
            <div className="opportunity-filter-tabs">
              {[
                { key: "all", label: "All" },
                { key: "strong_buy", label: "Strong Buy" },
                { key: "buy", label: "Buy" },
                { key: "watch", label: "Watch" },
                { key: "high_conviction", label: "High Conviction" },
              ].map((item) => (
                <button
                  key={item.key}
                  className={filter === item.key ? "active" : ""}
                  onClick={() => setFilter(item.key)}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <OpportunityList
              opportunities={filteredOpportunities}
              selected={selected}
              setSelected={setSelected}
            />
          </div>

          <div className="execution-right">
            {selected ? (
              <>
                <OpportunityReviewPanel trade={selected} market={market} />
              </>
            ) : (
              <section className="dashboard-card">
                <p className="muted">No opportunities found for this market.</p>
              </section>
            )}

            <div className="execution-bottom-grid">
              <PortfolioRiskPanel />
              <AutomationStatusPanel />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
