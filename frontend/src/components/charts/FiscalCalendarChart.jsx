// src/components/charts/FiscalCalendarChart.jsx
// Visualiza ventas por semana fiscal con indicadores de promociones

import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

function formatCurrency(v) {
  return "$" + (v ?? 0).toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const data = payload[0]?.payload;
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs shadow-xl min-w-[200px]">
      <p className="text-slate-300 font-semibold mb-2">Semana {data.semana_fiscal}</p>
      <p className="text-slate-400">{data.fecha_inicio} → {data.fecha_fin}</p>
      <p className="text-indigo-400 mt-1">Ventas: <span className="text-white font-semibold">{formatCurrency(data.total_sales)}</span></p>
      <p className="text-slate-400">Transacciones: {data.transactions}</p>
      {data.has_promo && (
        <>
          <p className="text-amber-400 mt-1">MD promedio: {data.avg_md_pct}%</p>
          <div className="mt-1 flex flex-wrap gap-1">
            {[...new Set(data.promos.map(p => p.tipo_promo))].map(tipo => (
              <span key={tipo} className={`px-1.5 py-0.5 rounded text-xs font-medium ${
                tipo === "WkndPromo" ? "bg-indigo-500/20 text-indigo-300" :
                tipo === "OtherPromo" ? "bg-amber-500/20 text-amber-300" :
                "bg-emerald-500/20 text-emerald-300"
              }`}>{tipo}</span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function FiscalCalendarChart({ weeks = [], selectedWeek, onSelectWeek }) {
  if (!weeks.length) return null;

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-slate-200 font-semibold text-sm">Ventas por Semana Fiscal</h3>
          <p className="text-slate-500 text-xs mt-0.5">Haz click en una semana para ver sus promociones</p>
        </div>
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-indigo-500 inline-block" />
            Sin promo
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-sm bg-amber-400 inline-block" />
            Con promo
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart
          data={weeks}
          margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
          onClick={(e) => {
            if (e?.activePayload?.[0]) {
              onSelectWeek?.(e.activePayload[0].payload);
            }
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis
            dataKey="semana_fiscal"
            tickFormatter={(v) => `S${v}`}
            tick={{ fill: "#64748b", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval={3}
          />
          <YAxis
            tickFormatter={(v) => "$" + (v / 1000).toFixed(0) + "k"}
            tick={{ fill: "#64748b", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={48}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#1e293b" }} />
          <Bar dataKey="total_sales" radius={[3, 3, 0, 0]}>
            {weeks.map((w) => (
              <Cell
                key={w.semana_fiscal}
                fill={
                  w.semana_fiscal === selectedWeek?.semana_fiscal
                    ? "#818cf8"
                    : w.has_promo
                    ? "#fbbf24"
                    : "#6366f1"
                }
                fillOpacity={w.semana_fiscal === selectedWeek?.semana_fiscal ? 1 : 0.7}
                style={{ cursor: "pointer" }}
              />
            ))}
          </Bar>
          <Line
            dataKey="avg_md_pct"
            stroke="#f87171"
            strokeWidth={1.5}
            dot={false}
            strokeDasharray="4 2"
            yAxisId={0}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
