// src/components/ui/KPICard.jsx
// Consume campos de GET /insights: total_sales, avg_ticket, total_transactions
// y de GET /forecast: mae

export default function KPICard({ label, value, sub, trend, formatter }) {
  const formatted = formatter ? formatter(value) : value;
  const trendPositive = trend > 0;

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5 flex flex-col gap-3 hover:border-indigo-500/40 transition-colors">
      <span className="text-slate-400 text-sm font-medium tracking-wide">{label}</span>
      <span className="text-white text-3xl font-bold tabular-nums">{formatted}</span>
      <div className="flex items-center justify-between">
        {sub && <span className="text-slate-500 text-xs">{sub}</span>}
        {trend !== undefined && (
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              trendPositive
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-rose-500/10 text-rose-400"
            }`}
          >
            {trendPositive ? "▲" : "▼"} {Math.abs(trend).toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  );
}
