// src/components/charts/ForecastLineChart.jsx
// Consume: forecast.series de GET /forecast
// Cada punto: { date, actual, forecast, lower, upper }
// - actual: línea sólida cyan
// - forecast: línea discontinua indigo
// - [lower, upper]: área semitransparente de confianza

import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";

function formatCurrency(v) {
  if (v === null || v === undefined) return "—";
  return "$" + v.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function formatDate(dateStr) {
  // Muestra solo día/mes para no saturar el eje X
  const d = new Date(dateStr + "T00:00:00");
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  const data = payload[0]?.payload ?? {};
  const isForecast = data.forecast !== null;

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs shadow-xl min-w-[160px]">
      <p className="text-slate-400 mb-2 font-medium">{label}</p>
      {data.actual !== null && (
        <p className="text-cyan-400">Actual: <span className="text-white font-semibold">{formatCurrency(data.actual)}</span></p>
      )}
      {isForecast && (
        <>
          <p className="text-indigo-400">Forecast: <span className="text-white font-semibold">{formatCurrency(data.forecast)}</span></p>
          <p className="text-slate-500">Lower: {formatCurrency(data.lower)}</p>
          <p className="text-slate-500">Upper: {formatCurrency(data.upper)}</p>
        </>
      )}
    </div>
  );
}

// Encuentra la fecha donde empieza el forecast para la línea de referencia
function getForecastStartDate(series) {
  const idx = series.findIndex((d) => d.forecast !== null);
  return idx >= 0 ? series[idx].date : null;
}

// Recharts necesita un solo campo para el área del intervalo de confianza.
// Transformamos [lower, upper] → [lower, upper - lower] (área acumulada desde lower).
function prepareData(series) {
  return series.map((d) => ({
    ...d,
    confidenceBand: d.lower !== null ? [d.lower, d.upper] : [null, null],
  }));
}

export default function ForecastLineChart({ series = [], mae, model, confidence }) {
  const data = prepareData(series);
  const forecastStart = getForecastStartDate(series);

  // Ticks: mostrar 1 de cada 10 fechas para no saturar
  const ticks = data
    .filter((_, i) => i % 10 === 0)
    .map((d) => d.date);

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-slate-200 font-semibold text-sm">Sales Forecast</h3>
          <p className="text-slate-500 text-xs mt-0.5">Historical vs Predicted</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          {model && (
            <span className="bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2 py-1 rounded-lg font-medium uppercase tracking-wide">
              {model}
            </span>
          )}
          {mae !== undefined && (
            <span className="text-slate-500">MAE: <span className="text-slate-300">${mae.toFixed(0)}</span></span>
          )}
          {confidence && (
            <span className="text-slate-500">{(confidence * 100).toFixed(0)}% CI</span>
          )}
        </div>
      </div>

      {/* Leyenda manual */}
      <div className="flex items-center gap-5 mb-4 text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-6 h-0.5 bg-cyan-400 inline-block rounded" />
          Actual
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-6 h-0.5 bg-indigo-400 inline-block rounded border-dashed border-t-2 border-indigo-400" />
          Forecast
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-4 h-3 bg-indigo-400/20 inline-block rounded" />
          Confidence Interval
        </span>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

          <XAxis
            dataKey="date"
            ticks={ticks}
            tickFormatter={formatDate}
            tick={{ fill: "#64748b", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(v) => "$" + (v / 1000).toFixed(1) + "k"}
            tick={{ fill: "#64748b", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={52}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Línea que marca el inicio del forecast */}
          {forecastStart && (
            <ReferenceLine
              x={forecastStart}
              stroke="#6366f1"
              strokeDasharray="4 4"
              strokeOpacity={0.5}
              label={{ value: "Forecast →", position: "top", fill: "#6366f1", fontSize: 10 }}
            />
          )}

          {/* Banda de confianza [lower, upper] */}
          <Area
            dataKey="confidenceBand"
            fill="#6366f1"
            fillOpacity={0.12}
            stroke="none"
            type="monotone"
            isAnimationActive={false}
          />

          {/* Línea actual (histórico) */}
          <Line
            dataKey="actual"
            stroke="#22d3ee"
            strokeWidth={2}
            dot={false}
            type="monotone"
            connectNulls={false}
            isAnimationActive={true}
          />

          {/* Línea forecast (predicción) */}
          <Line
            dataKey="forecast"
            stroke="#818cf8"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            type="monotone"
            connectNulls={false}
            isAnimationActive={true}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
