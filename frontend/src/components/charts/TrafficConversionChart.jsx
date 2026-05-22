// src/components/charts/TrafficConversionChart.jsx
// Barras de tráfico por tienda + línea de tasa de conversión

import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
} from "recharts";

const STORE_COLORS = {
  "Tienda Norte":   "#6366f1",
  "Tienda Sur":     "#f87171",
  "Tienda Centro":  "#34d399",
  "Tienda Oriente": "#fbbf24",
  "Tienda Poniente":"#a78bfa",
};

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const trafico = payload.find(p => p.dataKey === "trafico_total");
  const conv = payload.find(p => p.dataKey === "tasa_conversion_pct");
  const txns = payload[0]?.payload?.transacciones_total;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs shadow-xl min-w-[180px]">
      <p className="text-slate-200 font-semibold mb-2">{label}</p>
      {trafico && <p className="text-indigo-400">Tráfico: <span className="text-white font-semibold">{trafico.value?.toLocaleString()}</span></p>}
      {txns !== undefined && <p className="text-slate-400">Transacciones: <span className="text-slate-200">{txns?.toLocaleString()}</span></p>}
      {conv && <p className="text-amber-400 mt-1">Conversión: <span className="text-white font-bold">{conv.value}%</span></p>}
    </div>
  );
}

function ConvBadge({ nivel }) {
  const styles = {
    alto:  "bg-emerald-500/15 text-emerald-400",
    medio: "bg-amber-500/15 text-amber-400",
    bajo:  "bg-rose-500/15 text-rose-400",
  };
  const icons = { alto: "🟢", medio: "🟡", bajo: "🔴" };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-lg font-medium ${styles[nivel]}`}>
      {icons[nivel]} {nivel}
    </span>
  );
}

export default function TrafficConversionChart({ data, avgConversion, bestStore, worstStore, semana }) {
  if (!data?.length) return null;

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-slate-200 font-semibold text-sm">
            Tráfico y Conversión por Tienda
            {semana ? ` — Semana ${semana}` : " — Acumulado"}
          </h3>
          <p className="text-slate-500 text-xs mt-0.5">
            Barras = visitantes · Línea = tasa de conversión %
          </p>
        </div>
        <div className="text-right text-xs">
          <p className="text-slate-500">Conv. promedio</p>
          <p className="text-amber-400 font-bold text-lg">{avgConversion}%</p>
        </div>
      </div>

      {/* Best / Worst */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="bg-emerald-500/5 border border-emerald-500/15 rounded-xl px-3 py-2.5">
          <p className="text-emerald-400 text-xs font-semibold mb-0.5">🏆 Mejor conversión</p>
          <p className="text-white text-sm font-bold">{bestStore}</p>
        </div>
        <div className="bg-rose-500/5 border border-rose-500/15 rounded-xl px-3 py-2.5">
          <p className="text-rose-400 text-xs font-semibold mb-0.5">📉 Menor conversión</p>
          <p className="text-white text-sm font-bold">{worstStore}</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data} margin={{ top: 4, right: 40, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="tienda"
            tick={{ fill: "#64748b", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => v.replace("Tienda ", "")}
          />
          <YAxis
            yAxisId="left"
            tickFormatter={(v) => v.toLocaleString()}
            tick={{ fill: "#64748b", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={55}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tickFormatter={(v) => `${v}%`}
            tick={{ fill: "#fbbf24", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={40}
            domain={[0, 35]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: "11px", color: "#64748b", paddingTop: "12px" }}
            formatter={(value) => value === "trafico_total" ? "Tráfico" : "Conversión %"}
          />
          <Bar dataKey="trafico_total" yAxisId="left" radius={[4, 4, 0, 0]} name="trafico_total">
            {data.map((entry) => (
              <Cell
                key={entry.tienda}
                fill={STORE_COLORS[entry.tienda] ?? "#6366f1"}
                fillOpacity={0.8}
              />
            ))}
          </Bar>
          <Line
            dataKey="tasa_conversion_pct"
            yAxisId="right"
            stroke="#fbbf24"
            strokeWidth={2.5}
            dot={{ fill: "#fbbf24", r: 5, strokeWidth: 0 }}
            activeDot={{ r: 7 }}
            name="tasa_conversion_pct"
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Tabla de insights */}
      <div className="mt-5 flex flex-col gap-2">
        {data.map((row) => (
          <div
            key={row.tienda}
            className={`text-xs px-3 py-2 rounded-lg border ${
              row.nivel_conversion === "alto"
                ? "bg-emerald-500/5 border-emerald-500/15 text-emerald-300"
                : row.nivel_conversion === "bajo"
                ? "bg-rose-500/5 border-rose-500/15 text-rose-300"
                : "bg-slate-900/40 border-slate-700/30 text-slate-400"
            }`}
          >
            {row.insight}
          </div>
        ))}
      </div>
    </div>
  );
}
