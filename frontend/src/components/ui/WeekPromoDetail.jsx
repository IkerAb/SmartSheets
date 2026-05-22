// src/components/ui/WeekPromoDetail.jsx
// Muestra el detalle de promociones de una semana fiscal seleccionada

const tipoStyles = {
  WkndPromo:  { bg: "bg-indigo-500/10", border: "border-indigo-500/20", text: "text-indigo-300", label: "Weekend Promo" },
  OtherPromo: { bg: "bg-amber-500/10",  border: "border-amber-500/20",  text: "text-amber-300",  label: "Other Promo"   },
  DD:         { bg: "bg-emerald-500/10",border: "border-emerald-500/20",text: "text-emerald-300", label: "Daily Deal"    },
};

function PromoCard({ promo }) {
  const style = tipoStyles[promo.tipo_promo] ?? tipoStyles.DD;
  return (
    <div className={`rounded-xl border p-3 ${style.bg} ${style.border}`}>
      <div className="flex items-start justify-between gap-2 mb-1">
        <span className={`text-xs font-semibold ${style.text}`}>{style.label}</span>
        <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${style.bg} ${style.text}`}>
          MD {promo.md_pct}%
        </span>
      </div>
      <p className="text-slate-200 text-xs font-medium">{promo.categoria}</p>
      <p className="text-slate-400 text-xs mt-0.5 leading-relaxed">{promo.descripcion}</p>
    </div>
  );
}

export default function WeekPromoDetail({ week }) {
  if (!week) return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5 flex items-center justify-center h-48">
      <p className="text-slate-600 text-sm">Selecciona una semana en la gráfica</p>
    </div>
  );

  const allPromos = week.promos ?? [];
  const wknd = allPromos.filter(p => p.tipo_promo === "WkndPromo");
  const other = allPromos.filter(p => p.tipo_promo === "OtherPromo");
  const dd = allPromos.filter(p => p.tipo_promo === "DD");

  const formatCurrency = (v) => "$" + (v ?? 0).toLocaleString("en-US", { maximumFractionDigits: 0 });

  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-slate-200 font-semibold text-sm">
            Semana {week.semana_fiscal}
          </h3>
          <p className="text-slate-500 text-xs mt-0.5">
            {week.fecha_inicio} → {week.fecha_fin}
          </p>
        </div>
        <div className="text-right">
          <p className="text-white font-bold text-lg tabular-nums">
            {formatCurrency(week.total_sales)}
          </p>
          <p className="text-slate-500 text-xs">{week.transactions} transacciones</p>
        </div>
      </div>

      {/* MD promedio */}
      {week.has_promo && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-3 py-2 mb-4 flex items-center justify-between">
          <span className="text-amber-300 text-xs font-semibold">📊 MD promedio de la semana</span>
          <span className="text-amber-300 text-sm font-bold">{week.avg_md_pct}%</span>
        </div>
      )}

      {/* Promos */}
      {!week.has_promo ? (
        <p className="text-slate-600 text-sm text-center py-4">Sin promociones esta semana</p>
      ) : (
        <div className="flex flex-col gap-3 overflow-y-auto max-h-72">
          {wknd.length > 0 && wknd.map((p, i) => <PromoCard key={i} promo={p} />)}
          {other.length > 0 && other.map((p, i) => <PromoCard key={i} promo={p} />)}
          {dd.length > 0 && dd.map((p, i) => <PromoCard key={i} promo={p} />)}
        </div>
      )}
    </div>
  );
}
