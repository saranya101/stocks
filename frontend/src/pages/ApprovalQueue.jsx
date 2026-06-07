import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import API from "../api/api"; // your existing axios client — calls map 1:1 to fetch if you prefer
import "./ApprovalQueue.css";

/* ============================================================
   QuantOS — Approval Queue
   Data source: GET /trade-plans  ·  PATCH /trade-plans/{id}/status
   No mock data. All values come straight from the API.
   ============================================================ */

const FILTERS = [
  "ALL",
  "PENDING",
  "APPROVED",
  "SNOOZED",
  "REJECTED",
  "EXECUTED",
];

const STATUS_META = {
  PENDING: { label: "Pending", tone: "pending" },
  APPROVED: { label: "Approved", tone: "approved" },
  REJECTED: { label: "Rejected", tone: "rejected" },
  SNOOZED: { label: "Snoozed", tone: "snoozed" },
  EXECUTED: { label: "Executed", tone: "executed" },
};

const ACTION_LABEL = {
  APPROVED: "Approved",
  REJECTED: "Rejected",
  SNOOZED: "Snoozed",
};

/* ---------- formatters (graceful "—" for missing values) ---------- */
const usd = (v) =>
  v == null || v === "" || isNaN(Number(v))
    ? "—"
    : "$" +
      Number(v).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
const rr = (v) =>
  v == null || isNaN(Number(v)) ? "—" : Number(v).toFixed(2) + ":1";
const int = (v) =>
  v == null || isNaN(Number(v)) ? "—" : Number(v).toLocaleString("en-US");
const prob = (v) =>
  v == null || isNaN(Number(v))
    ? "—"
    : (Number(v) <= 1 ? Math.round(Number(v) * 100) : Math.round(Number(v))) +
      "%";
const convOf = (v) =>
  v == null || isNaN(Number(v))
    ? null
    : Math.max(0, Math.min(100, Math.round(Number(v))));

function dirOf(d) {
  const s = (d || "").toString().toUpperCase();
  const short = s.includes("SHORT") || s.includes("SELL") || s.includes("BEAR");
  return short
    ? { label: "SHORT", cls: "short", down: true }
    : { label: "LONG", cls: "long", down: false };
}

/* ---------- inline icons (no dependencies) ---------- */
const Caret = ({ down }) => (
  <svg
    width="8"
    height="8"
    viewBox="0 0 10 10"
    style={{ transform: down ? "rotate(180deg)" : "none" }}
    aria-hidden
  >
    <path d="M5 1 9 8 1 8Z" fill="currentColor" />
  </svg>
);
const IconSearch = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
  >
    <circle cx="11" cy="11" r="7" />
    <path d="m21 21-4.3-4.3" />
  </svg>
);
const IconRefresh = ({ spinning }) => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={spinning ? "spin" : ""}
  >
    <path d="M21 12a9 9 0 1 1-2.64-6.36" />
    <path d="M21 3v6h-6" />
  </svg>
);

/* ---------- small presentational pieces ---------- */
function GradeBadge({ grade }) {
  if (!grade) return <span className="grade">—</span>;
  const t = grade.toString()[0]?.toUpperCase();
  const tone =
    t === "A" ? "g-a" : t === "B" ? "g-b" : t === "C" ? "g-c" : "g-d";
  return <span className={`grade ${tone}`}>{grade}</span>;
}

function StatusPill({ status }) {
  const m = STATUS_META[status] || { label: status || "—", tone: "snoozed" };
  return <span className={`pill ${m.tone}`}>{m.label}</span>;
}

function DirTag({ direction, lg }) {
  const d = dirOf(direction);
  return (
    <span className={`dir ${d.cls} ${lg ? "lg" : ""}`}>
      <Caret down={d.down} />
      {d.label}
    </span>
  );
}

function ScoreBar({ label, value }) {
  const pct =
    value == null
      ? 0
      : Number(value) <= 1
        ? Number(value) * 100
        : Math.min(100, Number(value));
  const disp =
    value == null
      ? "—"
      : Number(value) <= 1
        ? Number(value).toFixed(2)
        : Math.round(Number(value));
  const tone = pct >= 70 ? "hi" : pct >= 45 ? "mid" : "lo";
  return (
    <div className="score">
      <span className="score-label">{label}</span>
      <div className="score-track">
        <div className={`score-fill ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="score-val">{disp}</span>
    </div>
  );
}

function RRLadder({ entry, stop, target }) {
  const vals = [entry, stop, target];
  if (vals.some((v) => v == null || isNaN(Number(v)))) {
    return (
      <div className="ladder-empty">Price levels unavailable in payload</div>
    );
  }
  const e = Number(entry),
    s = Number(stop),
    t = Number(target);
  const lo = Math.min(e, s, t),
    hi = Math.max(e, s, t),
    range = hi - lo || 1;
  const pos = (v) => ((v - lo) / range) * 100;
  const eP = pos(e),
    sP = pos(s),
    tP = pos(t);
  const riskL = Math.min(eP, sP),
    riskW = Math.abs(eP - sP);
  const rewL = Math.min(eP, tP),
    rewW = Math.abs(eP - tP);
  const Marker = ({ p, cls, label, value }) => (
    <div className={`mk ${cls}`} style={{ left: `${p}%` }}>
      <span className="mk-val">{usd(value)}</span>
      <span className="mk-dot" />
      <span className="mk-label">{label}</span>
    </div>
  );
  return (
    <div className="ladder">
      <div className="ladder-track">
        <div
          className="ladder-seg risk"
          style={{ left: `${riskL}%`, width: `${riskW}%` }}
        />
        <div
          className="ladder-seg reward"
          style={{ left: `${rewL}%`, width: `${rewW}%` }}
        />
        <Marker p={sP} cls="stop" label="STOP" value={s} />
        <Marker p={eP} cls="entry" label="ENTRY" value={e} />
        <Marker p={tP} cls="target" label="TGT" value={t} />
      </div>
    </div>
  );
}

function Section({ title, wide, children }) {
  return (
    <section className={`section ${wide ? "wide" : ""}`}>
      <h3 className="sec-title">{title}</h3>
      {children}
    </section>
  );
}
const Tile = ({ label, value, tone }) => (
  <div className={`tile ${tone || ""}`}>
    <span>{label}</span>
    <b className="mono">{value}</b>
  </div>
);
const Row = ({ label, value, tone }) => (
  <div className="row">
    <span>{label}</span>
    <b className={`mono ${tone || ""}`}>{value}</b>
  </div>
);

/* ---------- trade card (left list) ---------- */
function TradeCard({ plan, active, onSelect, index }) {
  const conv = convOf(plan.conviction);
  return (
    <button
      className={`card ${active ? "active" : ""}`}
      style={{ animationDelay: `${Math.min(index, 12) * 0.03}s` }}
      onClick={() => onSelect(plan.id)}
    >
      <div className="card-top">
        <div className="card-tk">
          <strong className="tk">{plan.ticker || "—"}</strong>
          <DirTag direction={plan.direction} />
        </div>
        <StatusPill status={plan.status} />
      </div>
      <div className="card-rec">{plan.recommendation || "—"}</div>
      <div className="card-foot">
        <div className="card-metric">
          <span>CONV</span>
          <b className="mono">{conv ?? "—"}</b>
        </div>
        <div className="card-metric">
          <span>GRADE</span>
          <GradeBadge grade={plan.grade} />
        </div>
        <div className="card-metric">
          <span>R:R</span>
          <b className="mono">{rr(plan.risk_reward)}</b>
        </div>
      </div>
      <div className="card-conv-bar">
        <div className="card-conv-fill" style={{ width: `${conv ?? 0}%` }} />
      </div>
    </button>
  );
}

/* ---------- review panel (right) ---------- */
function ReviewPanel({ plan, busyAction, onDecide }) {
  if (!plan) {
    return (
      <div className="empty-review">
        <p>
          Select a proposal from the queue to review its full thesis, setup and
          intelligence breakdown.
        </p>
      </div>
    );
  }
  const executed = plan.status === "EXECUTED";
  const scores = [
    ["Technical", plan.technical_score],
    ["Backtest", plan.backtest_score],
    ["Volume", plan.volume_score],
    ["News", plan.news_score],
  ];
  const nums = scores
    .map(([, v]) => v)
    .filter((v) => v != null && !isNaN(Number(v)));
  const composite = nums.length
    ? Math.round(
        nums.reduce(
          (a, v) => a + (Number(v) <= 1 ? Number(v) * 100 : Number(v)),
          0,
        ) / nums.length,
      )
    : null;
  const conv = convOf(plan.conviction);
  const busy = !!busyAction;

  return (
    <div className="review" key={plan.id}>
      <div className="rv-head">
        <div className="rv-head-l">
          <div className="rv-tk-row">
            <h2 className="rv-tk">{plan.ticker || "—"}</h2>
            <DirTag direction={plan.direction} lg />
            <StatusPill status={plan.status} />
          </div>
          <div className="rv-rec">
            <span className="rv-rec-main">{plan.recommendation || "—"}</span>
            <span className="rv-sep">/</span> Grade{" "}
            <GradeBadge grade={plan.grade} />
            <span className="rv-sep">/</span> Probability{" "}
            <b className="mono">{prob(plan.probability)}</b>
          </div>
        </div>
        <div className="conv">
          <div className="conv-num">
            <strong>{conv ?? "—"}</strong>
            <span>/100</span>
          </div>
          <div className="conv-track">
            <div className="conv-fill" style={{ width: `${conv ?? 0}%` }} />
          </div>
          <span className="conv-label">Conviction</span>
        </div>
      </div>

      <div className="rv-body">
        <Section title="Trade Setup">
          <div className="tiles">
            <Tile label="Entry" value={usd(plan.entry_price)} />
            <Tile label="Stop" value={usd(plan.stop_loss)} tone="red" />
            <Tile label="Target" value={usd(plan.take_profit)} tone="green" />
            <Tile
              label="Risk : Reward"
              value={rr(plan.risk_reward)}
              tone="accent"
            />
          </div>
          <RRLadder
            entry={plan.entry_price}
            stop={plan.stop_loss}
            target={plan.take_profit}
          />
          <div className="row tight">
            <span>Expected hold</span>
            <b className="mono">
              {plan.expected_hold_days != null
                ? `${plan.expected_hold_days} days`
                : "—"}
            </b>
          </div>
        </Section>

        <Section title="Position Plan">
          <div className="rows">
            <Row label="Shares" value={int(plan.shares)} />
            <Row label="Position Value" value={usd(plan.position_value)} />
            <Row label="Risk Amount" value={usd(plan.risk_amount)} tone="red" />
          </div>
        </Section>

        <Section title="Intelligence Breakdown" wide>
          <div className="intel-head">
            <span>Composite signal · derived from factors</span>
            <b className="mono">{composite == null ? "—" : composite}</b>
          </div>
          <div className="scores">
            {scores.map(([l, v]) => (
              <ScoreBar key={l} label={l} value={v} />
            ))}
          </div>
        </Section>
      </div>
      <Section title="Company Intelligence" wide>
        <div className="rows">
          <Row label="Company" value={plan.company_name || "—"} />
          <Row label="Sector" value={plan.sector || "—"} />
          <Row label="Industry" value={plan.industry || "—"} />
          <Row label="Market Cap" value={plan.market_cap || "—"} />
          <Row label="Country" value={plan.country || "—"} />
        </div>

        {plan.website && (
          <a
            href={plan.website}
            target="_blank"
            rel="noopener noreferrer"
            className="company-link"
          >
            Visit Company Website →
          </a>
        )}

        {plan.description && (
          <p className="company-description">{plan.description}</p>
        )}
      </Section>
      <Section title="Opportunity Ranking">
        <div className="tiles">
          <Tile
            label="Rank"
            value={
              plan.rank && plan.total_scanned
                ? `#${plan.rank} / ${plan.total_scanned}`
                : "—"
            }
          />

          <Tile
            label="Top Percentile"
            value={
              plan.rank && plan.total_scanned
                ? `${((plan.rank / plan.total_scanned) * 100).toFixed(1)}%`
                : "—"
            }
          />
        </div>
      </Section>
      <Section title="Investment Committee Memo" wide>
        <div className="memo-text">
          {plan.investment_memo || "Memo unavailable"}
        </div>
      </Section>

      <div className="rv-actions">
        <button
          className="act approve"
          disabled={executed || plan.status === "APPROVED" || busy}
          onClick={() => onDecide("APPROVED")}
        >
          {busyAction === "APPROVED" && <span className="spin-mini" />} Approve
          Trade
        </button>
        <button
          className="act reject"
          disabled={executed || plan.status === "REJECTED" || busy}
          onClick={() => onDecide("REJECTED")}
        >
          {busyAction === "REJECTED" && <span className="spin-mini" />} Reject
          Trade
        </button>
        <button
          className="act snooze"
          disabled={executed || plan.status === "SNOOZED" || busy}
          onClick={() => onDecide("SNOOZED")}
        >
          {busyAction === "SNOOZED" && <span className="spin-mini" />} Snooze
        </button>
      </div>

      {executed && (
        <div className="locked-note">
          This proposal is executed and locked from further action.
        </div>
      )}
    </div>
  );
}

/* ---------- skeletons ---------- */
const SkeletonList = () =>
  Array.from({ length: 6 }).map((_, i) => (
    <div className="sk-card" key={i} style={{ animationDelay: `${i * 0.06}s` }}>
      <div className="sk-line w40" />
      <div className="sk-line w70" />
      <div className="sk-line w90" />
    </div>
  ));

const ReviewSkeleton = () => (
  <div className="review-sk">
    <div className="sk-line w30 tall" />
    <div className="sk-line w60" />
    <div className="sk-grid">
      {Array.from({ length: 4 }).map((_, i) => (
        <div className="sk-block" key={i} />
      ))}
    </div>
    <div className="sk-block tallblock" />
  </div>
);

/* ============================================================
   Main component
   ============================================================ */
export default function ApprovalQueue() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("PENDING"); // approval queue opens on what needs action
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [busyAction, setBusyAction] = useState(null);
  const [toast, setToast] = useState(null);
  const toastTimer = useRef(null);

  const showToast = useCallback((msg, tone) => {
    setToast({ msg, tone, key: Date.now() });
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2600);
  }, []);

  /* ---- GET /trade-plans ---- */
  const fetchPlans = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await API.get("/trade-plans");
      const list = Array.isArray(data)
        ? data
        : data?.trade_plans || data?.items || [];
      setPlans(list);
    } catch (err) {
      console.error(err);
      setError("Unable to load trade plans.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlans();
    return () => clearTimeout(toastTimer.current);
  }, [fetchPlans]);

  /* ---- derived ---- */
  const counts = useMemo(() => {
    const c = { PENDING: 0, APPROVED: 0, REJECTED: 0, SNOOZED: 0, EXECUTED: 0 };
    for (const p of plans) if (c[p.status] != null) c[p.status]++;
    return c;
  }, [plans]);

  const visible = useMemo(() => {
    let list = plans;
    if (filter !== "ALL") list = list.filter((p) => p.status === filter);
    const q = query.trim().toUpperCase();
    if (q)
      list = list.filter((p) => (p.ticker || "").toUpperCase().includes(q));
    return [...list].sort(
      (a, b) => (b.conviction ?? -Infinity) - (a.conviction ?? -Infinity),
    );
  }, [plans, filter, query]);

  const selected = useMemo(
    () => plans.find((p) => p.id === selectedId) || null,
    [plans, selectedId],
  );

  // keep a valid selection (and auto-advance after a decision removes one from view)
  useEffect(() => {
    if (visible.length === 0) {
      if (selectedId !== null) setSelectedId(null);
      return;
    }
    if (!visible.some((p) => p.id === selectedId)) setSelectedId(visible[0].id);
  }, [visible, selectedId]);

  // keyboard navigation through the queue
  useEffect(() => {
    function onKey(e) {
      const tag = document.activeElement?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
      if (visible.length === 0) return;
      e.preventDefault();
      const idx = visible.findIndex((p) => p.id === selectedId);
      const next =
        e.key === "ArrowDown"
          ? Math.min(visible.length - 1, idx + 1)
          : Math.max(0, idx - 1);
      setSelectedId(visible[next].id);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [visible, selectedId]);

  /* ---- PATCH /trade-plans/{id}/status (optimistic) ---- */
  const decide = useCallback(
    async (status) => {
      if (!selectedId) return;
      const id = selectedId;
      const plan = plans.find((p) => p.id === id);
      if (!plan) return;
      const prev = plan.status;

      setBusyId(id);
      setBusyAction(status);
      setPlans((ps) => ps.map((p) => (p.id === id ? { ...p, status } : p)));

      try {
        await API.patch(`/trade-plans/${id}/status`, { status });
        showToast(
          `${plan.ticker} — ${ACTION_LABEL[status]}`,
          STATUS_META[status].tone,
        );
      } catch (err) {
        console.error(err);
        setPlans((ps) =>
          ps.map((p) => (p.id === id ? { ...p, status: prev } : p)),
        );
        showToast(
          `Failed to ${ACTION_LABEL[status].toLowerCase().replace("ed", "")} ${plan.ticker}`,
          "error",
        );
      } finally {
        setBusyId(null);
        setBusyAction(null);
      }
    },
    [selectedId, plans, showToast],
  );

  const filterCount = (f) => (f === "ALL" ? plans.length : (counts[f] ?? 0));
  const filterLabel = (f) => (f === "ALL" ? "All" : STATUS_META[f].label);

  const RibbonStat = ({ n, label, tone }) => (
    <div className={`stat ${tone}`}>
      <span className="stat-dot" />
      <div className="stat-body">
        <b className="stat-n mono">{n}</b>
        <span className="stat-l">{label}</span>
      </div>
    </div>
  );

  return (
    <div className="aq">
      {/* TOP */}
      <header className="aq-top">
        <div className="aq-title">
          <svg
            width="30"
            height="30"
            viewBox="0 0 30 30"
            className="aq-mark"
            aria-hidden
          >
            <rect
              x="1"
              y="1"
              width="28"
              height="28"
              rx="7"
              fill="none"
              stroke="#5bc0d8"
              strokeWidth="1.3"
            />
            <path
              d="M8 19 13 11 16 15 22 8"
              fill="none"
              stroke="#5bc0d8"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <div>
            <h1>APPROVAL QUEUE</h1>
            <p>QuantOS · trade proposal review — pre-execution</p>
          </div>
        </div>

        <div className="aq-ribbon">
          <RibbonStat n={counts.PENDING} label="Pending" tone="pending" />
          <RibbonStat n={counts.APPROVED} label="Approved" tone="approved" />
          <RibbonStat n={counts.SNOOZED} label="Snoozed" tone="snoozed" />
          <RibbonStat n={counts.REJECTED} label="Rejected" tone="rejected" />
          <RibbonStat n={counts.EXECUTED} label="Executed" tone="executed" />
          <span className="ribbon-div" />
          <RibbonStat n={plans.length} label="Total" tone="total" />
          <button
            className="refresh"
            onClick={fetchPlans}
            disabled={loading}
            title="Refresh queue"
          >
            <IconRefresh spinning={loading} />
          </button>
        </div>
      </header>

      {/* MAIN */}
      <div className="aq-main">
        <aside className="aq-left">
          <div className="aq-controls">
            <div className="filters">
              {FILTERS.map((f) => (
                <button
                  key={f}
                  className={`f ${filter === f ? "active" : ""}`}
                  onClick={() => setFilter(f)}
                >
                  {filterLabel(f)} <em>{filterCount(f)}</em>
                </button>
              ))}
            </div>
            <div className="search">
              <IconSearch />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search ticker…"
                spellCheck={false}
                autoComplete="off"
              />
              {query && (
                <button
                  className="search-clear"
                  onClick={() => setQuery("")}
                  aria-label="Clear"
                >
                  ×
                </button>
              )}
            </div>
          </div>

          <div className="aq-list">
            {loading ? (
              <SkeletonList />
            ) : error ? (
              <div className="error-state">
                <p>{error}</p>
                <button onClick={fetchPlans}>Retry</button>
              </div>
            ) : visible.length === 0 ? (
              <div className="empty-list">
                <p>
                  {query
                    ? `No ${filter === "ALL" ? "" : filterLabel(filter).toLowerCase() + " "}proposals match “${query}”.`
                    : `No ${filterLabel(filter).toLowerCase()} proposals in the queue.`}
                </p>
              </div>
            ) : (
              visible.map((p, i) => (
                <TradeCard
                  key={p.id}
                  plan={p}
                  index={i}
                  active={p.id === selectedId}
                  onSelect={setSelectedId}
                />
              ))
            )}
          </div>

          <div className="aq-hint">
            <kbd>↑</kbd>
            <kbd>↓</kbd> navigate queue · sorted by conviction
          </div>
        </aside>

        <section className="aq-right">
          {loading ? (
            <ReviewSkeleton />
          ) : (
            <ReviewPanel
              plan={selected}
              busyAction={busyId === selected?.id ? busyAction : null}
              onDecide={decide}
            />
          )}
        </section>
      </div>

      {toast && (
        <div className={`toast ${toast.tone}`} key={toast.key}>
          {toast.msg}
        </div>
      )}
    </div>
  );
}
