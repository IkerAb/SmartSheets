// src/components/charts/SimulationChart.jsx
// Consume: simulate response = { base, simulated, delta_revenue, delta_pct, modifiers }
// de POST /simulate.
// Muestra dos líneas: base (slate) vs simulated (emerald/rose según delta)

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

function buildData(base, simulated) {
  return base.labels.map((date, i) => ({
    date,
    base: base.values[i],
    simulated: simulated.values[i],
  }));
}

function formatDate(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function formatCurrency(v) {
  return "$" + (v ?? 0).toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs shadow-xl min-w-[150px]">
      <p className="text-slate-400 mb-2">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.dataKey === "base" ? "Base" : "Simulated"}: <span className="text-white font-semibold">{formatCurrency(p.value)}</span>
        </p>
      ))}
    </div>
  );
}

export default function SimulationChart({ simulateData }) {
  if (!simulateData) return null;

  const { base, simulated, delta_revenue, delta_pct, modifiers } = simulateData;
  const data = buildData(base, simulated);
  const positive = delta_pct >= 0;
  const simulatedColor = positive ? "#34d399" : "#f87171";

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-slate-200 font-semibold text-sm">Scenario Simulation</h3>
          <p className="text-slate-500 text-xs mt-0.5">
            Price ×{modifiers.price_modifier} · Volume ×{modifiers.volume_modifier}
          </p>
        </div>
        {/* Delta badge */}
        <div className={`text-center px-3 py-2 rounded-xl border ${positive ? "bg-emerald-500/10 border-emerald-500/20" : "bg-rose-500/10 border-rose-500/20"}`}>
          <p className={`text-lg font-bold ${positive ? "text-emerald-400" : "text-rose-400"}`}>
            {positive ? "+" : ""}{delta_pct.toFixed(1)}%
          </p>
          <p className="text-slate-500 text-xs">
            {positive ? "+" : ""}{formatCurrency(delta_revenue)} revenue
          </p>
        </div>
      </div>

      {/* Leyenda */}
      <div className="flex items-center gap-5 mb-4 text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-6 h-0.5 bg-slate-400 inline-block rounded" />
          Base
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-6 h-0.5 inline-block rounded" style={{ backgroundColor: simulatedColor }} />
          Simulated
        </span>
      </div>

      {/* Totales */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="bg-slate-900/50 rounded-xl p-3">
          <p className="text-slate-500 text-xs mb-1">Base Total</p>
          <p className="text-white font-semibold tabular-nums">{formatCurrency(base.total_projected)}</p>
        </div>
        <div className={`rounded-xl p-3 ${positive ? "bg-emerald-900/20" : "bg-rose-900/20"}`}>
          <p className="text-slate-500 text-xs mb-1">Simulated Total</p>
          <p className="font-semibold tabular-nums" style={{ color: simulatedColor }}>
            {formatCurrency(simulated.total_projected)}
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
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
          <Tooltip content={<CustomTooltip />} />
          <Line dataKey="base" stroke="#94a3b8" strokeWidth={2} dot={false} type="monotone" />
          <Line dataKey="simulated" stroke={simulatedColor} strokeWidth={2} dot={false} type="monotone" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
