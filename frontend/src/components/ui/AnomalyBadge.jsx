// src/components/ui/AnomalyBadge.jsx
// Consume el array anomalies de GET /insights
// Cada anomaly: { date, value, direction: "spike"|"dip", severity: "low"|"medium"|"high" }

const severityStyles = {
  high:   "bg-rose-500/15 border-rose-500/30 text-rose-300",
  medium: "bg-amber-500/15 border-amber-500/30 text-amber-300",
  low:    "bg-slate-500/15 border-slate-500/30 text-slate-300",
};

const directionIcon = { spike: "↑", dip: "↓" };

function formatCurrency(v) {
  return "$" + v.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

export default function AnomalyBadge({ anomaly }) {
  const { date, value, direction, severity } = anomaly;
  return (
    <div
      className={`flex items-center justify-between px-3 py-2 rounded-lg border text-xs font-medium ${severityStyles[severity]}`}
    >
      <span className="flex items-center gap-1.5">
        <span className="text-base leading-none">{directionIcon[direction]}</span>
        <span>{date}</span>
      </span>
      <span className="tabular-nums">{formatCurrency(value)}</span>
      <span className="capitalize opacity-70">{severity}</span>
    </div>
  );
}
