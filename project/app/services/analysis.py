"""
app/services/analysis.py
─────────────────────────
Calcula KPIs de negocio: ventas totales, top productos, crecimiento MoM,
ticket promedio, y genera resumen en lenguaje natural.
"""
from __future__ import annotations

import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalysisService:

    def compute_insights(self, df: pd.DataFrame) -> dict:
        logger.info("Computing insights for %d rows", len(df))

        # normalizar fecha sin timezone para operaciones de resample
        df = df.copy()
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.tz_localize(None)

        total_sales = float(df["ventas"].sum())
        total_tx = len(df)
        avg_ticket = total_sales / total_tx if total_tx else 0.0

        top_products = self._top_products(df, total_sales)
        monthly = self._monthly_growth(df)
        chart = self._chart_data(df)
        summary = self._natural_summary(total_sales, avg_ticket, monthly, top_products)

        return {
            "total_sales": round(total_sales, 2),
            "avg_ticket": round(avg_ticket, 2),
            "total_transactions": total_tx,
            "top_products": top_products,
            "monthly_growth": monthly,
            "chart_ready": chart,
            "natural_summary": summary,
        }

    def _top_products(self, df: pd.DataFrame, total_sales: float, n: int = 5) -> list[dict]:
        grouped = (
            df.groupby("producto")["ventas"]
            .sum()
            .sort_values(ascending=False)
            .head(n)
        )
        return [
            {
                "name": prod,
                "total": round(float(val), 2),
                "pct_of_total": round(float(val) / total_sales * 100, 1) if total_sales else 0.0,
            }
            for prod, val in grouped.items()
        ]

    def _monthly_growth(self, df: pd.DataFrame) -> list[dict]:
        monthly = (
            df.set_index("fecha")["ventas"]
            .resample("ME")
            .sum()
            .reset_index()
        )
        monthly["month"] = monthly["fecha"].dt.strftime("%Y-%m")
        monthly["pct_change"] = monthly["ventas"].pct_change() * 100
        result = []
        for _, row in monthly.iterrows():
            result.append({
                "month": row["month"],
                "total": round(float(row["ventas"]), 2),
                "pct_change": round(float(row["pct_change"]), 1)
                if not pd.isna(row["pct_change"]) else None,
            })
        return result

    def _chart_data(self, df: pd.DataFrame) -> dict:
        daily = (
            df.set_index("fecha")["ventas"]
            .resample("D")
            .sum()
            .fillna(0)
        )
        return {
            "labels": [d.strftime("%Y-%m-%d") for d in daily.index],
            "values": [round(float(v), 2) for v in daily.values],
        }

    def _natural_summary(self, total, avg_ticket, monthly, top) -> str:
        lines = [
            f"Total sales amount to ${total:,.2f} with an average ticket of ${avg_ticket:,.2f}."
        ]
        if monthly:
            best = max(monthly, key=lambda m: m["total"])
            worst = min(monthly, key=lambda m: m["total"])
            lines.append(
                f"Best month was {best['month']} (${best['total']:,.2f}); "
                f"lowest was {worst['month']} (${worst['total']:,.2f})."
            )
        growth_months = [m for m in monthly if m["pct_change"] is not None]
        if growth_months:
            best_g = max(growth_months, key=lambda m: m["pct_change"])
            if best_g["pct_change"] > 0:
                lines.append(
                    f"Highest MoM growth was {best_g['month']} at +{best_g['pct_change']:.1f}%."
                )
        if top:
            lines.append(
                f"Top product: '{top[0]['name']}' representing "
                f"{top[0]['pct_of_total']:.1f}% of total revenue."
            )
        return " ".join(lines)
