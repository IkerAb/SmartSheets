// src/App.jsx
import { useState, useEffect } from "react";
import DashboardLayout from "./components/layout/DashboardLayout";
import ForecastDashboard from "./pages/ForecastDashboard";
import FiscalCalendarPage from "./pages/FiscalCalendarPage";
import { getHealth, uploadDataset, uploadPromotions, uploadInventory, uploadTraffic } from "./services/api";

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

function UploadCard({ icon, title, desc, activeId, onUpload, uploading, msg, color = "indigo", buttonLabel }) {
  const colors = {
    indigo:  "bg-indigo-600 hover:bg-indigo-500",
    amber:   "bg-amber-600 hover:bg-amber-500",
    emerald: "bg-emerald-600 hover:bg-emerald-500",
    cyan:    "bg-cyan-600 hover:bg-cyan-500",
  };
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-6 w-full text-center">
      <div className="text-4xl mb-3">{icon}</div>
      <h2 className="text-slate-200 text-lg font-semibold mb-1">{title}</h2>
      <p className="text-slate-500 text-xs mb-5">{desc}</p>
      {activeId && <p className="text-emerald-400 text-xs mb-3 font-mono">Activo: {activeId.slice(0, 8)}…</p>}
      <label className={`block cursor-pointer ${colors[color]} text-white rounded-xl px-6 py-3 text-sm font-medium transition-colors`}>
        {uploading ? "Cargando…" : buttonLabel}
        <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={onUpload} disabled={uploading} />
      </label>
      {msg && (
        <div className={`mt-3 rounded-xl px-4 py-3 text-xs ${
          msg.type === "success"
            ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
            : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
        }`}>{msg.text}</div>
      )}
    </div>
  );
}

function UploadPage({ onDatasetLoaded, onPromoLoaded, onInventoryLoaded, onTrafficLoaded,
                      datasetId, promoId, inventoryId, trafficId }) {
  const [states, setStates] = useState({
    uploadingDataset: false, uploadingPromo: false,
    uploadingInventory: false, uploadingTraffic: false,
    msgDataset: null, msgPromo: null, msgInventory: null, msgTraffic: null,
  });

  function set(key, val) { setStates(s => ({ ...s, [key]: val })); }

  async function handle(uploadFn, loadingKey, msgKey, onLoaded, e) {
    const file = e.target.files?.[0];
    if (!file) return;
    set(loadingKey, true); set(msgKey, null);
    try {
      const res = await uploadFn(file);
      const text = res.row_count
        ? `✅ ${res.row_count} registros cargados correctamente`
        : "✅ Cargado correctamente";
      set(msgKey, { type: "success", text });
      onLoaded(res[Object.keys(res).find(k => k.endsWith("_id"))]);
    } catch (err) {
      set(msgKey, { type: "error", text: err.message });
    } finally {
      set(loadingKey, false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 max-w-3xl mx-auto py-8">
      <UploadCard
        icon="📂" title="Ventas" color="indigo"
        desc="fecha, producto, tienda, ventas"
        activeId={datasetId} uploading={states.uploadingDataset} msg={states.msgDataset}
        onUpload={(e) => handle(uploadDataset, "uploadingDataset", "msgDataset", onDatasetLoaded, e)}
        buttonLabel="Subir ventas"
      />
      <UploadCard
        icon="📅" title="Promociones" color="amber"
        desc="semana_fiscal, fecha_inicio, fecha_fin, tipo_promo, categoria, descripcion, md_pct"
        activeId={promoId} uploading={states.uploadingPromo} msg={states.msgPromo}
        onUpload={(e) => handle(uploadPromotions, "uploadingPromo", "msgPromo", onPromoLoaded, e)}
        buttonLabel="Subir calendario"
      />
      <UploadCard
        icon="📦" title="Inventario" color="emerald"
        desc="semana_fiscal, categoria, tienda, inventario_inicial, unidades_vendidas"
        activeId={inventoryId} uploading={states.uploadingInventory} msg={states.msgInventory}
        onUpload={(e) => handle(uploadInventory, "uploadingInventory", "msgInventory", onInventoryLoaded, e)}
        buttonLabel="Subir inventario"
      />
      <UploadCard
        icon="🚶" title="Tráfico" color="cyan"
        desc="semana_fiscal, tienda, trafico, transacciones, tasa_conversion_pct"
        activeId={trafficId} uploading={states.uploadingTraffic} msg={states.msgTraffic}
        onUpload={(e) => handle(uploadTraffic, "uploadingTraffic", "msgTraffic", onTrafficLoaded, e)}
        buttonLabel="Subir tráfico"
      />
    </div>
  );
}

export default function App() {
  const [activePage,  setActivePage]  = useState("kpis");
  const [activeTab,   setActiveTab]   = useState("dashboard");
  const [datasetId,   setDatasetId]   = useState(null);
  const [promoId,     setPromoId]     = useState(null);
  const [inventoryId, setInventoryId] = useState(null);
  const [trafficId,   setTrafficId]   = useState(null);
  const [health,      setHealth]      = useState(null);

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
        return (
          <FiscalCalendarPage
            datasetId={datasetId}
            promoId={promoId}
            inventoryId={inventoryId}
            trafficId={trafficId}
          />
        );
      case "upload":
        return (
          <UploadPage
            onDatasetLoaded={(id) => { setDatasetId(id); setActivePage("kpis"); }}
            onPromoLoaded={setPromoId}
            onInventoryLoaded={setInventoryId}
            onTrafficLoaded={setTrafficId}
            datasetId={datasetId}
            promoId={promoId}
            inventoryId={inventoryId}
            trafficId={trafficId}
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
      inventoryId={inventoryId}
      trafficId={trafficId}
      health={health}
    >
      {renderPage()}
    </DashboardLayout>
  );
}
