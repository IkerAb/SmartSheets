// src/pages/ForecastDashboard.jsx
import { useEffect, useState, useMemo } from "react";
import { getInsights, getForecast, runSimulation } from "../services/api";
import KPICard from "../components/ui/KPICard";
import AnomalyBadge from "../components/ui/AnomalyBadge";
import { TopProductsTable, MonthlyGrowthTable, StoresTable } from "../components/ui/MetricsTable";
import ForecastLineChart from "../components/charts/ForecastLineChart";
import InsightsBarChart from "../components/charts/InsightsBarChart";
import SimulationChart from "../components/charts/SimulationChart";

function formatCurrency(v) {
  return "$" + (v ?? 0).toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

function ErrorBanner({ message }) {
  return (
    <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl px-4 py-3 text-sm">
      {message}
    </div>
  );
}

// ── Dashboard tab ─────────────────────────────────────────────────────────────
function DashboardTab({ insights, forecast, selectedMonth, setSelectedMonth, filteredChart }) {
  const growth = insights?.monthly_growth ?? [];
  const months = growth.map(m => m.month);
  const lastMoM = growth[growth.length - 1]?.mom_pct ?? 0;

  return (
    <div className="flex flex-col gap-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard label="Total Revenue" value={insights?.total_sales} formatter={formatCurrency}
          trend={lastMoM} sub={`${insights?.total_transactions?.toLocaleString()} transactions`} />
        <KPICard label="Avg. Ticket" value={insights?.avg_ticket} formatter={formatCurrency} sub="per transaction" />
        <KPICard label="Forecast MAE" value={forecast?.mae}
          formatter={(v) => v ? "$" + v.toFixed(0) : "N/A"} sub={`Model: ${forecast?.model?.toUpperCase()}`} />
        <KPICard label="Forecast Horizon" value={forecast?.horizon}
          formatter={(v) => `${v} days`} sub={`${((forecast?.confidence ?? 0) * 100).toFixed(0)}% confidence`} />
      </div>

      {/* Summary */}
      {insights?.natural_summary && (
        <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-2xl px-5 py-4 text-sm text-slate-300 leading-relaxed">
          <span className="text-indigo-400 font-semibold mr-2">💡 Summary:</span>
          {insights.natural_summary}
        </div>
      )}

      {/* Selector de mes + bar chart */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-slate-200 font-semibold text-sm">Ventas Diarias por Mes</h3>
            <p className="text-slate-500 text-xs mt-0.5">Selecciona un mes para filtrar</p>
          </div>
          <select
            value={selectedMonth ?? ""}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          >
            {months.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <InsightsBarChart chart_ready={filteredChart} title={`Ventas — ${selectedMonth ?? "All"}`} />
      </div>

      {/* Anomalías */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
        <h3 className="text-slate-300 text-sm font-semibold mb-4">Anomalías Detectadas</h3>
        <div className="flex flex-col gap-2">
          {(insights?.anomalies ?? []).length === 0
            ? <p className="text-slate-600 text-sm">No se encontraron anomalías.</p>
            : insights.anomalies.map((a) => <AnomalyBadge key={a.date} anomaly={a} />)
          }
        </div>
      </div>

      {/* Tablas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TopProductsTable products={insights?.top_products} />
        <MonthlyGrowthTable monthly_growth={insights?.monthly_growth} />
      </div>
      <StoresTable store_insights={insights?.store_insights} />
    </div>
  );
}

// ── Forecast tab ──────────────────────────────────────────────────────────────
function ForecastTab({ forecast }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <KPICard label="Modelo" value={forecast?.model?.toUpperCase()} formatter={(v) => v} />
        <KPICard label="MAE" value={forecast?.mae} formatter={(v) => v ? "$" + v.toFixed(0) : "N/A"} sub="Error histórico" />
        <KPICard label="Horizonte" value={forecast?.horizon} formatter={(v) => `${v} días`}
          sub={`${((forecast?.confidence ?? 0) * 100).toFixed(0)}% confianza`} />
      </div>
      {forecast?.warnings?.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3 text-xs text-amber-300">
          ⚠️ {forecast.warnings.join(" · ")}
        </div>
      )}
      <ForecastLineChart
        series={forecast?.series ?? []}
        mae={forecast?.mae}
        model={forecast?.model}
        confidence={forecast?.confidence}
      />
    </div>
  );
}

// ── Simulate tab ──────────────────────────────────────────────────────────────
function SimulateTab({ datasetId, simulate, setSimulate }) {
  const [priceModifier, setPriceModifier]   = useState(1.2);
  const [volumeModifier, setVolumeModifier] = useState(0.85);
  const [simRunning, setSimRunning]         = useState(false);
  const [error, setError]                   = useState(null);

  async function handleSimulate() {
    setSimRunning(true);
    setError(null);
    try {
      const { runSimulation } = await import("../services/api");
      const sim = await runSimulation({ dataset_id: datasetId, price_modifier: priceModifier, volume_modifier: volumeModifier });
      setSimulate(sim);
    } catch (e) {
      setError(e.message);
    } finally {
      setSimRunning(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5">
        <h3 className="text-slate-200 font-semibold text-sm mb-4">Controles de Simulación</h3>
        {error && <div className="bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl px-4 py-3 text-xs mb-4">{error}</div>}
        <div className="flex flex-wrap items-end gap-4 mb-5">
          <div>
            <label className="block text-slate-400 text-xs mb-1.5">Price modifier</label>
            <input type="number" step="0.05" min="0.5" max="2" value={priceModifier}
              onChange={(e) => setPriceModifier(parseFloat(e.target.value))}
              className="bg-slate-900 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm w-28 focus:outline-none focus:border-indigo-500" />
            <p className="text-slate-600 text-xs mt-1">1.20 = +20%</p>
          </div>
          <div>
            <label className="block text-slate-400 text-xs mb-1.5">Volume modifier</label>
            <input type="number" step="0.05" min="0.5" max="2" value={volumeModifier}
              onChange={(e) => setVolumeModifier(parseFloat(e.target.value))}
              className="bg-slate-900 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm w-28 focus:outline-none focus:border-indigo-500" />
            <p className="text-slate-600 text-xs mt-1">0.85 = -15%</p>
          </div>
          <button onClick={handleSimulate} disabled={simRunning}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">
            {simRunning ? "Calculando…" : "Run Simulation"}
          </button>
          <p className="text-slate-500 text-xs self-center">
            Efecto neto: ×{(priceModifier * volumeModifier).toFixed(3)} → {((priceModifier * volumeModifier - 1) * 100).toFixed(1)}% revenue
          </p>
        </div>
        <SimulationChart simulateData={simulate} />
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ForecastDashboard({ datasetId, activeTab }) {
  const [insights, setInsights] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [simulate, setSimulate] = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(null);

  useEffect(() => {
    async function load() {
      if (!datasetId) return;
      setLoading(true);
      setError(null);
      try {
        const [ins, fcast] = await Promise.all([
          getInsights({ dataset_id: datasetId }),
          getForecast({ dataset_id: datasetId, horizon: 30 }),
        ]);
        setInsights(ins);
        setForecast(fcast);
        if (ins?.monthly_growth?.length) {
          setSelectedMonth(ins.monthly_growth[ins.monthly_growth.length - 1].month);
        }
        const sim = await runSimulation({ dataset_id: datasetId, price_modifier: 1.2, volume_modifier: 0.85 });
        setSimulate(sim);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    if (datasetId) load();
  }, [datasetId]);

  const filteredChart = useMemo(() => {
    if (!insights?.chart_ready || !selectedMonth) return insights?.chart_ready;
    const { labels, values } = insights.chart_ready;
    const filtered = labels.reduce((acc, label, i) => {
      if (label.startsWith(selectedMonth)) { acc.labels.push(label); acc.values.push(values[i]); }
      return acc;
    }, { labels: [], values: [] });
    return filtered.labels.length > 0 ? filtered : insights.chart_ready;
  }, [insights, selectedMonth]);

  if (!datasetId) return (
    <div className="flex flex-col items-center justify-center py-32 text-center">
      <div className="text-6xl mb-4">↑</div>
      <h2 className="text-slate-200 text-xl font-semibold mb-2">No hay dataset cargado</h2>
      <p className="text-slate-500 text-sm">Ve a Upload Data y sube un archivo CSV o Excel.</p>
    </div>
  );

  if (loading) return <Spinner />;
  if (error)   return <ErrorBanner message={error} />;

  if (activeTab === "forecast") return <ForecastTab forecast={forecast} />;
  if (activeTab === "simulate") return <SimulateTab datasetId={datasetId} simulate={simulate} setSimulate={setSimulate} />;
  return (
    <DashboardTab
      insights={insights}
      forecast={forecast}
      selectedMonth={selectedMonth}
      setSelectedMonth={setSelectedMonth}
      filteredChart={filteredChart}
    />
  );
}
