// src/App.jsx
import { useState, useEffect } from "react";
import DashboardLayout from "./components/layout/DashboardLayout";
import ForecastDashboard from "./pages/ForecastDashboard";
import FiscalCalendarPage from "./pages/FiscalCalendarPage";
import { getHealth, uploadDataset, uploadPromotions } from "./services/api";

// ── Tabs de KPIs ──────────────────────────────────────────────────────────────
const KPI_TABS = [
  { id: "dashboard", label: "Dashboard" },
  { id: "forecast",  label: "Forecast"  },
  { id: "simulate",  label: "Simulate"  },
];

function KPITabs({ activeTab, onTabChange }) {
  return (
    <div className="flex items-center gap-1 bg-slate-800/60 border border-slate-700/50 rounded-xl p-1 mb-6 w-fit">
      {KPI_TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === tab.id
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

// ── Upload page ───────────────────────────────────────────────────────────────
function UploadPage({ onDatasetLoaded, onPromoLoaded, datasetId, promoId }) {
  const [uploadingDataset, setUploadingDataset] = useState(false);
  const [uploadingPromo, setUploadingPromo]     = useState(false);
  const [msgDataset, setMsgDataset]             = useState(null);
  const [msgPromo, setMsgPromo]                 = useState(null);

  async function handleDataset(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingDataset(true);
    setMsgDataset(null);
    try {
      const res = await uploadDataset(file);
      setMsgDataset({ type: "success", text: `✅ ${res.row_count} filas · ${res.products.length} categorías · ${res.date_range[0]} → ${res.date_range[1]}` });
      onDatasetLoaded(res.dataset_id);
    } catch (err) {
      setMsgDataset({ type: "error", text: err.message });
    } finally {
      setUploadingDataset(false);
    }
  }

  async function handlePromo(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingPromo(true);
    setMsgPromo(null);
    try {
      const res = await uploadPromotions(file);
      setMsgPromo({ type: "success", text: `✅ ${res.row_count} promos · ${res.semanas} semanas · ${res.categorias.length} categorías` });
      onPromoLoaded(res.promo_id);
    } catch (err) {
      setMsgPromo({ type: "error", text: err.message });
    } finally {
      setUploadingPromo(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center py-16 gap-6 max-w-lg mx-auto">
      {/* Dataset */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-8 w-full text-center">
        <div className="text-4xl mb-3">📂</div>
        <h2 className="text-slate-200 text-lg font-semibold mb-1">Archivo de Ventas</h2>
        <p className="text-slate-500 text-xs mb-5">CSV o Excel con columnas: fecha, producto, tienda, ventas</p>
        {datasetId && <p className="text-emerald-400 text-xs mb-3 font-mono">Activo: {datasetId.slice(0, 8)}…</p>}
        <label className="block cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl px-6 py-3 text-sm font-medium transition-colors">
          {uploadingDataset ? "Cargando…" : "Subir ventas"}
          <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleDataset} disabled={uploadingDataset} />
        </label>
        {msgDataset && (
          <div className={`mt-3 rounded-xl px-4 py-3 text-xs ${
            msgDataset.type === "success"
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
          }`}>{msgDataset.text}</div>
        )}
      </div>

      {/* Promos */}
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-8 w-full text-center">
        <div className="text-4xl mb-3">📅</div>
        <h2 className="text-slate-200 text-lg font-semibold mb-1">Calendario de Promociones</h2>
        <p className="text-slate-500 text-xs mb-5">CSV con columnas: semana_fiscal, fecha_inicio, fecha_fin, tipo_promo, categoria, descripcion, md_pct</p>
        {promoId && <p className="text-emerald-400 text-xs mb-3 font-mono">Activo: {promoId.slice(0, 8)}…</p>}
        <label className="block cursor-pointer bg-amber-600 hover:bg-amber-500 text-white rounded-xl px-6 py-3 text-sm font-medium transition-colors">
          {uploadingPromo ? "Cargando…" : "Subir calendario"}
          <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handlePromo} disabled={uploadingPromo} />
        </label>
        {msgPromo && (
          <div className={`mt-3 rounded-xl px-4 py-3 text-xs ${
            msgPromo.type === "success"
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
          }`}>{msgPromo.text}</div>
        )}
      </div>
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [activePage, setActivePage] = useState("kpis");
  const [activeTab, setActiveTab]   = useState("dashboard");
  const [datasetId, setDatasetId]   = useState(null);
  const [promoId, setPromoId]       = useState(null);
  const [health, setHealth]         = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => null);
  }, []);

  function handleNavigate(page) {
    setActivePage(page);
    if (page === "kpis") setActiveTab("dashboard");
  }

  function renderPage() {
    switch (activePage) {
      case "kpis":
        return (
          <div>
            <KPITabs activeTab={activeTab} onTabChange={setActiveTab} />
            <ForecastDashboard datasetId={datasetId} activeTab={activeTab} />
          </div>
        );
      case "calendar":
        return <FiscalCalendarPage datasetId={datasetId} promoId={promoId} />;
      case "upload":
        return (
          <UploadPage
            onDatasetLoaded={(id) => { setDatasetId(id); setActivePage("kpis"); }}
            onPromoLoaded={(id) => setPromoId(id)}
            datasetId={datasetId}
            promoId={promoId}
          />
        );
      default:
        return null;
    }
  }

  return (
    <DashboardLayout
      activePage={activePage}
      onNavigate={handleNavigate}
      datasetId={datasetId}
      promoId={promoId}
      health={health}
    >
      {renderPage()}
    </DashboardLayout>
  );
}
