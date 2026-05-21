// src/mock/forecastData.js
// Mock data que replica exactamente los response schemas de la API documentada.
// Cuando FastAPI tenga los endpoints listos, basta con descomentar las llamadas
// en services/api.js y dejar de importar desde aquí.

// ─── POST /upload response ────────────────────────────────────────────────────
export const mockUploadResponse = {
  dataset_id: "1ce4a1a1-0d69-4a1b-bd2d-de71d3554afa",
  row_count: 1825,
  columns: ["fecha", "producto", "ventas"],
  date_range: ["2023-01-01", "2023-12-31"],
  products: ["Auriculares BT", "Laptop Pro", "Mouse Inalámbrico", "Teclado Mecánico", "Monitor 4K"],
  status: "cleaned",
  message: "Dataset uploaded and processed successfully.",
};

// ─── GET /insights response ───────────────────────────────────────────────────
export const mockInsightsResponse = {
  total_sales: 482310.5,
  avg_ticket: 264.28,
  total_transactions: 1825,
  top_products: [
    { name: "Laptop Pro",         total: 198400.0, pct: 41.1 },
    { name: "Monitor 4K",         total: 102300.0, pct: 21.2 },
    { name: "Auriculares BT",     total:  84200.0, pct: 17.5 },
    { name: "Teclado Mecánico",   total:  58100.0, pct: 12.0 },
    { name: "Mouse Inalámbrico",  total:  39310.5, pct:  8.2 },
  ],
  monthly_growth: [
    { month: "2023-01", sales: 31200, mom_pct: null },
    { month: "2023-02", sales: 33800, mom_pct:  8.3 },
    { month: "2023-03", sales: 38400, mom_pct: 13.6 },
    { month: "2023-04", sales: 35900, mom_pct: -6.5 },
    { month: "2023-05", sales: 42100, mom_pct: 17.3 },
    { month: "2023-06", sales: 39800, mom_pct: -5.5 },
    { month: "2023-07", sales: 44200, mom_pct: 11.1 },
    { month: "2023-08", sales: 47600, mom_pct:  7.7 },
    { month: "2023-09", sales: 45300, mom_pct: -4.8 },
    { month: "2023-10", sales: 49800, mom_pct:  9.9 },
    { month: "2023-11", sales: 68910, mom_pct: 38.4 }, // Black Friday
    { month: "2023-12", sales: 55310, mom_pct: -19.7 },
  ],
  anomalies: [
    { date: "2023-11-24", value: 8420.0, direction: "spike", severity: "high" },
    { date: "2023-07-04", value: 310.5,  direction: "dip",   severity: "medium" },
    { date: "2023-03-17", value: 6180.0, direction: "spike", severity: "low" },
  ],
  natural_summary:
    "Your best month was November 2023 with $68,910 in sales, driven by a Black Friday spike on the 24th. " +
    "Laptop Pro accounts for 41% of total revenue. Overall growth from January to December was +77%.",
  chart_ready: {
    // Muestra de 30 días de datos diarios listos para graficar
    labels: Array.from({ length: 30 }, (_, i) => {
      const d = new Date("2023-12-01");
      d.setDate(d.getDate() + i);
      return d.toISOString().split("T")[0];
    }),
    values: [
      1820, 1940, 1760, 2100, 2380, 1650, 1490,
      2010, 2150, 1980, 2340, 2560, 1870, 1720,
      2080, 2290, 2140, 2470, 2680, 1940, 1810,
      2200, 2390, 2250, 2610, 2830, 2100, 1980,
      2320, 2540,
    ],
  },
};

// ─── GET /forecast response ───────────────────────────────────────────────────
// Combina histórico (type: "actual") + predicción (type: "forecast")
// para que ForecastLineChart pueda distinguirlos.

const historicalDates = Array.from({ length: 60 }, (_, i) => {
  const d = new Date("2023-11-01");
  d.setDate(d.getDate() + i);
  return d.toISOString().split("T")[0];
});

const historicalValues = [
  1820, 1940, 1760, 2100, 2380, 1650, 1490, 2010, 2150, 1980,
  2340, 2560, 1870, 1720, 2080, 2290, 2140, 2470, 2680, 1940,
  1810, 2200, 2390, 2250, 2610, 2830, 8420, 3100, 2980, 2540, // spike Black Friday día 27
  2100, 1980, 2320, 2200, 2050, 1920, 1840, 2010, 2180, 2090,
  1960, 2140, 2310, 2200, 2080, 1970, 1890, 2060, 2230, 2140,
  2000, 2180, 2350, 2240, 2120, 2010, 1930, 2100, 2270, 2180,
];

const forecastDates = Array.from({ length: 30 }, (_, i) => {
  const d = new Date("2024-01-30");
  d.setDate(d.getDate() + i);
  return d.toISOString().split("T")[0];
});

const forecastValues  = [2210, 2280, 2190, 2350, 2430, 2310, 2180, 2380, 2460, 2340, 2500, 2590, 2450, 2320, 2520, 2610, 2470, 2340, 2540, 2630, 2490, 2360, 2560, 2650, 2510, 2380, 2580, 2670, 2530, 2400];
const lowerValues     = [1900, 1960, 1880, 2020, 2090, 1990, 1880, 2050, 2120, 2010, 2150, 2230, 2110, 1990, 2170, 2250, 2130, 2010, 2200, 2280, 2150, 2040, 2210, 2290, 2160, 2050, 2220, 2300, 2180, 2070];
const upperValues     = [2520, 2600, 2500, 2680, 2770, 2630, 2480, 2710, 2800, 2670, 2850, 2950, 2790, 2650, 2870, 2970, 2810, 2670, 2880, 2980, 2830, 2680, 2910, 3010, 2860, 2710, 2940, 3040, 2880, 2730];

export const mockForecastResponse = {
  model: "ets",
  horizon: 30,
  aggregation: "day",
  confidence: 0.90,
  mae: 312.4,
  warnings: [],
  // Arrays para el endpoint real
  labels: forecastDates,
  values: forecastValues,
  lower: lowerValues,
  upper: upperValues,
  // Serie combinada para el gráfico (histórico + forecast)
  // El ForecastLineChart usa este array directamente.
  series: [
    ...historicalDates.map((date, i) => ({
      date,
      actual:   historicalValues[i],
      forecast: null,
      lower:    null,
      upper:    null,
    })),
    ...forecastDates.map((date, i) => ({
      date,
      actual:   null,
      forecast: forecastValues[i],
      lower:    lowerValues[i],
      upper:    upperValues[i],
    })),
  ],
};

// ─── POST /simulate response ──────────────────────────────────────────────────
export const mockSimulateResponse = {
  base: {
    labels: forecastDates,
    values: forecastValues,
    total_projected: forecastValues.reduce((a, b) => a + b, 0),
  },
  simulated: {
    labels: forecastDates,
    // price +20%, volume -15% → neto ×1.02
    values: forecastValues.map((v) => parseFloat((v * 1.02).toFixed(2))),
    total_projected: parseFloat(
      forecastValues.reduce((a, b) => a + b * 1.02, 0).toFixed(2)
    ),
  },
  delta_revenue: parseFloat(
    forecastValues.reduce((a, b) => a + b * 0.02, 0).toFixed(2)
  ),
  delta_pct: 2.0,
  modifiers: { price_modifier: 1.2, volume_modifier: 0.85 },
};

// ─── GET /health response ─────────────────────────────────────────────────────
export const mockHealthResponse = {
  status: "ok",
  version: "0.1.0",
  environment: "development",
  database: "connected",
  uptime_seconds: 3420.5,
};
