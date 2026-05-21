"""
app/services/analysis.py
─────────────────────────
Calcula KPIs. Campos alineados con el frontend React:
- top_products: usa 'pct' en lugar de 'pct_of_total'
- monthly_growth: usa 'sales' y 'mom_pct' en lugar de 'total' y 'pct_change'
"""
from __future__ import annotations

import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalysisService:

    def compute_insights(self, df: pd.DataFrame) -> dict:
        logger.info("Computing insights for %d rows", len(df))

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
                "pct": round(float(val) / total_sales * 100, 1) if total_sales else 0.0,
                # ↑ 'pct' en lugar de 'pct_of_total' — alineado con frontend
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
                "sales": round(float(row["ventas"]), 2),       # 'sales' en lugar de 'total'
                "mom_pct": round(float(row["pct_change"]), 1)  # 'mom_pct' en lugar de 'pct_change'
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
            best = max(monthly, key=lambda m: m["sales"])
            worst = min(monthly, key=lambda m: m["sales"])
            lines.append(
                f"Best month was {best['month']} (${best['sales']:,.2f}); "
                f"lowest was {worst['month']} (${worst['sales']:,.2f})."
            )
        growth_months = [m for m in monthly if m["mom_pct"] is not None]
        if growth_months:
            best_g = max(growth_months, key=lambda m: m["mom_pct"])
            if best_g["mom_pct"] > 0:
                lines.append(
                    f"Highest MoM growth was {best_g['month']} at +{best_g['mom_pct']:.1f}%."
                )
        if top:
            lines.append(
                f"Top product: '{top[0]['name']}' representing "
                f"{top[0]['pct']:.1f}% of total revenue."
            )
        return " ".join(lines)
