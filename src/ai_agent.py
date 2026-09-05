"""Agente de insights: regras auditáveis e síntese generativa opcional."""

from __future__ import annotations

import json
import os
from typing import Any


def deterministic_insights(kpis: dict[str, Any]) -> list[str]:
    """Gera recomendações transparentes mesmo sem uma chave de API."""
    delivered_rate = kpis["delivered_records"] / kpis["records"]
    cancelled_rate = kpis["cancelled_records"] / kpis["records"]
    invalid_date_rate = kpis["invalid_dates"] / kpis["records"]
    top_share = kpis["top_family_value"] / kpis["recorded_value"]

    return [
        f"{invalid_date_rate:.0%} das datas são inválidas; não use esses registros em análises de tendência.",
        f"Apenas {delivered_rate:.0%} dos registros estão como Delivered; acompanhe a fila operacional.",
        f"Cancelamentos representam {cancelled_rate:.0%} dos registros; separe valor registrado de valor efetivado.",
        f"A família {kpis['top_family']} concentra {top_share:.1%} do valor registrado.",
        "Padronize os campos na entrada para reduzir retrabalho e tornar os KPIs comparáveis.",
    ]


def generate_ai_summary(kpis: dict[str, Any], insights: list[str]) -> str | None:
    """Solicita uma síntese curta à OpenAI quando OPENAI_API_KEY estiver definida."""
    if not os.getenv("OPENAI_API_KEY"):
        return None

    from openai import OpenAI

    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        input=(
            "Atue como analista executivo automotivo. Produza uma síntese em português, "
            "com no máximo 120 palavras, sem inventar dados. Diferencie registros, valor "
            "registrado e entregas. Dados: "
            + json.dumps({"kpis": kpis, "insights": insights}, ensure_ascii=False)
        ),
    )
    return response.output_text

