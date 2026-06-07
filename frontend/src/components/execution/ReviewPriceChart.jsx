import { useEffect, useState } from "react";
import API from "../../api/api";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
} from "recharts";

function money(value) {
  return value || value === 0 ? `$${Number(value).toFixed(2)}` : "—";
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div className="chart-tooltip">
      <span>{label}</span>
      <strong>{money(payload[0].value)}</strong>
    </div>
  );
}

export default function ReviewPriceChart({ ticker, entry, target, stop }) {
  const [period, setPeriod] = useState("1mo");
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;

    async function loadChart() {
      setLoading(true);

      try {
        const res = await API.get(`/stock-chart/${ticker}?period=${period}`);

        const chartData = (res.data.prices || []).map((item) => ({
          date: item.date,
          close: Number(item.close),
          sma20: item.sma20,
          sma50: item.sma50,
        }));

        setPrices(chartData);
      } catch (err) {
        console.error("Chart failed:", err);
        setPrices([]);
      }

      setLoading(false);
    }

    loadChart();
  }, [ticker, period]);

  const closes = prices.map((item) => item.close).filter(Boolean);
  const latest = closes[closes.length - 1];
  const first = closes[0];
  const change = latest && first ? ((latest - first) / first) * 100 : null;

  return (
    <section className="review-section chart-section">
      <div className="chart-header">
        <div>
          <h3>Price Action</h3>
          <p className={change >= 0 ? "gain" : "loss"}>
            {latest ? money(latest) : "—"}{" "}
            {change !== null
              ? `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`
              : ""}
          </p>
        </div>

        <div className="chart-period-tabs">
          {["5d", "1mo", "3mo", "6mo", "1y"].map((item) => (
            <button
              key={item}
              className={period === item ? "active" : ""}
              onClick={() => setPeriod(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <div className="review-chart-box">
        {loading ? (
          <div className="chart-empty">Loading chart...</div>
        ) : prices.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={prices}
              margin={{ top: 20, right: 20, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#34d8a0" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#34d8a0" stopOpacity={0} />
                </linearGradient>
              </defs>

              <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.06)" />

              <XAxis dataKey="date" hide />

              <YAxis
                orientation="right"
                width={70}
                tick={{ fill: "#7d8797", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                domain={["dataMin - 10", "dataMax + 10"]}
                tickFormatter={(value) => `$${Number(value).toFixed(0)}`}
              />

              <Tooltip content={<CustomTooltip />} />

              {entry && (
                <ReferenceLine
                  y={entry}
                  stroke="#34d8a0"
                  strokeDasharray="5 5"
                  label="ENTRY"
                />
              )}

              {target && (
                <ReferenceLine
                  y={target}
                  stroke="#e9c486"
                  strokeDasharray="5 5"
                  label="TARGET"
                />
              )}

              {stop && (
                <ReferenceLine
                  y={stop}
                  stroke="#fb7185"
                  strokeDasharray="5 5"
                  label="STOP"
                />
              )}

              <Area
                type="monotone"
                dataKey="close"
                stroke="#34d8a0"
                strokeWidth={2.5}
                fill="url(#priceGradient)"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-empty">No chart data found.</div>
        )}
      </div>
    </section>
  );
}
