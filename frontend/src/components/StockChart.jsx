import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer
} from "recharts";

function StockChart({ data }) {

  return (
    <ResponsiveContainer width="100%" height={500}>

      <LineChart data={data}>

        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="date" hide />

        <YAxis />

        <Tooltip />

        <Legend />

        <Line
          type="monotone"
          dataKey="close"
          stroke="#2563eb"
          dot={false}
        />

        <Line
          type="monotone"
          dataKey="sma20"
          stroke="#16a34a"
          dot={false}
        />

        <Line
          type="monotone"
          dataKey="sma50"
          stroke="#dc2626"
          dot={false}
        />

      </LineChart>

    </ResponsiveContainer>
  );
}

export default StockChart;