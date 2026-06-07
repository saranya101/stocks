export default function OpportunityCard({ trade, selected, onSelect }) {
  return (
    <button
      className={`discover-card ${selected ? "active" : ""}`}
      onClick={() => onSelect(trade)}
    >
      <div>
        <strong>{trade.ticker}</strong>
        <p>{trade.recommendation} · {trade.direction}</p>
      </div>

      <div className="discover-score">
        <span>{trade.conviction}/100</span>
        <small>Grade {trade.grade}</small>
      </div>
    </button>
  );
}