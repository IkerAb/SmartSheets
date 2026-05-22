// src/pages/FiscalCalendarPage.jsx
import { useEffect, useState } from "react";
import { getFiscalCalendar } from "../services/api";
import FiscalCalendarChart from "../components/charts/FiscalCalendarChart";
import WeekPromoDetail from "../components/ui/WeekPromoDetail";

function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

export default function FiscalCalendarPage({ datasetId, promoId }) {
  const [weeks, setWeeks]               = useState([]);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);
  const [selectedWeek, setSelectedWeek] = useState(null);

  useEffect(() => {
    async function load() {
      if (!datasetId || !promoId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await getFiscalCalendar({ dataset_id: datasetId, promo_id: promoId });
        setWeeks(data.weeks ?? []);
        if (data.weeks?.length) {
          const best = data.weeks.reduce((a, b) => a.total_sales > b.total_sales ? a : b);
          setSelectedWeek(best);
        }
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [datasetId, promoId]);

  if (!datasetId || !promoId) {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-center">
        <div className="text-6xl mb-4">📅</div>
        <h2 className="text-slate-200 text-xl font-semibold mb-2">Calendario Fiscal</h2>
        <p className="text-slate-500 text-sm max-w-sm">
          Necesitas subir un archivo de ventas y un calendario de promociones.
        </p>
      </div>
    );
  }

  if (loading) return <Spinner />;
  if (error) return (
    <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl px-4 py-3 text-sm">
      {error}
    </div>
  );

  const totalSales     = weeks.reduce((a, b) => a + b.total_sales, 0);
  const weeksWithPromo = weeks.filter(w => w.has_promo).length;
  const avgMD          = weeks.filter(w => w.has_promo).reduce((a, b) => a + b.avg_md_pct, 0) / (weeksWithPromo || 1);
  const bestWeek       = weeks.reduce((a, b) => a.total_sales > b.total_sales ? a : b, weeks[0]);

  return (
    <div className="flex flex-col gap-6">

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-4">
          <p className="text-slate-400 text-xs mb-1">Total Anual</p>
          <p className="text-white text-2xl font-bold tabular-nums">
            ${totalSales.toLocaleString("en-US", { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-4">
          <p className="text-slate-400 text-xs mb-1">Semanas con Promo</p>
          <p className="text-white text-2xl font-bold">
            {weeksWithPromo} <span className="text-slate-500 text-sm">/ {weeks.length}</span>
          </p>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-4">
          <p className="text-slate-400 text-xs mb-1">MD Promedio</p>
          <p className="text-amber-400 text-2xl font-bold">{avgMD.toFixed(1)}%</p>
        </div>
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-4">
          <p className="text-slate-400 text-xs mb-1">Mejor Semana</p>
          <p className="text-white text-2xl font-bold">S{bestWeek?.semana_fiscal}</p>
          <p className="text-emerald-400 text-xs">
            ${bestWeek?.total_sales.toLocaleString("en-US", { maximumFractionDigits: 0 })}
          </p>
        </div>
      </div>

      {/* Gráfica */}
      <FiscalCalendarChart
        weeks={weeks}
        selectedWeek={selectedWeek}
        onSelectWeek={setSelectedWeek}
      />

      {/* Selector de semana + detalle */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        {/* Selector + detalle de promo */}
        <div className="flex flex-col gap-3">
          {/* Dropdown selector */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-4 flex items-center gap-4">
            <label className="text-slate-400 text-sm font-medium whitespace-nowrap">
              Ver semana:
            </label>
            <select
              value={selectedWeek?.semana_fiscal ?? ""}
              onChange={(e) => {
                const w = weeks.find(w => w.semana_fiscal === parseInt(e.target.value));
                if (w) setSelectedWeek(w);
              }}
              className="flex-1 bg-slate-900 border border-slate-700 text-slate-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
            >
              {weeks.map((w) => (
                <option key={w.semana_fiscal} value={w.semana_fiscal}>
                  Semana {w.semana_fiscal} — {w.fecha_inicio} {w.has_promo ? `· MD ${w.avg_md_pct}%` : "· Sin promo"}
                </option>
              ))}
            </select>
          </div>

          {/* Detalle de la semana */}
          <WeekPromoDetail week={selectedWeek} />
        </div>

        {/* Top 5 semanas */}
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
          <h3 className="text-slate-300 text-sm font-semibold mb-4">Top 5 Semanas por Ventas</h3>
          <div className="flex flex-col gap-2">
            {[...weeks]
              .sort((a, b) => b.total_sales - a.total_sales)
              .slice(0, 5)
              .map((w, i) => (
                <div
                  key={w.semana_fiscal}
                  onClick={() => setSelectedWeek(w)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-colors ${
                    selectedWeek?.semana_fiscal === w.semana_fiscal
                      ? "bg-indigo-500/20 border border-indigo-500/30"
                      : "bg-slate-900/50 hover:bg-slate-700/50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-slate-600 text-xs w-4">{i + 1}</span>
                    <div>
                      <p className="text-slate-200 text-xs font-medium">Semana {w.semana_fiscal}</p>
                      <p className="text-slate-500 text-xs">{w.fecha_inicio} → {w.fecha_fin}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-white text-xs font-semibold tabular-nums">
                      ${w.total_sales.toLocaleString("en-US", { maximumFractionDigits: 0 })}
                    </p>
                    {w.has_promo && (
                      <p className="text-amber-400 text-xs">MD {w.avg_md_pct}%</p>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>

    </div>
  );
}
