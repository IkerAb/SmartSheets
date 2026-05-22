// src/services/api.js
// Capa de acceso a la API de SmartSheets (FastAPI).
// Mientras el backend no esté listo, cada función devuelve mock data.
// Para conectar al backend real: cambia USE_MOCK a false y asegúrate
// de que VITE_API_URL esté definida en tu .env

import {
  mockUploadResponse,
  mockInsightsResponse,
  mockForecastResponse,
  mockSimulateResponse,
  mockHealthResponse,
} from "../mock/forecastData";

const USE_MOCK = false; // conectado a FastAPI // ← cambia a false cuando FastAPI esté listo
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

// Helper interno — no exportar
async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "API error");
  }
  return res.json();
}

// ─── POST /upload ─────────────────────────────────────────────────────────────
// file: File object (del input type="file")
// Devuelve: { dataset_id, row_count, columns, date_range, products, status, message }
export async function uploadDataset(file) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 1200)); // simula latencia
    return mockUploadResponse;
  }
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

// ─── GET /insights ────────────────────────────────────────────────────────────
// params: { dataset_id, anomaly_method?, anomaly_threshold? }
// Devuelve: { total_sales, avg_ticket, total_transactions, top_products,
//             monthly_growth, anomalies, natural_summary, chart_ready }
export async function getInsights({
  dataset_id,
  anomaly_method = "zscore",
  anomaly_threshold = 2.5,
} = {}) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 800));
    return mockInsightsResponse;
  }
  const params = new URLSearchParams({ dataset_id, anomaly_method, anomaly_threshold });
  return request(`/insights?${params}`);
}

// ─── GET /forecast ────────────────────────────────────────────────────────────
// params: { dataset_id, horizon?, product?, confidence?, aggregation? }
// Devuelve: { model, horizon, labels, values, lower, upper, mae, warnings, series }
export async function getForecast({
  dataset_id,
  horizon = 30,
  product = null,
  confidence = 0.9,
  aggregation = "day",
} = {}) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 900));
    return mockForecastResponse;
  }
  const params = new URLSearchParams({ dataset_id, horizon, confidence, aggregation });
  if (product) params.append("product", product);
  return request(`/forecast?${params}`);
}

// ─── POST /simulate ───────────────────────────────────────────────────────────
// body: { dataset_id, horizon?, price_modifier?, volume_modifier?, product? }
// Devuelve: { base, simulated, delta_revenue, delta_pct, modifiers }
export async function runSimulation({
  dataset_id,
  horizon = 30,
  price_modifier = 1.0,
  volume_modifier = 1.0,
  product = null,
} = {}) {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 1000));
    return mockSimulateResponse;
  }
  return request("/simulate", {
    method: "POST",
    body: JSON.stringify({ dataset_id, horizon, price_modifier, volume_modifier, product }),
  });
}

// ─── GET /health ──────────────────────────────────────────────────────────────
// Devuelve: { status, version, environment, database, uptime_seconds }
export async function getHealth() {
  if (USE_MOCK) return mockHealthResponse;
  return request("/health");
}

// ─── POST /promotions/upload ──────────────────────────────────────────────────
export async function uploadPromotions(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/promotions/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Promotion upload failed");
  return res.json();
}

// ─── GET /promotions/{promo_id}/calendar ─────────────────────────────────────
export async function getFiscalCalendar({ dataset_id, promo_id } = {}) {
  const params = new URLSearchParams({ dataset_id });
  const res = await fetch(`${BASE_URL}/promotions/${promo_id}/calendar?${params}`);
  if (!res.ok) throw new Error("Failed to load fiscal calendar");
  return res.json();
}

// ─── GET /promotions/{promo_id}/week/{semana} ─────────────────────────────────
export async function getWeekPromotions({ promo_id, semana } = {}) {
  const res = await fetch(`${BASE_URL}/promotions/${promo_id}/week/${semana}`);
  if (!res.ok) throw new Error("Failed to load week promotions");
  return res.json();
}

// ─── POST /inventory/upload ───────────────────────────────────────────────────
export async function uploadInventory(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/inventory/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Inventory upload failed");
  return res.json();
}

// ─── GET /inventory/{id}/sellthrough ─────────────────────────────────────────
export async function getSellThrough({ inventory_id, semana, promo_id } = {}) {
  const params = new URLSearchParams();
  if (semana) params.append("semana", semana);
  if (promo_id) params.append("promo_id", promo_id);
  const res = await fetch(`${BASE_URL}/inventory/${inventory_id}/sellthrough?${params}`);
  if (!res.ok) throw new Error("Failed to load sell-through");
  return res.json();
}

// ─── POST /traffic/upload ─────────────────────────────────────────────────────
export async function uploadTraffic(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/traffic/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error("Traffic upload failed");
  return res.json();
}

// ─── GET /traffic/{id}/conversion ────────────────────────────────────────────
export async function getTrafficConversion({ traffic_id, semana } = {}) {
  const params = new URLSearchParams();
  if (semana) params.append("semana", semana);
  const res = await fetch(`${BASE_URL}/traffic/${traffic_id}/conversion?${params}`);
  if (!res.ok) throw new Error("Failed to load traffic conversion");
  return res.json();
}
