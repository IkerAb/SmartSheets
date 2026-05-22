"""Inventory ingestion and sell-through analysis service."""

from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

from app.models.inventory_models import (
    InventoryPersistRequest,
    InventoryPersistResult,
    InventoryRecord,
    SellThroughPoint,
)
from app.repositories.inventory_repository import PostgresInventoryRepository


@dataclass(frozen=True)
class InventoryUploadPayload:
    filename: str
    content: bytes


REQUIRED_COLS = {"semana_fiscal", "categoria", "tienda", "inventario_inicial", "unidades_vendidas"}


class InventoryService:

    def __init__(self, repository: PostgresInventoryRepository | None = None) -> None:
        self._repository = repository or PostgresInventoryRepository()

    def ingest_and_persist(self, payload: InventoryUploadPayload) -> InventoryPersistResult:
        df = self._parse(payload)
        df = self._validate(df)
        records = self._to_records(df)
        request = InventoryPersistRequest(
            source_filename=payload.filename,
            records=records,
        )
        return self._repository.persist_inventory(request)

    def compute_sell_through(
        self,
        inventory_df: pd.DataFrame,
        promo_df: pd.DataFrame | None = None,
        semana: int | None = None,
    ) -> list[SellThroughPoint]:
        """
        Calcula ST por categoría (opcionalmente filtrado por semana).
        Cruza con promos si se provee promo_df.
        """
        df = inventory_df.copy()
        if semana:
            df = df[df["semana_fiscal"] == semana]

        # agregar por semana + categoría (suma de todas las tiendas)
        grouped = (
            df.groupby(["semana_fiscal", "categoria"])
            .agg(
                inventario_inicial=("inventario_inicial", "sum"),
                unidades_vendidas=("unidades_vendidas", "sum"),
            )
            .reset_index()
        )

        results = []
        for _, row in grouped.iterrows():
            sem = int(row["semana_fiscal"])
            cat = str(row["categoria"])
            inv = int(row["inventario_inicial"])
            sold = int(row["unidades_vendidas"])
            st = round(sold / inv * 100, 1) if inv > 0 else 0.0

            # nivel de ST
            if st >= 70:
                nivel = "alto"
            elif st >= 40:
                nivel = "medio"
            else:
                nivel = "bajo"

            # cruzar con promos
            tiene_promo = False
            tipo_promos: list[str] = []
            md_promedio = 0.0

            if promo_df is not None:
                week_promos = promo_df[
                    (promo_df["semana_fiscal"] == sem) &
                    (promo_df["categoria"].str.lower() == cat.lower())
                ]
                if not week_promos.empty:
                    tiene_promo = True
                    tipo_promos = week_promos["tipo_promo"].unique().tolist()
                    md_promedio = round(float(week_promos["md_pct"].mean()), 1)

            # insight automático
            insight = self._generate_insight(cat, st, nivel, tiene_promo, tipo_promos, md_promedio, inv, sold)

            results.append(SellThroughPoint(
                semana_fiscal=sem,
                categoria=cat,
                tienda=None,
                inventario_inicial=inv,
                unidades_vendidas=sold,
                sell_through_pct=st,
                nivel=nivel,
                tiene_promo=tiene_promo,
                tipo_promos=tipo_promos,
                md_promedio=md_promedio,
                insight=insight,
            ))

        return sorted(results, key=lambda x: x.sell_through_pct, reverse=True)

    def _generate_insight(
        self, cat, st, nivel, tiene_promo, tipo_promos, md_promedio, inv, sold
    ) -> str:
        if tiene_promo and nivel == "alto":
            tipos = " + ".join(tipo_promos)
            return (
                f"{cat} tuvo ST {st}% con {tipos} activa (MD {md_promedio}%) — "
                f"promo efectiva con inventario suficiente. {sold} de {inv} unidades vendidas."
            )
        elif tiene_promo and nivel == "medio":
            return (
                f"{cat} tuvo ST {st}% con promo activa (MD {md_promedio}%) — "
                f"resultado moderado. Revisar si el inventario fue suficiente o si la promo tuvo poco alcance."
            )
        elif tiene_promo and nivel == "bajo":
            return (
                f"⚠️ {cat} tuvo ST {st}% a pesar de tener promo activa (MD {md_promedio}%) — "
                f"posible falta de inventario, promo poco atractiva o categoría fuera de temporada."
            )
        elif not tiene_promo and nivel == "alto":
            return (
                f"{cat} tuvo ST {st}% sin promo activa — "
                f"categoría con demanda orgánica fuerte. Considerar reducir MD en futuras semanas."
            )
        else:
            return (
                f"{cat} tuvo ST {st}% sin promo activa — "
                f"desempeño esperado para semana sin activación comercial."
            )

    def _parse(self, payload: InventoryUploadPayload) -> pd.DataFrame:
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
        df["inventario_inicial"] = pd.to_numeric(df["inventario_inicial"], errors="coerce").fillna(0).astype(int)
        df["unidades_vendidas"] = pd.to_numeric(df["unidades_vendidas"], errors="coerce").fillna(0).astype(int)
        df["categoria"] = df["categoria"].astype(str).str.strip()
        df["tienda"] = df["tienda"].astype(str).str.strip()
        return df.dropna(subset=["semana_fiscal"])

    def _to_records(self, df: pd.DataFrame) -> list[InventoryRecord]:
        return [
            InventoryRecord(
                semana_fiscal=int(row.semana_fiscal),
                categoria=str(row.categoria),
                tienda=str(row.tienda),
                inventario_inicial=int(row.inventario_inicial),
                unidades_vendidas=int(row.unidades_vendidas),
            )
            for row in df.itertuples(index=False)
        ]
