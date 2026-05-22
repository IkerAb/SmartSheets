// src/components/ui/SellThroughTable.jsx
// Tabla de Sell-Through por categoría con colores e insights

function STBadge({ nivel, pct }) {
  const styles = {
    alto:  "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    medio: "bg-amber-500/15 text-amber-400 border-amber-500/20",
    bajo:  "bg-rose-500/15 text-rose-400 border-rose-500/20",
  };
  const icons = { alto: "🟢", medio: "🟡", bajo: "🔴" };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg border text-xs font-bold tabular-nums ${styles[nivel]}`}>
      {icons[nivel]} {pct}%
    </span>
  );
}

function PromoChips({ tipos }) {
  if (!tipos?.length) return <span className="text-slate-600 text-xs">—</span>;
  const colors = {
    WkndPromo:  "bg-indigo-500/10 text-indigo-300 border-indigo-500/20",
    OtherPromo: "bg-amber-500/10 text-amber-300 border-amber-500/20",
    DD:         "bg-emerald-500/10 text-emerald-300 border-emerald-500/20",
  };
  return (
    <div className="flex flex-wrap gap-1">
      {tipos.map(t => (
        <span key={t} className={`text-xs px-1.5 py-0.5 rounded border ${colors[t] ?? "bg-slate-700 text-slate-300"}`}>
          {t}
        </span>
      ))}
    </div>
  );
}

export default function SellThroughTable({ data, resumen, semana }) {
  if (!data?.length) return null;

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-slate-200 font-semibold text-sm">
            Sell-Through {semana ? `— Semana ${semana}` : "— Todas las semanas"}
          </h3>
          <p className="text-slate-500 text-xs mt-0.5">Inventario inicial vs unidades vendidas por categoría</p>
        </div>
      </div>

      {/* Resumen */}
      {resumen && (
        <div className="bg-slate-900/60 border border-slate-700/30 rounded-xl px-4 py-3 mb-4 text-xs text-slate-300 leading-relaxed">
          <span className="text-indigo-400 font-semibold mr-2">📊 Resumen:</span>
          {resumen}
        </div>
      )}

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs border-b border-slate-700/50">
              <th className="text-left pb-3 font-medium">Categoría</th>
              <th className="text-right pb-3 font-medium">Inv. Inicial</th>
              <th className="text-right pb-3 font-medium">Uds. Vendidas</th>
              <th className="text-right pb-3 font-medium">Sell-Through</th>
              <th className="text-left pb-3 font-medium pl-4">Promos</th>
              <th className="text-right pb-3 font-medium">MD%</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.categoria} className="border-b border-slate-700/30 last:border-0 hover:bg-slate-700/20 transition-colors">
                <td className="py-3 text-slate-200 font-medium">{row.categoria}</td>
                <td className="py-3 text-right text-slate-400 tabular-nums">{row.inventario_inicial.toLocaleString()}</td>
                <td className="py-3 text-right text-slate-300 tabular-nums font-medium">{row.unidades_vendidas.toLocaleString()}</td>
                <td className="py-3 text-right">
                  <STBadge nivel={row.nivel} pct={row.sell_through_pct} />
                </td>
                <td className="py-3 pl-4">
                  <PromoChips tipos={row.tipo_promos} />
                </td>
                <td className="py-3 text-right">
                  {row.md_promedio > 0
                    ? <span className="text-amber-400 text-xs font-semibold">{row.md_promedio}%</span>
                    : <span className="text-slate-600 text-xs">—</span>
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Insights */}
      <div className="mt-4 flex flex-col gap-2">
        {data.filter(r => r.insight).map((row) => (
          <div
            key={row.categoria}
            className={`text-xs px-3 py-2 rounded-lg border ${
              row.nivel === "alto"
                ? "bg-emerald-500/5 border-emerald-500/15 text-emerald-300"
                : row.nivel === "bajo" && row.tiene_promo
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
