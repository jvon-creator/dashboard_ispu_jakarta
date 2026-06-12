from __future__ import annotations

from pathlib import Path
from typing import Iterable
import html

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# Konfigurasi halaman
# ============================================================
st.set_page_config(
    page_title="Dashboard ISPU Jakarta | DLH DKI Jakarta",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Konstanta desain & data
# ============================================================
DATA_PATH = Path(__file__).parent / "data" / "ispu_jakarta_bersih.csv"

CATEGORY_ORDER = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CATEGORY_COLORS = {
    "BAIK": "#16A34A",
    "SEDANG": "#F59E0B",
    "TIDAK SEHAT": "#EA580C",
    "SANGAT TIDAK SEHAT": "#DC2626",
    "BERBAHAYA": "#7F1D1D",
}
CRITICAL_COLORS = {
    "PM10": "#92400E",
    "PM2.5": "#0891B2",
    "O3": "#059669",
    "CO": "#DB2777",
    "SO2": "#64748B",
    "NO2": "#7C3AED",
}
STATION_COORDS = {
    "DKI1 Bunderan HI": (-6.1944, 106.8230),
    "DKI2 Kelapa Gading": (-6.1587, 106.9040),
    "DKI3 Jagakarsa": (-6.3340, 106.8234),
    "DKI4 Lubang Buaya": (-6.2906, 106.9098),
    "DKI5 Kebon Jeruk": (-6.1989, 106.7693),
}
MONTH_ORDER = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]
POLLUTANT_COLS = ["pm10", "pm25", "so2", "co", "o3", "no2"]

# ============================================================
# CSS light theme: SPKU command desk
# ============================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            --paper: #F7FBF8;
            --panel: #FFFFFF;
            --panel-2: #F1F7F4;
            --ink: #10201B;
            --muted: #64756E;
            --soft: #DDEBE4;
            --teal: #0F766E;
            --teal-2: #14B8A6;
            --mint: #D9FBEF;
            --amber: #F59E0B;
            --orange: #EA580C;
            --red: #DC2626;
            --slate: #334155;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(20, 184, 166, .16), transparent 26%),
                radial-gradient(circle at 92% 0%, rgba(245, 158, 11, .16), transparent 24%),
                linear-gradient(180deg, #F9FCFA 0%, #F4FAF6 52%, #EEF7F2 100%);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.3rem;
            padding-bottom: 3rem;
        }

        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #DCEAE3;
            box-shadow: 12px 0 30px rgba(15, 118, 110, .06);
        }
        section[data-testid="stSidebar"] label {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: .75rem !important;
            letter-spacing: .04em !important;
            color: #0F766E !important;
            text-transform: uppercase;
        }
        section[data-testid="stSidebar"] [data-baseweb="tag"] {
            background: #E2F8F2 !important;
            border: 1px solid #B9E9DC !important;
            color: #0F766E !important;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #DDEBE4;
            border-radius: 22px;
            padding: 18px 18px 16px;
            box-shadow: 0 16px 35px rgba(15, 118, 110, .09);
            min-height: 130px;
        }
        div[data-testid="stMetricLabel"] p {
            font-family: 'IBM Plex Mono', monospace !important;
            color: #0F766E !important;
            font-size: .72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: .06em !important;
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', 'Inter', sans-serif !important;
            color: #10201B !important;
            font-weight: 700 !important;
        }
        .kpi-caption {
            color: #687A73;
            font-size: .83rem;
            line-height: 1.35;
            margin-top: -6px;
        }
        .hero {
            position: relative;
            overflow: hidden;
            border-radius: 32px;
            border: 1px solid #DDEBE4;
            background:
                linear-gradient(135deg, #FFFFFF 0%, #F4FBF8 58%, #E8F8F3 100%);
            box-shadow: 0 28px 70px rgba(15, 118, 110, .12);
            padding: 36px 38px 32px;
            margin-bottom: 18px;
        }
        .hero:before {
            content: "";
            position: absolute;
            right: -80px;
            top: -120px;
            width: 460px;
            height: 460px;
            border-radius: 50%;
            background:
                radial-gradient(circle, rgba(15, 118, 110, .15) 0 2px, transparent 2px 24px),
                conic-gradient(from 80deg, rgba(15,118,110,.18), rgba(245,158,11,.16), rgba(22,163,74,.12), rgba(15,118,110,.18));
            opacity: .85;
        }
        .hero:after {
            content: "SPKU NETWORK";
            position: absolute;
            right: 32px;
            bottom: 22px;
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: .22em;
            font-size: .72rem;
            color: rgba(15, 118, 110, .34);
        }
        .eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            color: #0F766E;
            letter-spacing: .11em;
            text-transform: uppercase;
            font-weight: 800;
            font-size: .78rem;
            margin-bottom: .75rem;
        }
        .hero h1 {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(2.1rem, 5vw, 4.4rem);
            line-height: .96;
            letter-spacing: -.055em;
            margin: 0 0 1rem;
            max-width: 980px;
            color: #10201B;
            position: relative;
            z-index: 2;
        }
        .hero p {
            color: #4A6259;
            max-width: 900px;
            line-height: 1.65;
            font-size: 1.05rem;
            margin: 0;
            position: relative;
            z-index: 2;
        }
        .station-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 24px;
            position: relative;
            z-index: 2;
        }
        .station-chip {
            font-family: 'IBM Plex Mono', monospace;
            font-size: .76rem;
            color: #0F766E;
            background: #E2F8F2;
            border: 1px solid #B7E9DB;
            border-radius: 999px;
            padding: 8px 12px;
        }
        .section-kicker {
            font-family: 'IBM Plex Mono', monospace;
            color: #0F766E;
            letter-spacing: .11em;
            text-transform: uppercase;
            font-size: .73rem;
            font-weight: 800;
            margin-top: 1.25rem;
        }
        .section-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(1.45rem, 2.35vw, 2.1rem);
            line-height: 1.04;
            letter-spacing: -.035em;
            font-weight: 700;
            color: #10201B;
            margin: .2rem 0 .55rem;
        }
        .section-copy {
            color: #64756E;
            line-height: 1.62;
            max-width: 1010px;
            margin-bottom: 1rem;
        }
        .insight-card {
            background: linear-gradient(90deg, rgba(15, 118, 110, .10), rgba(217, 251, 239, .72), rgba(245, 158, 11, .10));
            border: 1px solid #CFE7DC;
            border-radius: 22px;
            padding: 18px 20px;
            box-shadow: 0 14px 32px rgba(15, 118, 110, .08);
            margin: 14px 0 20px;
        }
        .insight-title {
            font-family: 'IBM Plex Mono', monospace;
            color: #0F766E;
            letter-spacing: .08em;
            text-transform: uppercase;
            font-size: .76rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .insight-card p {
            color: #2F4840;
            line-height: 1.58;
            margin: 0;
        }
        .mini-card {
            background: #FFFFFF;
            border: 1px solid #DDEBE4;
            border-radius: 22px;
            padding: 18px 20px;
            box-shadow: 0 14px 32px rgba(15, 118, 110, .08);
            margin: 12px 0 18px;
        }
        .mini-card p, .mini-card li { color: #334155; line-height: 1.56; }
        .pill {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 9px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: .72rem;
            font-weight: 800;
            margin-right: 6px;
        }
        .pill-teal { background: #D9FBEF; color: #0F766E; border: 1px solid #A6E7D3; }
        .pill-amber { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .pill-red { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
        div[data-testid="stTabs"] button {
            font-weight: 750;
            color: #536760;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #0F766E;
            border-bottom-color: #0F766E;
        }
        .stDownloadButton button, .stButton button {
            border-radius: 999px !important;
            border: 1px solid #0F766E !important;
            background: #0F766E !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }
        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #DDEBE4;
        }
        footer, #MainMenu { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Utilitas data & visualisasi
# ============================================================
@st.cache_data(show_spinner=False)
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal", "stasiun", "max", "critical", "categori"]).copy()
    if "tahun" not in df.columns:
        df["tahun"] = df["tanggal"].dt.year
    if "bulan" not in df.columns:
        df["bulan"] = df["tanggal"].dt.month
    if "nama_bulan" not in df.columns:
        df["nama_bulan"] = df["tanggal"].dt.month_name()
    df["tahun"] = df["tahun"].astype(int)
    df["bulan"] = df["bulan"].astype(int)
    df["nama_bulan"] = pd.Categorical(df["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    df["is_unhealthy_or_worse"] = df["categori"].isin(["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"])
    df["periode_harian"] = df["tanggal"].dt.to_period("D").dt.to_timestamp()
    df["periode_bulanan"] = df["tanggal"].dt.to_period("M").dt.to_timestamp()
    df["periode_tahunan"] = pd.to_datetime(df["tahun"].astype(str) + "-01-01")
    df["lat"] = df["stasiun"].map(lambda x: STATION_COORDS.get(x, (np.nan, np.nan))[0])
    df["lon"] = df["stasiun"].map(lambda x: STATION_COORDS.get(x, (np.nan, np.nan))[1])
    return df


def fmt_number(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return "-"
    return f"{value * 100:,.{digits}f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def mode_value(series: pd.Series) -> str:
    counts = series.dropna().value_counts()
    return "-" if counts.empty else str(counts.index[0])


def safe_join(items: Iterable[str], max_items: int = 3) -> str:
    selected = [str(i) for i in list(items)[:max_items]]
    return ", ".join(selected) if selected else "-"


def get_plot_template() -> go.layout.Template:
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Inter, Arial, sans-serif", color="#334155"),
        title=dict(font=dict(family="Space Grotesk, Inter, Arial, sans-serif", size=22, color="#10201B"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        colorway=["#0F766E", "#14B8A6", "#F59E0B", "#EA580C", "#DC2626", "#7C3AED", "#64748B"],
        xaxis=dict(gridcolor="#E5EEE9", zerolinecolor="#DDEBE4", linecolor="#DDEBE4"),
        yaxis=dict(gridcolor="#E5EEE9", zerolinecolor="#DDEBE4", linecolor="#DDEBE4"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#334155")),
        margin=dict(l=30, r=30, t=70, b=35),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="#0F766E", font=dict(color="#10201B")),
    )
    return template


PLOT_TEMPLATE = get_plot_template()


def polish_figure(fig: go.Figure, height: int = 450) -> go.Figure:
    fig.update_layout(template=PLOT_TEMPLATE, height=height)
    fig.update_xaxes(title_font=dict(color="#536760"), tickfont=dict(color="#536760"))
    fig.update_yaxes(title_font=dict(color="#536760"), tickfont=dict(color="#536760"))
    return fig


def section_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-kicker">{html.escape(kicker)}</div>
        <div class="section-title">{html.escape(title)}</div>
        <div class="section-copy">{html.escape(copy)}</div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, analysis: str, action: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{html.escape(title)}</div>
            <p><b>Analisis utama:</b> {analysis}</p>
            <p style="margin-top:10px"><b>Insight tindak lanjut:</b> {action}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def describe_trend(df: pd.DataFrame) -> tuple[str, float]:
    annual = df.groupby("tahun", as_index=False)["max"].mean().sort_values("tahun")
    if len(annual) < 2:
        return "belum dapat disimpulkan karena hanya ada satu tahun data pada filter aktif", 0.0
    x = annual["tahun"].to_numpy(dtype=float)
    y = annual["max"].to_numpy(dtype=float)
    slope = float(np.polyfit(x, y, 1)[0])
    if slope > 0.8:
        direction = "cenderung memburuk"
    elif slope < -0.8:
        direction = "cenderung membaik"
    else:
        direction = "relatif stabil atau fluktuatif"
    return direction, slope


def make_download(df: pd.DataFrame, filename: str) -> None:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Unduh data terfilter (.csv)", csv, filename, "text/csv")

# ============================================================
# Load data
# ============================================================
df = load_data()

# ============================================================
# Sidebar filter interaktif
# ============================================================
with st.sidebar:
    st.markdown("### Panel kendali")
    st.markdown(
        "Gunakan filter ini saat demo untuk menunjukkan perubahan insight menurut rentang tanggal, stasiun, kategori, dan pencemar kritis."
    )

    min_date = df["tanggal"].min().date()
    max_date = df["tanggal"].max().date()
    selected_dates = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

    station_options = sorted(df["stasiun"].dropna().unique())
    selected_stations = st.multiselect("Stasiun SPKU", station_options, default=station_options)

    category_options = [c for c in CATEGORY_ORDER if c in set(df["categori"].dropna())]
    selected_categories = st.multiselect("Kategori ISPU", category_options, default=category_options)

    critical_options = sorted(df["critical"].dropna().unique())
    selected_critical = st.multiselect("Pencemar kritis", critical_options, default=critical_options)

    granularity = st.radio("Granularitas tren", ["Harian", "Bulanan", "Tahunan"], index=1, horizontal=False)

    st.markdown("---")
    st.caption("Satuan analisis utama: satu tanggal dan satu stasiun SPKU. Dataset bersih berasal dari hasil validasi Tugas 3–5.")

# ============================================================
# Filter data
# ============================================================
mask = (
    (df["tanggal"].dt.date >= start_date)
    & (df["tanggal"].dt.date <= end_date)
    & (df["stasiun"].isin(selected_stations))
    & (df["categori"].isin(selected_categories))
    & (df["critical"].isin(selected_critical))
)
fdf = df.loc[mask].copy()

# ============================================================
# Hero
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Business Intelligence Dashboard · ISPU DKI Jakarta</div>
        <h1>Ruang kendali kualitas udara untuk keputusan yang berbasis risiko.</h1>
        <p>
            Dashboard ini menyajikan kondisi umum, tren waktu, perbandingan stasiun, parameter pencemar kritis,
            dan pola musiman kualitas udara Jakarta. Setiap visualisasi dilengkapi analisis dan tindak lanjut agar
            dapat digunakan langsung saat presentasi, rapat teknis, maupun briefing pimpinan.
        </p>
        <div class="station-strip">
            <div class="station-chip">DKI1 · Bunderan HI</div>
            <div class="station-chip">DKI2 · Kelapa Gading</div>
            <div class="station-chip">DKI3 · Jagakarsa</div>
            <div class="station-chip">DKI4 · Lubang Buaya</div>
            <div class="station-chip">DKI5 · Kebon Jeruk</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if fdf.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih. Perluas rentang tanggal atau pilih ulang filter stasiun/kategori/pencemar.")
    st.stop()

# ============================================================
# KPI utama
# ============================================================
avg_ispu = fdf["max"].mean()
unhealthy_obs_pct = fdf["is_unhealthy_or_worse"].mean()
unhealthy_day_pct = fdf.groupby(fdf["tanggal"].dt.date)["is_unhealthy_or_worse"].any().mean()
dominant_pollutant = mode_value(fdf["critical"])
station_avg = fdf.groupby("stasiun")["max"].mean().sort_values(ascending=False)
priority_station = station_avg.index[0] if not station_avg.empty else "-"
obs_count = len(fdf)
day_count = fdf["tanggal"].dt.date.nunique()
period_label = f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"

kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.metric("Rata-rata ISPU", fmt_number(avg_ispu), help=f"Rata-rata kolom max dari {obs_count:,} observasi tanggal-stasiun.".replace(",", "."))
    st.markdown("<div class='kpi-caption'>Indikator ringkas kondisi kualitas udara pada filter aktif.</div>", unsafe_allow_html=True)
with kpi_cols[1]:
    st.metric("Hari Tidak Sehat+", fmt_pct(unhealthy_day_pct), help="Persentase hari ketika minimal satu stasiun pada filter aktif masuk kategori Tidak Sehat atau lebih buruk.")
    st.markdown(f"<div class='kpi-caption'>Pembanding observasi tanggal-stasiun: {fmt_pct(unhealthy_obs_pct)}.</div>", unsafe_allow_html=True)
with kpi_cols[2]:
    st.metric("Pencemar dominan", dominant_pollutant, help="Parameter yang paling sering menjadi critical pollutant pada data terfilter.")
    st.markdown("<div class='kpi-caption'>Digunakan untuk menentukan fokus pengendalian emisi.</div>", unsafe_allow_html=True)
with kpi_cols[3]:
    st.metric("Stasiun prioritas", priority_station.replace("DKI", "DKI ", 1), help="Stasiun dengan rata-rata ISPU tertinggi pada filter aktif.")
    st.markdown("<div class='kpi-caption'>Lokasi awal untuk evaluasi dan intervensi operasional.</div>", unsafe_allow_html=True)

st.caption(
    f"Periode aktif: {period_label}. Data terfilter mencakup {obs_count:,} observasi dan {day_count:,} hari unik.".replace(",", ".")
)

# ============================================================
# Tabs visualisasi
# ============================================================
tabs = st.tabs([
    "1 · Overview",
    "2 · Tren temporal",
    "3 · Antar stasiun",
    "4 · Pencemar kritis",
    "5 · Pola musiman",
    "Lampiran",
])

# ============================================================
# Visualisasi 1 — Overview
# ============================================================
with tabs[0]:
    section_header(
        "Visualisasi 1",
        "Overview kualitas udara Jakarta",
        "Menjawab kondisi umum Jakarta melalui KPI utama, peta kondisi terkini per stasiun, distribusi kategori ISPU, dan ringkasan prioritas lokasi."
    )

    latest_per_station = fdf.sort_values("tanggal").groupby("stasiun", as_index=False).tail(1).copy()
    latest_per_station["size"] = latest_per_station["max"].clip(lower=18, upper=260)

    col_map, col_dist = st.columns([1.18, 1])
    with col_map:
        fig_map = px.scatter_mapbox(
            latest_per_station,
            lat="lat",
            lon="lon",
            color="categori",
            size="size",
            hover_name="stasiun",
            hover_data={"max": ":.1f", "critical": True, "tanggal": True, "lat": False, "lon": False, "size": False},
            color_discrete_map=CATEGORY_COLORS,
            category_orders={"categori": CATEGORY_ORDER},
            zoom=9.2,
            height=500,
            title="Ringkasan kondisi terkini per SPKU pada filter aktif",
        )
        fig_map.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": -6.22, "lon": 106.84},
            margin=dict(l=0, r=0, t=62, b=0),
            legend_title_text="Kategori",
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_dist:
        category_dist = fdf["categori"].value_counts(normalize=True).reindex(CATEGORY_ORDER).dropna().mul(100).reset_index()
        category_dist.columns = ["Kategori", "Persentase"]
        fig_cat = px.bar(
            category_dist,
            x="Kategori",
            y="Persentase",
            color="Kategori",
            color_discrete_map=CATEGORY_COLORS,
            text=category_dist["Persentase"].map(lambda x: f"{x:.1f}%"),
            title="Distribusi kategori ISPU",
        )
        fig_cat.update_traces(textposition="outside", cliponaxis=False)
        fig_cat.update_layout(showlegend=False, yaxis_title="Persentase observasi", xaxis_title="Kategori")
        st.plotly_chart(polish_figure(fig_cat, height=500), use_container_width=True)

    station_summary = (
        fdf.groupby("stasiun", as_index=False)
        .agg(
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            persen_tidak_sehat=("is_unhealthy_or_worse", "mean"),
            pencemar_dominan=("critical", mode_value),
            observasi=("tanggal", "count"),
        )
        .sort_values("rata_rata_ispu", ascending=False)
    )
    top_station = station_summary.iloc[0]
    display_station_summary = station_summary.copy()
    display_station_summary["rata_rata_ispu"] = display_station_summary["rata_rata_ispu"].round(1)
    display_station_summary["median_ispu"] = display_station_summary["median_ispu"].round(1)
    display_station_summary["persen_tidak_sehat"] = (display_station_summary["persen_tidak_sehat"] * 100).round(1)
    display_station_summary = display_station_summary.rename(columns={
        "stasiun": "Stasiun", "rata_rata_ispu": "Rata-rata ISPU", "median_ispu": "Median ISPU",
        "persen_tidak_sehat": "% Tidak Sehat+", "pencemar_dominan": "Pencemar Dominan", "observasi": "Observasi"
    })
    st.dataframe(display_station_summary, use_container_width=True, hide_index=True)

    insight_card(
        "Analisis & insight overview",
        f"Pada filter aktif, rata-rata ISPU berada di <b>{fmt_number(avg_ispu)}</b>, hari dengan minimal satu stasiun Tidak Sehat+ sebesar <b>{fmt_pct(unhealthy_day_pct)}</b>, dan pencemar dominan adalah <b>{html.escape(dominant_pollutant)}</b>.",
        f"Gunakan <b>{html.escape(top_station['stasiun'])}</b> sebagai titik awal briefing lokasi prioritas. Ketika KPI Hari Tidak Sehat+ meningkat, aktifkan pemantauan lebih rapat dan komunikasi risiko harian."
    )

# ============================================================
# Visualisasi 2 — Tren Temporal
# ============================================================
with tabs[1]:
    section_header(
        "Visualisasi 2",
        "Tren temporal kualitas udara",
        "Menjawab apakah kualitas udara cenderung membaik, memburuk, atau fluktuatif melalui pilihan granularitas harian, bulanan, dan tahunan."
    )

    period_col = {"Harian": "periode_harian", "Bulanan": "periode_bulanan", "Tahunan": "periode_tahunan"}[granularity]
    trend_df = (
        fdf.groupby([period_col, "stasiun"], as_index=False)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat=("is_unhealthy_or_worse", "mean"), observasi=("max", "count"))
        .rename(columns={period_col: "periode"})
        .sort_values("periode")
    )
    trend_df["periode"] = pd.to_datetime(trend_df["periode"])

    direction, slope = describe_trend(fdf)
    annual_rank = fdf.groupby("tahun", as_index=False).agg(rata_rata_ispu=("max", "mean"), observasi=("max", "count"), tidak_sehat=("is_unhealthy_or_worse", "mean")).sort_values("rata_rata_ispu")
    best_year = int(annual_rank.iloc[0]["tahun"]) if not annual_rank.empty else None
    worst_year = int(annual_rank.iloc[-1]["tahun"]) if not annual_rank.empty else None
    worst_year_obs = int(annual_rank.iloc[-1]["observasi"]) if not annual_rank.empty else 0

    fig_trend = px.line(
        trend_df,
        x="periode",
        y="rata_rata_ispu",
        color="stasiun",
        markers=(granularity == "Tahunan"),
        title=f"Tren {granularity.lower()} ISPU: {direction}",
        labels={"periode": "Periode", "rata_rata_ispu": "Rata-rata ISPU", "stasiun": "Stasiun"},
    )
    fig_trend.add_hline(y=100, line_dash="dash", line_color="#EA580C", annotation_text="Batas Tidak Sehat")
    fig_trend.update_traces(line_width=2.6)
    st.plotly_chart(polish_figure(fig_trend, height=540), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_year = px.bar(
            annual_rank.sort_values("tahun"),
            x="tahun",
            y="rata_rata_ispu",
            color="rata_rata_ispu",
            color_continuous_scale=["#16A34A", "#F59E0B", "#EA580C", "#DC2626"],
            title=f"Tahun terbaik: {best_year} · terburuk: {worst_year}",
            labels={"tahun": "Tahun", "rata_rata_ispu": "Rata-rata ISPU"},
        )
        fig_year.update_layout(coloraxis_showscale=False)
        st.plotly_chart(polish_figure(fig_year, height=360), use_container_width=True)
    with col_b:
        annual_unhealthy = annual_rank.sort_values("tahun").copy()
        annual_unhealthy["persen_tidak_sehat"] = annual_unhealthy["tidak_sehat"] * 100
        fig_unhealthy = px.area(
            annual_unhealthy,
            x="tahun",
            y="persen_tidak_sehat",
            title="Proporsi observasi Tidak Sehat+ per tahun",
            labels={"tahun": "Tahun", "persen_tidak_sehat": "% Tidak Sehat+"},
        )
        fig_unhealthy.update_traces(line_color="#DC2626", fillcolor="rgba(220, 38, 38, .12)")
        st.plotly_chart(polish_figure(fig_unhealthy, height=360), use_container_width=True)

    insight_card(
        "Analisis & insight tren temporal",
        f"Arah tren tahunan pada filter aktif <b>{direction}</b> dengan kemiringan sekitar <b>{slope:.2f}</b> poin ISPU per tahun. Tahun terendah adalah <b>{best_year}</b>, sedangkan tahun tertinggi adalah <b>{worst_year}</b> dengan <b>{worst_year_obs}</b> observasi.",
        "Gunakan tren tahunan dan proporsi Tidak Sehat+ sebagai indikator evaluasi program. Tahun dengan jumlah observasi rendah perlu diberi catatan agar tidak menjadi satu-satunya dasar keputusan."
    )

# ============================================================
# Visualisasi 3 — Perbandingan antar stasiun
# ============================================================
with tabs[2]:
    section_header(
        "Visualisasi 3",
        "Perbandingan kualitas udara antar 5 SPKU",
        "Menjawab stasiun mana yang memiliki kualitas udara relatif terburuk dan terbaik berdasarkan rata-rata ISPU serta distribusi kategori risiko."
    )

    station_metric = (
        fdf.groupby("stasiun", as_index=False)
        .agg(rata_rata_ispu=("max", "mean"), median_ispu=("max", "median"), tidak_sehat=("is_unhealthy_or_worse", "mean"), observasi=("max", "count"))
        .sort_values("rata_rata_ispu", ascending=True)
    )
    worst_station = station_metric.sort_values("rata_rata_ispu", ascending=False).iloc[0]["stasiun"]
    best_station = station_metric.sort_values("rata_rata_ispu", ascending=True).iloc[0]["stasiun"]

    col1, col2 = st.columns([1.05, 1])
    with col1:
        fig_station = px.bar(
            station_metric,
            y="stasiun",
            x="rata_rata_ispu",
            orientation="h",
            color="rata_rata_ispu",
            color_continuous_scale=["#16A34A", "#F59E0B", "#EA580C", "#DC2626"],
            text=station_metric["rata_rata_ispu"].map(lambda x: f"{x:.1f}"),
            title=f"{worst_station} memiliki rata-rata ISPU tertinggi",
            labels={"stasiun": "Stasiun", "rata_rata_ispu": "Rata-rata ISPU"},
        )
        fig_station.update_traces(textposition="outside", cliponaxis=False)
        fig_station.update_layout(coloraxis_showscale=False)
        st.plotly_chart(polish_figure(fig_station, height=480), use_container_width=True)

    with col2:
        station_category = fdf.groupby(["stasiun", "categori"], as_index=False).size().rename(columns={"size": "jumlah"})
        station_category["persentase"] = station_category["jumlah"] / station_category.groupby("stasiun")["jumlah"].transform("sum") * 100
        fig_stack = px.bar(
            station_category,
            y="stasiun",
            x="persentase",
            color="categori",
            orientation="h",
            category_orders={"categori": CATEGORY_ORDER},
            color_discrete_map=CATEGORY_COLORS,
            title="Distribusi kategori ISPU per stasiun",
            labels={"stasiun": "Stasiun", "persentase": "Persentase", "categori": "Kategori"},
        )
        fig_stack.update_layout(barmode="stack")
        st.plotly_chart(polish_figure(fig_stack, height=480), use_container_width=True)

    fig_box = px.box(
        fdf,
        x="stasiun",
        y="max",
        color="stasiun",
        title="Sebaran nilai ISPU per stasiun",
        labels={"stasiun": "Stasiun", "max": "ISPU"},
    )
    fig_box.update_layout(showlegend=False)
    fig_box.update_xaxes(tickangle=-15)
    st.plotly_chart(polish_figure(fig_box, height=380), use_container_width=True)

    worst_unhealthy = station_metric.sort_values("tidak_sehat", ascending=False).iloc[0]
    insight_card(
        "Analisis & insight antar stasiun",
        f"Stasiun dengan rata-rata ISPU tertinggi adalah <b>{html.escape(worst_station)}</b>, sedangkan yang terendah adalah <b>{html.escape(best_station)}</b>. Dari sisi proporsi Tidak Sehat+, stasiun tertinggi adalah <b>{html.escape(worst_unhealthy['stasiun'])}</b> sebesar <b>{fmt_pct(worst_unhealthy['tidak_sehat'])}</b>.",
        "Prioritaskan intervensi menggunakan dua indikator sekaligus: rata-rata ISPU dan frekuensi Tidak Sehat+. Pendekatan ini mencegah keputusan yang hanya bergantung pada satu angka rata-rata."
    )

# ============================================================
# Visualisasi 4 — Pencemar kritis
# ============================================================
with tabs[3]:
    section_header(
        "Visualisasi 4",
        "Analisis parameter pencemar kritis",
        "Menjawab parameter apa yang paling sering menentukan nilai ISPU tertinggi dan apakah karakteristik pencemar berbeda antar stasiun atau periode."
    )

    critical_count = fdf["critical"].value_counts().reset_index()
    critical_count.columns = ["critical", "jumlah"]
    critical_count["persentase"] = critical_count["jumlah"] / critical_count["jumlah"].sum() * 100
    top_critical = critical_count.iloc[0]["critical"] if not critical_count.empty else "-"
    top_critical_pct = critical_count.iloc[0]["persentase"] / 100 if not critical_count.empty else np.nan

    col1, col2 = st.columns([1, 1.1])
    with col1:
        fig_crit = px.bar(
            critical_count.sort_values("jumlah"),
            y="critical",
            x="jumlah",
            orientation="h",
            color="critical",
            color_discrete_map=CRITICAL_COLORS,
            text=critical_count.sort_values("jumlah")["persentase"].map(lambda x: f"{x:.1f}%"),
            title=f"{top_critical} paling sering menjadi pencemar kritis",
            labels={"critical": "Pencemar", "jumlah": "Jumlah observasi"},
        )
        fig_crit.update_traces(textposition="outside", cliponaxis=False)
        fig_crit.update_layout(showlegend=False)
        st.plotly_chart(polish_figure(fig_crit, height=470), use_container_width=True)

    with col2:
        crit_station = fdf.groupby(["stasiun", "critical"], as_index=False).size().rename(columns={"size": "jumlah"})
        fig_heat = px.density_heatmap(
            crit_station,
            x="critical",
            y="stasiun",
            z="jumlah",
            histfunc="sum",
            color_continuous_scale=["#F9FCFA", "#D9FBEF", "#14B8A6", "#0F766E", "#134E4A"],
            title="Frekuensi pencemar kritis menurut stasiun",
            labels={"critical": "Pencemar", "stasiun": "Stasiun", "jumlah": "Frekuensi"},
        )
        st.plotly_chart(polish_figure(fig_heat, height=470), use_container_width=True)

    crit_trend = fdf.groupby(["tahun", "critical"], as_index=False).size().rename(columns={"size": "jumlah"})
    fig_crit_trend = px.line(
        crit_trend,
        x="tahun",
        y="jumlah",
        color="critical",
        markers=True,
        color_discrete_map=CRITICAL_COLORS,
        title="Tren kemunculan pencemar kritis per tahun",
        labels={"tahun": "Tahun", "jumlah": "Jumlah observasi", "critical": "Pencemar"},
    )
    fig_crit_trend.update_traces(line_width=2.6)
    st.plotly_chart(polish_figure(fig_crit_trend, height=420), use_container_width=True)

    station_top_critical = (
        fdf.groupby(["stasiun", "critical"]).size().reset_index(name="jumlah")
        .sort_values(["stasiun", "jumlah"], ascending=[True, False])
        .groupby("stasiun").head(1)
    )
    dominant_pairs = "; ".join([f"{row.stasiun}: {row.critical}" for row in station_top_critical.itertuples(index=False)])
    insight_card(
        "Analisis & insight pencemar kritis",
        f"Parameter <b>{html.escape(top_critical)}</b> menjadi pencemar kritis paling dominan dengan porsi <b>{fmt_pct(top_critical_pct)}</b> pada filter aktif. Namun, heatmap menunjukkan pencemar dominan dapat berbeda antar SPKU.",
        f"Rancang paket intervensi per lokasi berdasarkan pencemar dominan: <b>{html.escape(dominant_pairs)}</b>. Program pengendalian emisi menjadi lebih tepat sasaran daripada pendekatan seragam."
    )

# ============================================================
# Visualisasi 5 — Pola musiman
# ============================================================
with tabs[4]:
    section_header(
        "Visualisasi 5",
        "Pola musiman kualitas udara",
        "Menjawab bulan mana yang cenderung memiliki risiko kualitas udara lebih tinggi dan bagaimana kalender operasional dapat disusun sebelum periode rawan."
    )

    seasonal = (
        fdf.groupby(["tahun", "bulan", "nama_bulan"], observed=True, as_index=False)
        .agg(rata_rata_ispu=("max", "mean"), tidak_sehat=("is_unhealthy_or_worse", "mean"), observasi=("max", "count"))
    )
    heat = seasonal.pivot_table(index="tahun", columns="nama_bulan", values="rata_rata_ispu", aggfunc="mean", observed=True).reindex(columns=MONTH_ORDER)

    col1, col2 = st.columns([1.22, 1])
    with col1:
        fig_heatmap = px.imshow(
            heat,
            aspect="auto",
            color_continuous_scale=["#16A34A", "#F59E0B", "#EA580C", "#DC2626", "#7F1D1D"],
            title="Heatmap rata-rata ISPU per bulan dan tahun",
            labels=dict(x="Bulan", y="Tahun", color="Rata-rata ISPU"),
        )
        fig_heatmap.update_xaxes(side="top")
        st.plotly_chart(polish_figure(fig_heatmap, height=530), use_container_width=True)

    with col2:
        monthly = (
            fdf.groupby(["bulan", "nama_bulan"], observed=True, as_index=False)
            .agg(rata_rata_ispu=("max", "mean"), tidak_sehat=("is_unhealthy_or_worse", "mean"), observasi=("max", "count"))
            .sort_values("bulan")
        )
        monthly["persen_tidak_sehat"] = monthly["tidak_sehat"] * 100
        worst_month = monthly.sort_values("rata_rata_ispu", ascending=False).iloc[0]
        best_month = monthly.sort_values("rata_rata_ispu", ascending=True).iloc[0]

        fig_month = px.bar(
            monthly,
            x="nama_bulan",
            y="rata_rata_ispu",
            color="rata_rata_ispu",
            color_continuous_scale=["#16A34A", "#F59E0B", "#EA580C", "#DC2626"],
            title=f"Bulan terburuk: {worst_month['nama_bulan']} · terbaik: {best_month['nama_bulan']}",
            labels={"nama_bulan": "Bulan", "rata_rata_ispu": "Rata-rata ISPU"},
        )
        fig_month.update_layout(coloraxis_showscale=False)
        fig_month.update_xaxes(tickangle=-45)
        st.plotly_chart(polish_figure(fig_month, height=530), use_container_width=True)

    fig_month_unhealthy = px.line(
        monthly,
        x="nama_bulan",
        y="persen_tidak_sehat",
        markers=True,
        title="Proporsi Tidak Sehat+ menurut bulan",
        labels={"nama_bulan": "Bulan", "persen_tidak_sehat": "% Tidak Sehat+"},
    )
    fig_month_unhealthy.update_traces(line_color="#DC2626", line_width=3, marker_size=9)
    fig_month_unhealthy.update_xaxes(tickangle=-45)
    st.plotly_chart(polish_figure(fig_month_unhealthy, height=350), use_container_width=True)

    insight_card(
        "Analisis & insight pola musiman",
        f"Pada filter aktif, <b>{html.escape(str(worst_month['nama_bulan']))}</b> memiliki rata-rata ISPU tertinggi sebesar <b>{fmt_number(worst_month['rata_rata_ispu'])}</b>, sedangkan <b>{html.escape(str(best_month['nama_bulan']))}</b> terendah sebesar <b>{fmt_number(best_month['rata_rata_ispu'])}</b>. Persentase Tidak Sehat+ pada bulan terburuk adalah <b>{fmt_pct(worst_month['tidak_sehat'])}</b>.",
        "Susun kalender kewaspadaan menjelang bulan berisiko tinggi. Hubungan dengan musim hujan/kemarau perlu dikonfirmasi dengan data meteorologi, tetapi pola ISPU sudah cukup untuk memulai penguatan operasi sebelum risiko meningkat."
    )

# ============================================================
# Lampiran & ekspor
# ============================================================
with tabs[5]:
    section_header(
        "Lampiran",
        "Data terfilter, catatan interpretasi, dan rekomendasi operasional",
        "Bagian ini memastikan dashboard dapat digunakan saat demo langsung, sekaligus menyediakan data yang sama dengan filter aktif untuk analisis lanjutan."
    )

    rec_cols = st.columns(3)
    with rec_cols[0]:
        st.markdown(
            """
            <div class="mini-card">
                <span class="pill pill-teal">Lokasi</span>
                <p><b>Prioritaskan stasiun berisiko.</b><br/>Gunakan kombinasi rata-rata ISPU dan % Tidak Sehat+ untuk menentukan lokasi intervensi bulanan.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with rec_cols[1]:
        st.markdown(
            """
            <div class="mini-card">
                <span class="pill pill-amber">Polutan</span>
                <p><b>Bedakan strategi per pencemar.</b><br/>Fokus program disesuaikan dengan pencemar dominan: O3, PM2.5, PM10, atau parameter lain sesuai filter.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with rec_cols[2]:
        st.markdown(
            """
            <div class="mini-card">
                <span class="pill pill-red">Musiman</span>
                <p><b>Aktifkan kalender kewaspadaan.</b><br/>Perkuat pemantauan dan komunikasi risiko sebelum bulan dengan rata-rata ISPU tertinggi.</p>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("#### Data terfilter")
    columns_to_show = ["tanggal", "stasiun", "pm10", "pm25", "so2", "co", "o3", "no2", "max", "critical", "categori", "quality_notes"]
    existing_columns = [c for c in columns_to_show if c in fdf.columns]
    st.dataframe(fdf[existing_columns].sort_values(["tanggal", "stasiun"]), use_container_width=True, hide_index=True, height=420)
    make_download(fdf, "ispu_jakarta_data_terfilter.csv")

    st.markdown(
        """
        <div class="mini-card">
            <p><b>Catatan interpretasi:</b> Dashboard ini bersifat deskriptif dan diagnostik. Hasilnya menunjukkan lokasi, waktu, dan parameter prioritas, tetapi belum membuktikan penyebab polusi secara kausal. Untuk analisis penyebab, integrasikan data meteorologi, lalu lintas, aktivitas industri, kepadatan penduduk, dan sumber emisi lain.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
