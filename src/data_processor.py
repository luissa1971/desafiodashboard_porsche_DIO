"""Leitura, validação e agregação da base Porsche sanitizada."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "sale_id",
    "SaleDateSanitized",
    "PorscheModelSanitized",
    "ModelYearSanitized",
    "SalesPriceSanitized",
    "VehicleMileageSanitized",
    "PayMethodSanitized",
    "CitySanitized",
    "StateSanitized",
    "salesperson",
    "DeliveryStatusSanitized",
}


def load_and_prepare(path: str | Path) -> pd.DataFrame:
    """Carrega a aba Sanitized e cria campos analíticos sem alterar a origem."""
    df = pd.read_excel(path, sheet_name="Sanitized")
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(missing)}")

    prepared = df.copy()
    prepared["sale_date"] = pd.to_datetime(
        prepared["SaleDateSanitized"], errors="coerce", format="mixed"
    )
    prepared["sale_price"] = pd.to_numeric(
        prepared["SalesPriceSanitized"], errors="coerce"
    )
    prepared["vehicle_mileage"] = pd.to_numeric(
        prepared["VehicleMileageSanitized"], errors="coerce"
    )
    prepared["model_year"] = pd.to_numeric(
        prepared["ModelYearSanitized"], errors="coerce"
    ).astype("Int64")
    prepared["salesperson_clean"] = prepared["salesperson"].str.strip().str.title()
    prepared["model_family"] = prepared["PorscheModelSanitized"].str.extract(
        r"^(911|718|Taycan|Panamera|Cayenne|Macan)", expand=False
    )
    prepared["date_quality"] = prepared["sale_date"].notna().map(
        {True: "Valid", False: "Invalid"}
    )
    return prepared


def calculate_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Calcula os KPIs centrais usados no dashboard e pelo agente."""
    delivered = df["DeliveryStatusSanitized"].eq("Delivered")
    cancelled = df["DeliveryStatusSanitized"].eq("Cancelled")
    family_revenue = df.groupby("model_family")["sale_price"].sum()

    return {
        "records": int(len(df)),
        "recorded_value": float(df["sale_price"].sum()),
        "average_ticket": float(df["sale_price"].mean()),
        "delivered_records": int(delivered.sum()),
        "delivered_value": float(df.loc[delivered, "sale_price"].sum()),
        "cancelled_records": int(cancelled.sum()),
        "cancelled_value": float(df.loc[cancelled, "sale_price"].sum()),
        "valid_dates": int(df["sale_date"].notna().sum()),
        "invalid_dates": int(df["sale_date"].isna().sum()),
        "top_family": str(family_revenue.idxmax()),
        "top_family_value": float(family_revenue.max()),
    }


def grouped_metrics(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """Retorna volume, valor e ticket médio para uma dimensão."""
    return (
        df.groupby(group, dropna=False)
        .agg(
            records=("sale_id", "count"),
            recorded_value=("sale_price", "sum"),
            average_ticket=("sale_price", "mean"),
        )
        .reset_index()
        .sort_values("recorded_value", ascending=False)
    )


def temporal_metrics(df: pd.DataFrame, frequency: str = "YS") -> pd.DataFrame:
    """Agrega somente registros com datas válidas por ano ou mês."""
    valid = df.dropna(subset=["sale_date"]).copy()
    return (
        valid.set_index("sale_date")
        .resample(frequency)
        .agg(records=("sale_id", "count"), recorded_value=("sale_price", "sum"))
        .reset_index()
    )

