// src/App.jsx
// Punto de entrada limpio. Maneja:
// - qué página está activa
// - el dataset_id activo (se propaga a todas las páginas)
// - llamada inicial a /health

import { useState, useEffect } from "react";
import DashboardLayout from "./components/layout/DashboardLayout";
import ForecastDashboard from "./pages/ForecastDashboard";
import { getHealth, uploadDataset } from "./services/api";
import { mockUploadResponse } from "./mock/forecastData";

function UploadPage({ onDatasetLoaded }) {
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState(null);

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMsg(null);
    try {
      const res = await uploadDataset(file);
      setMsg({ type: "success", text: `Loaded: ${res.row_count} rows · ${res.products.length} products · ${res.date_range[0]} → ${res.date_range[1]}` });
      onDatasetLoaded(res.dataset_id);
    } catch (err) {
      setMsg({ type: "error", text: err.message });
    } finally {
      setUploading(false);
    }
  }

  // En modo mock, carga el dataset de muestra directamente
  function loadMockDataset() {
    onDatasetLoaded(mockUploadResponse.dataset_id);
  }

  return (
    <div className="flex flex-col items-center justify-center py-24 gap-6">
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-10 w-full max-w-md text-center">
        <div className="text-5xl mb-4">📂</div>
        <h2 className="text-slate-200 text-xl font-semibold mb-2">Upload Dataset</h2>
        <p className="text-slate-500 text-sm mb-6">CSV or Excel with columns: fecha, producto, ventas</p>

        <label className="block cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl px-6 py-3 text-sm font-medium transition-colors mb-3">
          {uploading ? "Uploading…" : "Choose file"}
          <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={handleFile} disabled={uploading} />
        </label>

        <button
          onClick={loadMockDataset}
          className="text-slate-500 hover:text-slate-300 text-xs underline underline-offset-2 transition-colors"
        >
          or load mock dataset
        </button>

        {msg && (
          <div className={`mt-4 rounded-xl px-4 py-3 text-sm ${
            msg.type === "success"
              ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border border-rose-500/20 text-rose-300"
          }`}>
            {msg.text}
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [datasetId, setDatasetId]   = useState(null);
  const [health, setHealth]         = useState(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => null);
    // Pre-carga el mock dataset para que el dashboard se vea inmediatamente
    setDatasetId(mockUploadResponse.dataset_id);
  }, []);

  function renderPage() {
    switch (activePage) {
      case "dashboard":
      case "forecast":
        return <ForecastDashboard datasetId={datasetId} />;
      case "simulate":
        return <ForecastDashboard datasetId={datasetId} />;
      case "upload":
        return <UploadPage onDatasetLoaded={(id) => { setDatasetId(id); setActivePage("dashboard"); }} />;
      default:
        return <ForecastDashboard datasetId={datasetId} />;
    }
  }

  return (
    <DashboardLayout
      activePage={activePage}
      onNavigate={setActivePage}
      datasetId={datasetId}
      health={health}
    >
      {renderPage()}
    </DashboardLayout>
  );
}
