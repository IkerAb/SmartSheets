"""Traffic ingestion and conversion rate analysis service."""

from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

from app.models.traffic_models import (
    TrafficPersistRequest,
    TrafficPersistResult,
    TrafficRecord,
    StoreTrafficPoint,
)
from app.repositories.traffic_repository import PostgresTrafficRepository


@dataclass(frozen=True)
class TrafficUploadPayload:
    filename: str
    content: bytes


REQUIRED_COLS = {"semana_fiscal", "tienda", "trafico", "transacciones", "tasa_conversion_pct"}


class TrafficService:

    def __init__(self, repository: PostgresTrafficRepository | None = None) -> None:
        self._repository = repository or PostgresTrafficRepository()

    def ingest_and_persist(self, payload: TrafficUploadPayload) -> TrafficPersistResult:
        df = self._parse(payload)
        df = self._validate(df)
        records = self._to_records(df)
        request = TrafficPersistRequest(
            source_filename=payload.filename,
            records=records,
        )
        return self._repository.persist_traffic(request)

    def compute_traffic_analysis(
        self,
        df: pd.DataFrame,
        semana: int | None = None,
    ) -> list[StoreTrafficPoint]:
        """Calcula tráfico y conversión por tienda."""
        data = df.copy()
        if semana:
            data = data[data["semana_fiscal"] == semana]

        grouped = (
            data.groupby("tienda")
            .agg(
                trafico_total=("trafico", "sum"),
                transacciones_total=("transacciones", "sum"),
            )
            .reset_index()
        )

        grouped["tasa_conversion_pct"] = (
            grouped["transacciones_total"] / grouped["trafico_total"] * 100
        ).round(1)

        avg_conv = float(grouped["tasa_conversion_pct"].mean())
        avg_trafico = float(grouped["trafico_total"].mean())

        results = []
        for _, row in grouped.iterrows():
            tienda = str(row["tienda"])
            trafico = int(row["trafico_total"])
            txns = int(row["transacciones_total"])
            conv = round(float(row["tasa_conversion_pct"]), 1)
            vs_avg = round(conv - avg_conv, 1)

            if conv >= avg_conv * 1.1:
                nivel = "alto"
            elif conv >= avg_conv * 0.9:
                nivel = "medio"
            else:
                nivel = "bajo"

            insight = self._generate_insight(tienda, trafico, txns, conv, nivel, vs_avg, avg_trafico)

            results.append(StoreTrafficPoint(
                tienda=tienda,
                semana_fiscal=semana,
                trafico_total=trafico,
                transacciones_total=txns,
                tasa_conversion_pct=conv,
                vs_promedio_pct=vs_avg,
                nivel_conversion=nivel,
                insight=insight,
            ))

        return sorted(results, key=lambda x: x.tasa_conversion_pct, reverse=True)

    def _generate_insight(self, tienda, trafico, txns, conv, nivel, vs_avg, avg_trafico) -> str:
        if nivel == "alto" and trafico >= avg_trafico:
            return (
                f"{tienda} lidera con {conv}% de conversión (+{vs_avg}% vs promedio) "
                f"y alto tráfico ({trafico:,} visitantes). Mejor tienda del periodo."
            )
        elif nivel == "alto" and trafico < avg_trafico:
            return (
                f"{tienda} tiene excelente conversión ({conv}%, +{vs_avg}% vs promedio) "
                f"pero tráfico bajo ({trafico:,}). Oportunidad: aumentar tráfico mantendría buena conversión."
            )
        elif nivel == "bajo" and trafico >= avg_trafico:
            return (
                f"⚠️ {tienda} tiene alto tráfico ({trafico:,}) pero baja conversión ({conv}%, {vs_avg}% vs promedio). "
                f"Revisar experiencia en tienda, layout o efectividad del equipo de ventas."
            )
        elif nivel == "bajo":
            return (
                f"⚠️ {tienda} tiene conversión baja ({conv}%, {vs_avg}% vs promedio) "
                f"y tráfico limitado ({trafico:,}). Requiere atención en activación comercial."
            )
        else:
            return (
                f"{tienda} con conversión promedio ({conv}%). "
                f"Tráfico: {trafico:,} visitantes, {txns:,} transacciones."
            )

    def _parse(self, payload: TrafficUploadPayload) -> pd.DataFrame:
        import io
        ext = payload.filename.rsplit(".", 1)[-1].lower()
        buf = io.BytesIO(payload.content)
        if ext == "csv":
            try:
                df = pd.read_csv(buf, encoding="utf-8")
            except UnicodeDecodeError:
                buf.seek(0)
                df = pd.read_csv(buf, encoding="latin-1")
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(buf, engine="openpyxl")
        else:
            raise ValueError(f"Extensión no soportada: .{ext}")
        df.columns = [c.lower().strip() for c in df.columns]
        return df

    def _validate(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            raise ValueError(f"Columnas faltantes: {missing}")
        df["semana_fiscal"] = pd.to_numeric(df["semana_fiscal"], errors="coerce").astype(int)
        df["trafico"] = pd.to_numeric(df["trafico"], errors="coerce").fillna(0).astype(int)
        df["transacciones"] = pd.to_numeric(df["transacciones"], errors="coerce").fillna(0).astype(int)
        df["tasa_conversion_pct"] = pd.to_numeric(df["tasa_conversion_pct"], errors="coerce").fillna(0)
        df["tienda"] = df["tienda"].astype(str).str.strip()
        return df.dropna(subset=["semana_fiscal"])

    def _to_records(self, df: pd.DataFrame) -> list[TrafficRecord]:
        return [
            TrafficRecord(
                semana_fiscal=int(row.semana_fiscal),
                tienda=str(row.tienda),
                trafico=int(row.trafico),
                transacciones=int(row.transacciones),
                tasa_conversion_pct=float(row.tasa_conversion_pct),
            )
            for row in df.itertuples(index=False)
        ]
