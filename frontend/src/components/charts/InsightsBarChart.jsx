// src/components/charts/InsightsBarChart.jsx
// Consume: insights.chart_ready = { labels: string[], values: number[] }
// de GET /insights. Los datos vienen listos para graficar directamente.

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

function buildChartData(labels = [], values = []) {
  return labels.map((label, i) => ({ date: label, sales: values[i] ?? 0 }));
}

function formatDate(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs shadow-xl">
      <p className="text-slate-400 mb-1">{label}</p>
      <p className="text-cyan-400 font-semibold">
        ${payload[0].value.toLocaleString("en-US", { maximumFractionDigits: 0 })}
      </p>
    </div>
  );
}

export default function InsightsBarChart({ chart_ready = {}, title = "Daily Sales" }) {
  const { labels = [], values = [] } = chart_ready;
  const data = buildChartData(labels, values);

  // Colorea las barras: el valor máximo en cyan, el resto en indigo tenue
  const maxVal = Math.max(...values);

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <div className="mb-6">
        <h3 className="text-slate-200 font-semibold text-sm">{title}</h3>
        <p className="text-slate-500 text-xs mt-0.5">From /insights chart_ready data</p>
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fill: "#64748b", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            interval={4}
          />
          <YAxis
            tickFormatter={(v) => "$" + (v / 1000).toFixed(1) + "k"}
            tick={{ fill: "#64748b", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={52}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1e293b" }} />
          <Bar dataKey="sales" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.sales === maxVal ? "#22d3ee" : "#6366f1"}
                fillOpacity={entry.sales === maxVal ? 1 : 0.65}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
