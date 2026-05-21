// src/components/layout/DashboardLayout.jsx
// Sidebar fijo + topbar + área de contenido scrollable.
// Recibe: activePage (string), onNavigate (fn), children

const navItems = [
  { id: "dashboard", label: "Dashboard",   icon: "▦" },
  { id: "forecast",  label: "Forecast",    icon: "⟋" },
  { id: "simulate",  label: "Simulate",    icon: "⧖" },
  { id: "upload",    label: "Upload Data", icon: "↑" },
];

export default function DashboardLayout({ activePage, onNavigate, children, datasetId, health }) {
  const dbOk = health?.database === "connected";

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="w-56 flex-shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col">
        {/* Logo */}
        <div className="px-5 py-5 border-b border-slate-800">
          <span className="text-white font-bold text-lg tracking-tight">Smart<span className="text-indigo-400">Sheets</span></span>
          <p className="text-slate-600 text-xs mt-0.5">Analytics Platform</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
          {navItems.map((item) => {
            const active = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors text-left ${
                  active
                    ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/20"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                <span className="text-base leading-none">{item.icon}</span>
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Footer del sidebar */}
        <div className="px-4 py-4 border-t border-slate-800">
          <div className="flex items-center gap-2 text-xs">
            <span className={`w-2 h-2 rounded-full ${dbOk ? "bg-emerald-400" : "bg-rose-400"}`} />
            <span className="text-slate-500">{dbOk ? "DB connected" : "DB unreachable"}</span>
          </div>
          {health?.version && (
            <p className="text-slate-700 text-xs mt-1">v{health.version}</p>
          )}
        </div>
      </aside>

      {/* ── Main area ────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="h-14 border-b border-slate-800 bg-slate-900/50 backdrop-blur flex items-center justify-between px-6 flex-shrink-0">
          <div>
            <span className="text-slate-200 font-semibold capitalize">{activePage}</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            {datasetId ? (
              <span className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 font-mono text-slate-400">
                dataset: <span className="text-indigo-400">{datasetId.slice(0, 8)}…</span>
              </span>
            ) : (
              <span className="text-amber-500/80">No dataset loaded — upload a file first</span>
            )}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
