"""Dashboard interativo Porsche Sales Analytics."""

from pathlib import Path

import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.ai_agent import deterministic_insights, generate_ai_summary
from src.data_processor import calculate_kpis, grouped_metrics, load_and_prepare, temporal_metrics


load_dotenv()
DATA_PATH = Path(__file__).parent / "data" / "porsche_sales_sanitized.xlsx"

st.set_page_config(page_title="Porsche Sales Analytics", page_icon="🏎️", layout="wide")
st.markdown(
    """
    <style>
    .stApp {background: #0b1220; color: #f8fafc;}
    [data-testid="stMetric"] {background:#182334; border:1px solid #263449; padding:16px; border-radius:14px;}
    h1, h2, h3 {letter-spacing:.02em;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data():
    return load_and_prepare(DATA_PATH)


df = get_data()

st.title("PORSCHE SALES ANALYTICS")
st.caption("Dashboard executivo • dados tratados e explicados por agente de IA")

with st.sidebar:
    st.header("Filtros")
    families = sorted(df["model_family"].dropna().unique())
    states = sorted(df["StateSanitized"].dropna().unique())
    statuses = sorted(df["DeliveryStatusSanitized"].dropna().unique())
    selected_families = st.multiselect("Família", families, default=families)
    selected_states = st.multiselect("Estado", states, default=states)
    selected_statuses = st.multiselect("Status", statuses, default=statuses)

filtered = df[
    df["model_family"].isin(selected_families)
    & df["StateSanitized"].isin(selected_states)
    & df["DeliveryStatusSanitized"].isin(selected_statuses)
]
kpis = calculate_kpis(filtered)

cols = st.columns(5)
cols[0].metric("Registros", f"{kpis['records']:,}")
cols[1].metric("Valor registrado", f"US$ {kpis['recorded_value']/1_000_000:.2f} mi")
cols[2].metric("Ticket médio", f"US$ {kpis['average_ticket']/1_000:.1f} mil")
cols[3].metric("Entregues", f"{kpis['delivered_records']:,}")
cols[4].metric("Família líder", kpis["top_family"])

left, right = st.columns(2)
with left:
    family = grouped_metrics(filtered, "model_family")
    fig = px.bar(
        family,
        x="recorded_value",
        y="model_family",
        orientation="h",
        title="Valor registrado por família",
        color="recorded_value",
        color_continuous_scale=["#6b0f1a", "#e30613"],
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="#111b2a", plot_bgcolor="#111b2a", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with right:
    yearly = temporal_metrics(filtered, "YS")
    fig = px.line(yearly, x="sale_date", y="recorded_value", markers=True, title="Evolução anual — datas válidas")
    fig.update_traces(line_color="#8b5cf6", marker_color="#e30613")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#111b2a", plot_bgcolor="#111b2a")
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    status = grouped_metrics(filtered, "DeliveryStatusSanitized")
    fig = px.bar(status, x="records", y="DeliveryStatusSanitized", orientation="h", title="Registros por status")
    fig.update_traces(marker_color="#64748b")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#111b2a", plot_bgcolor="#111b2a")
    st.plotly_chart(fig, use_container_width=True)

with right:
    payment = grouped_metrics(filtered, "PayMethodSanitized").head(7)
    fig = px.pie(payment, names="PayMethodSanitized", values="recorded_value", hole=.58, title="Mix de pagamento por valor")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#111b2a")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("AI Insights")
insights = deterministic_insights(kpis)
for item in insights:
    st.write(f"• {item}")

try:
    summary = generate_ai_summary(kpis, insights)
    if summary:
        st.info(summary)
except Exception as exc:
    st.warning(f"Síntese generativa indisponível: {exc}")

if kpis["invalid_dates"]:
    st.warning(f"Qualidade de dados: {kpis['invalid_dates']} datas inválidas foram excluídas dos gráficos temporais.")

