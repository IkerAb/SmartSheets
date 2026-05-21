// src/components/ui/MetricsTable.jsx
// Consume top_products y monthly_growth de GET /insights

function formatCurrency(v) {
  return "$" + v.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function MoMChip({ pct }) {
  if (pct === null) return <span className="text-slate-600 text-xs">—</span>;
  const pos = pct >= 0;
  return (
    <span
      className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
        pos ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
      }`}
    >
      {pos ? "+" : ""}
      {pct.toFixed(1)}%
    </span>
  );
}

export function TopProductsTable({ products = [] }) {
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <h3 className="text-slate-300 text-sm font-semibold mb-4">Top Products</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-slate-500 text-xs border-b border-slate-700/50">
            <th className="text-left pb-2 font-medium">Product</th>
            <th className="text-right pb-2 font-medium">Revenue</th>
            <th className="text-right pb-2 font-medium">Share</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p, i) => (
            <tr key={p.name} className="border-b border-slate-700/30 last:border-0">
              <td className="py-2.5 text-slate-300 flex items-center gap-2">
                <span className="text-slate-600 text-xs w-4">{i + 1}</span>
                {p.name}
              </td>
              <td className="py-2.5 text-right text-white tabular-nums font-medium">
                {formatCurrency(p.total)}
              </td>
              <td className="py-2.5 text-right">
                <span className="text-indigo-400 font-semibold">{p.pct.toFixed(1)}%</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function MonthlyGrowthTable({ monthly_growth = [] }) {
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <h3 className="text-slate-300 text-sm font-semibold mb-4">Monthly Growth (MoM)</h3>
      <div className="overflow-y-auto max-h-64">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-slate-800">
            <tr className="text-slate-500 text-xs border-b border-slate-700/50">
              <th className="text-left pb-2 font-medium">Month</th>
              <th className="text-right pb-2 font-medium">Sales</th>
              <th className="text-right pb-2 font-medium">MoM</th>
            </tr>
          </thead>
          <tbody>
            {monthly_growth.map((m) => (
              <tr key={m.month} className="border-b border-slate-700/30 last:border-0">
                <td className="py-2 text-slate-400">{m.month}</td>
                <td className="py-2 text-right text-white tabular-nums">{formatCurrency(m.sales)}</td>
                <td className="py-2 text-right">
                  <MoMChip pct={m.mom_pct} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
