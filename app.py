from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ============================================================
# Konfigurasi halaman
# ============================================================
st.set_page_config(
    page_title="Dashboard ISPU Jakarta | Dinas Lingkungan Hidup DKI Jakarta",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Design tokens
# ============================================================
INK = "#17201D"
MUTED = "#64736D"
SURFACE = "#FFFFFF"
CANVAS = "#EEF3F0"
MOSS = "#1E7F63"
MOSS_DARK = "#0F5B45"
MIST = "#DDE7E2"
SKY = "#8AB6D6"
AMBER = "#E3A539"
ORANGE = "#C76E3B"
DANGER = "#B84A4A"
VIOLET = "#7C6BB0"
STEEL = "#45606F"

CATEGORY_ORDER = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CATEGORY_COLORS = {
    "BAIK": "#2F9E44",
    "SEDANG": "#E3A539",
    "TIDAK SEHAT": "#D77A3D",
    "SANGAT TIDAK SEHAT": "#B84A4A",
    "BERBAHAYA": "#6B1D1D",
}
CRITICAL_COLORS = {
    "PM10": "#7A5C3E",
    "PM2.5": "#3B5B92",
    "O3": "#5D8B59",
    "CO": "#A85D7A",
    "SO2": "#6C7A89",
    "NO2": "#9E7D22",
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

# ============================================================
# CSS: identitas visual dashboard
# ============================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700;800&family=Sora:wght@500;600;700;800&display=swap');

        :root {{
            --ink: {INK};
            --muted: {MUTED};
            --surface: {SURFACE};
            --canvas: {CANVAS};
            --moss: {MOSS};
            --moss-dark: {MOSS_DARK};
            --mist: {MIST};
            --amber: {AMBER};
            --danger: {DANGER};
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--ink);
        }}

        .stApp {{
            background:
                radial-gradient(circle at 10% -10%, rgba(30, 127, 99, 0.18), transparent 34%),
                radial-gradient(circle at 86% 12%, rgba(138, 182, 214, 0.22), transparent 30%),
                linear-gradient(180deg, #EEF3F0 0%, #F8FAF8 38%, #EEF3F0 100%);
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #12231E 0%, #1B352D 62%, #203E35 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }}
        section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.92) !important; }}
        section[data-testid="stSidebar"] label {{ font-weight: 700 !important; }}
        section[data-testid="stSidebar"] [data-baseweb="tag"] {{ background-color: rgba(141, 190, 170, 0.22) !important; }}
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {{ color: rgba(255,255,255,0.72) !important; }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(23, 32, 29, 0.12);
            background:
                linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(243,248,245,0.92) 52%, rgba(211,228,219,0.72) 100%);
            border-radius: 28px;
            padding: 30px 34px;
            box-shadow: 0 24px 70px rgba(23, 32, 29, 0.10);
        }}
        .hero:after {{
            content: "";
            position: absolute;
            inset: auto -8% -42% auto;
            width: 520px;
            height: 520px;
            background: conic-gradient(from 190deg, rgba(30,127,99,.0), rgba(30,127,99,.22), rgba(227,165,57,.18), rgba(138,182,214,.10), rgba(30,127,99,.0));
            filter: blur(4px);
            border-radius: 50%;
            pointer-events: none;
        }}
        .eyebrow {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            letter-spacing: .12em;
            text-transform: uppercase;
            color: var(--moss-dark);
            font-weight: 700;
            margin-bottom: .7rem;
        }}
        .hero h1 {{
            font-family: 'Sora', sans-serif;
            font-size: clamp(2.1rem, 5vw, 4.1rem);
            line-height: .98;
            letter-spacing: -0.055em;
            margin: 0 0 1rem 0;
            color: var(--ink);
            max-width: 980px;
        }}
        .hero p {{
            color: var(--muted);
            max-width: 880px;
            font-size: 1.05rem;
            line-height: 1.68;
            margin: 0;
        }}
        .station-strip {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 22px;
            position: relative;
            z-index: 2;
        }}
        .station-chip {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.76rem;
            color: var(--ink);
            background: rgba(255,255,255,.76);
            border: 1px solid rgba(23, 32, 29, 0.12);
            border-radius: 999px;
            padding: 8px 12px;
        }}

        .section-title {{
            margin: 2.2rem 0 .9rem 0;
            font-family: 'Sora', sans-serif;
            font-weight: 800;
            letter-spacing: -0.035em;
            color: var(--ink);
        }}
        .section-kicker {{
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: var(--moss-dark);
            font-size: .76rem;
            font-weight: 700;
            margin-top: 2rem;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 6px 0;
        }}
        @media (max-width: 980px) {{ .metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
        @media (max-width: 620px) {{ .metric-grid {{ grid-template-columns: 1fr; }} }}
        .metric-card {{
            background: rgba(255,255,255,.86);
            border: 1px solid rgba(23, 32, 29, 0.10);
            border-radius: 22px;
            padding: 18px 18px 16px 18px;
            box-shadow: 0 18px 42px rgba(23, 32, 29, 0.08);
        }}
        .metric-label {{
            color: var(--muted);
            font-size: .8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .06em;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-family: 'Sora', sans-serif;
            color: var(--ink);
            font-size: 2.02rem;
            letter-spacing: -0.045em;
            font-weight: 800;
            line-height: 1;
        }}
        .metric-note {{
            color: var(--muted);
            font-size: .86rem;
            line-height: 1.45;
            margin-top: 10px;
        }}
        .insight-card {{
            background: linear-gradient(135deg, rgba(30,127,99,.10), rgba(255,255,255,.72));
            border: 1px solid rgba(30, 127, 99, 0.20);
            border-radius: 22px;
            padding: 18px 20px;
            box-shadow: 0 16px 42px rgba(23, 32, 29, 0.06);
            margin: 14px 0 26px 0;
        }}
        .insight-title {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: .78rem;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: var(--moss-dark);
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .insight-card p {{
            margin: 0;
            color: var(--ink);
            line-height: 1.65;
        }}
        .small-note {{ color: var(--muted); font-size: .88rem; line-height: 1.55; }}
        .footer-note {{
            color: var(--muted);
            font-size: .85rem;
            border-top: 1px solid rgba(23,32,29,.10);
            margin-top: 2rem;
            padding-top: 1rem;
        }}
        div[data-testid="stMetric"] {{
            background: rgba(255,255,255,.78);
            border-radius: 18px;
            padding: 14px 16px;
            border: 1px solid rgba(23,32,29,.08);
        }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,.72);
            border-radius: 999px;
            border: 1px solid rgba(23,32,29,.08);
            padding: 8px 14px;
        }}
        .stTabs [aria-selected="true"] {{
            background: #173D32 !important;
            color: white !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Data loading dan utilitas
# ============================================================
DATA_PATH = Path(__file__).parent / "data" / "ispu_jakarta_bersih.csv"

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal", "stasiun", "max", "categori", "critical"]).copy()
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.month
    if "nama_bulan" not in df.columns:
        month_map = dict(zip(range(1, 13), MONTH_ORDER))
        df["nama_bulan"] = df["bulan"].map(month_map)
    df["nama_bulan"] = pd.Categorical(df["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    df["categori"] = pd.Categorical(df["categori"], categories=CATEGORY_ORDER, ordered=True)
    df["is_unhealthy_or_worse"] = df["categori"].isin(["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"])
    return df.sort_values(["tanggal", "stasiun"]).reset_index(drop=True)

def fmt_number(value: float, decimals: int = 1) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(value: float, decimals: int = 1) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:.{decimals}f}%".replace(".", ",")

def category_from_ispu(value: float) -> str:
    if value <= 50:
        return "BAIK"
    if value <= 100:
        return "SEDANG"
    if value <= 199:
        return "TIDAK SEHAT"
    if value <= 299:
        return "SANGAT TIDAK SEHAT"
    return "BERBAHAYA"

def aggregate_time(df: pd.DataFrame, granularity: str) -> Tuple[pd.DataFrame, str]:
    if granularity == "Harian":
        tmp = df.copy()
        tmp["periode_visual"] = tmp["tanggal"].dt.to_period("D").dt.to_timestamp()
        x_title = "Tanggal"
    elif granularity == "Bulanan":
        tmp = df.copy()
        tmp["periode_visual"] = tmp["tanggal"].dt.to_period("M").dt.to_timestamp()
        x_title = "Bulan"
    else:
        tmp = df.copy()
        tmp["periode_visual"] = tmp["tanggal"].dt.to_period("Y").dt.to_timestamp()
        x_title = "Tahun"

    out = (
        tmp.groupby(["periode_visual", "stasiun"], observed=True)
        .agg(
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            hari_tidak_sehat=("is_unhealthy_or_worse", "sum"),
            jumlah_observasi=("max", "count"),
        )
        .reset_index()
    )
    out["persen_tidak_sehat"] = out["hari_tidak_sehat"] / out["jumlah_observasi"] * 100
    return out, x_title

def latest_station_status(df: pd.DataFrame) -> pd.DataFrame:
    idx = df.sort_values("tanggal").groupby("stasiun", observed=True).tail(1).index
    latest = df.loc[idx, ["tanggal", "stasiun", "max", "categori", "critical"]].copy()
    latest["lat"] = latest["stasiun"].map(lambda s: STATION_COORDS.get(s, (np.nan, np.nan))[0])
    latest["lon"] = latest["stasiun"].map(lambda s: STATION_COORDS.get(s, (np.nan, np.nan))[1])
    latest["status_ringkas"] = latest["stasiun"] + " • " + latest["categori"].astype(str) + " • ISPU " + latest["max"].round(0).astype(int).astype(str)
    return latest.sort_values("max", ascending=False)

def quality_headline(df: pd.DataFrame) -> Dict[str, object]:
    avg_ispu = df["max"].mean()
    unhealthy_pct = df["is_unhealthy_or_worse"].mean() * 100 if len(df) else np.nan
    dominant_pollutant = df["critical"].value_counts().idxmax() if len(df) else "-"
    dominant_pollutant_share = df["critical"].value_counts(normalize=True).max() * 100 if len(df) else np.nan
    station_risk = (
        df.groupby("stasiun", observed=True)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat=("is_unhealthy_or_worse", lambda x: x.mean() * 100), n=("max", "count"))
        .reset_index()
    )
    worst_station = station_risk.sort_values(["persen_tidak_sehat", "rata_rata_ispu"], ascending=False).iloc[0]["stasiun"] if len(station_risk) else "-"
    best_station = station_risk.sort_values(["persen_tidak_sehat", "rata_rata_ispu"], ascending=True).iloc[0]["stasiun"] if len(station_risk) else "-"
    return {
        "avg_ispu": avg_ispu,
        "unhealthy_pct": unhealthy_pct,
        "dominant_pollutant": dominant_pollutant,
        "dominant_pollutant_share": dominant_pollutant_share,
        "worst_station": worst_station,
        "best_station": best_station,
        "station_risk": station_risk,
    }

def year_extremes(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
    yearly = (
        df.groupby("tahun", observed=True)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat=("is_unhealthy_or_worse", lambda x: x.mean() * 100), jumlah_observasi=("max", "count"))
        .reset_index()
        .sort_values("tahun")
    )
    if yearly.empty:
        return "-", "-", yearly
    best = yearly.loc[yearly["rata_rata_ispu"].idxmin(), "tahun"]
    worst = yearly.loc[yearly["rata_rata_ispu"].idxmax(), "tahun"]
    return str(int(best)), str(int(worst)), yearly

def insight_box(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{title}</div>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def metric_cards(items: List[Tuple[str, str, str]]) -> None:
    html = '<div class="metric-grid">'
    for label, value, note in items:
        html += f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def apply_chart_layout(fig: go.Figure, height: int = 480) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.72)",
        font=dict(family="Inter, Arial, sans-serif", color=INK),
        title=dict(font=dict(family="Sora, Inter, sans-serif", size=20, color=INK), x=0.01, xanchor="left"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=24, r=24, t=72, b=36),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(23,32,29,0.07)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(23,32,29,0.07)", zeroline=False)
    return fig

# ============================================================
# Load data
# ============================================================
try:
    df_all = load_data(DATA_PATH)
except FileNotFoundError:
    st.error("File data tidak ditemukan. Pastikan `data/ispu_jakarta_bersih.csv` berada dalam repository yang sama dengan `app.py`.")
    st.stop()

# ============================================================
# Sidebar filters
# ============================================================
st.sidebar.markdown("## Panel kendali")
st.sidebar.markdown("Pilih periode, stasiun, dan kategori untuk menyesuaikan seluruh visualisasi.")

min_date = df_all["tanggal"].min().date()
max_date = df_all["tanggal"].max().date()
selected_dates = st.sidebar.date_input(
    "Rentang tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date, end_date = min_date, max_date

station_options = sorted(df_all["stasiun"].dropna().unique().tolist())
selected_stations = st.sidebar.multiselect("Stasiun SPKU", station_options, default=station_options)

category_options = [cat for cat in CATEGORY_ORDER if cat in df_all["categori"].astype(str).unique()]
selected_categories = st.sidebar.multiselect("Kategori ISPU", category_options, default=category_options)

pollutant_options = sorted(df_all["critical"].dropna().unique().tolist())
selected_pollutants = st.sidebar.multiselect("Pencemar kritis", pollutant_options, default=pollutant_options)

granularity = st.sidebar.radio("Granularitas tren", ["Harian", "Bulanan", "Tahunan"], index=1, horizontal=False)

show_data = st.sidebar.toggle("Tampilkan data hasil filter", value=False)

mask = (
    (df_all["tanggal"].dt.date >= start_date)
    & (df_all["tanggal"].dt.date <= end_date)
    & (df_all["stasiun"].isin(selected_stations))
    & (df_all["categori"].astype(str).isin(selected_categories))
    & (df_all["critical"].isin(selected_pollutants))
)
df = df_all.loc[mask].copy()

if df.empty:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Dashboard ISPU Jakarta</div>
            <h1>Tidak ada data pada kombinasi filter yang dipilih.</h1>
            <p>Perluas rentang tanggal, aktifkan kembali beberapa stasiun, atau pilih kategori dan pencemar kritis yang lebih luas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

headline = quality_headline(df)
best_year, worst_year, yearly_summary = year_extremes(df)
latest_status = latest_station_status(df)

# ============================================================
# Hero
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Dinas Lingkungan Hidup DKI Jakarta · Business Intelligence Dashboard</div>
        <h1>Ruang Kendali ISPU Jakarta</h1>
        <p>Dashboard ini merangkum kondisi kualitas udara harian dari 5 SPKU DKI Jakarta, menelusuri pola waktu, membandingkan risiko antar stasiun, dan mengidentifikasi pencemar kritis yang paling perlu ditindaklanjuti.</p>
        <div class="station-strip">
            <span class="station-chip">DKI1 · Bunderan HI</span>
            <span class="station-chip">DKI2 · Kelapa Gading</span>
            <span class="station-chip">DKI3 · Jagakarsa</span>
            <span class="station-chip">DKI4 · Lubang Buaya</span>
            <span class="station-chip">DKI5 · Kebon Jeruk</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

period_text = f"{pd.to_datetime(start_date).strftime('%d %b %Y')} – {pd.to_datetime(end_date).strftime('%d %b %Y')}"
metric_cards(
    [
        ("Rata-rata ISPU", fmt_number(headline["avg_ispu"], 1), f"Periode terpilih: {period_text}"),
        ("Hari tidak sehat+", fmt_pct(headline["unhealthy_pct"], 1), "Kategori TIDAK SEHAT, SANGAT TIDAK SEHAT, dan BERBAHAYA"),
        ("Pencemar dominan", str(headline["dominant_pollutant"]), f"Muncul pada {fmt_pct(headline['dominant_pollutant_share'], 1)} observasi"),
        ("Stasiun prioritas", str(headline["worst_station"]).replace("DKI", "DKI "), "Prioritas berdasarkan kombinasi rata-rata ISPU dan proporsi hari tidak sehat"),
    ]
)

st.markdown(
    f"<p class='small-note'>Dataset yang sedang ditampilkan berisi <strong>{len(df):,}</strong> observasi dari <strong>{df['stasiun'].nunique()}</strong> stasiun. Tahun dengan rata-rata ISPU terbaik pada filter ini adalah <strong>{best_year}</strong>, sedangkan tahun dengan rata-rata ISPU terburuk adalah <strong>{worst_year}</strong>.</p>".replace(",", "."),
    unsafe_allow_html=True,
)

# ============================================================
# Tabs for 5 visualizations
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1 · Overview",
    "2 · Tren temporal",
    "3 · Antar stasiun",
    "4 · Pencemar kritis",
    "5 · Pola musiman",
])

# ------------------------------------------------------------
# Visualisasi 1: Overview
# ------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-kicker">Visualisasi 1</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Overview kualitas udara Jakarta</h2>', unsafe_allow_html=True)

    col_map, col_table = st.columns([1.15, 0.85], gap="large")

    with col_map:
        map_df = latest_status.dropna(subset=["lat", "lon"]).copy()
        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            size="max",
            color="categori",
            color_discrete_map=CATEGORY_COLORS,
            hover_name="stasiun",
            hover_data={"max": ":.0f", "critical": True, "tanggal": "|%d %b %Y", "lat": False, "lon": False},
            zoom=10,
            center={"lat": -6.22, "lon": 106.84},
            title="Status terkini per SPKU memperlihatkan lokasi yang membutuhkan perhatian paling cepat",
            size_max=34,
            mapbox_style="open-street-map",
        )
        fig_map.update_layout(mapbox=dict(bearing=0, pitch=0))
        apply_chart_layout(fig_map, height=500)
        fig_map.update_layout(margin=dict(l=0, r=0, t=72, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_table:
        display_latest = latest_status[["tanggal", "stasiun", "max", "categori", "critical"]].copy()
        display_latest["tanggal"] = display_latest["tanggal"].dt.strftime("%d %b %Y")
        display_latest["max"] = display_latest["max"].round(0).astype(int)
        st.dataframe(
            display_latest.rename(columns={
                "tanggal": "Tanggal terakhir",
                "stasiun": "SPKU",
                "max": "ISPU",
                "categori": "Kategori",
                "critical": "Pencemar kritis",
            }),
            use_container_width=True,
            hide_index=True,
        )

    risk_level = category_from_ispu(headline["avg_ispu"])
    insight_box(
        "Analisis utama",
        f"Rata-rata ISPU pada filter aktif berada pada angka {fmt_number(headline['avg_ispu'], 1)} atau setara kategori {risk_level}. Sebanyak {fmt_pct(headline['unhealthy_pct'], 1)} observasi masuk kategori Tidak Sehat atau lebih buruk. Parameter yang paling sering menjadi pencemar kritis adalah {headline['dominant_pollutant']}.",
    )
    insight_box(
        "Insight tindak lanjut",
        f"Dinas dapat memprioritaskan pengendalian pada {headline['worst_station']} dan menyiapkan komunikasi risiko publik ketika indikator harian bergerak menuju kategori Tidak Sehat. Fokus program awal perlu diarahkan pada pencemar dominan {headline['dominant_pollutant']} tanpa mengabaikan variasi antar stasiun.",
    )

# ------------------------------------------------------------
# Visualisasi 2: Tren Temporal
# ------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-kicker">Visualisasi 2</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Tren temporal kualitas udara</h2>', unsafe_allow_html=True)

    trend_df, x_title = aggregate_time(df, granularity)
    fig_trend = px.line(
        trend_df,
        x="periode_visual",
        y="rata_rata_ispu",
        color="stasiun",
        markers=(granularity != "Harian"),
        title=f"Tren {granularity.lower()} menunjukkan kapan tekanan kualitas udara meningkat",
        labels={"periode_visual": x_title, "rata_rata_ispu": "Rata-rata ISPU", "stasiun": "SPKU"},
        color_discrete_sequence=[MOSS, STEEL, AMBER, ORANGE, VIOLET],
    )
    fig_trend.add_hrect(y0=100, y1=max(105, trend_df["rata_rata_ispu"].max() * 1.08), line_width=0, fillcolor="rgba(184,74,74,0.10)", annotation_text="Zona Tidak Sehat+", annotation_position="top left")
    apply_chart_layout(fig_trend, height=510)
    st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns([0.6, 0.4], gap="large")
    with c1:
        if not yearly_summary.empty:
            fig_year = px.bar(
                yearly_summary,
                x="tahun",
                y="rata_rata_ispu",
                color="persen_tidak_sehat",
                color_continuous_scale=[[0, "#2F9E44"], [0.5, "#E3A539"], [1, "#B84A4A"]],
                title="Perbandingan tahunan membantu menemukan tahun terbaik dan terburuk",
                labels={"tahun": "Tahun", "rata_rata_ispu": "Rata-rata ISPU", "persen_tidak_sehat": "% Tidak Sehat+"},
            )
            apply_chart_layout(fig_year, height=390)
            st.plotly_chart(fig_year, use_container_width=True)
    with c2:
        st.metric("Tahun kualitas udara terbaik", best_year)
        st.metric("Tahun kualitas udara terburuk", worst_year)
        if not yearly_summary.empty and len(yearly_summary) >= 2:
            first_val = yearly_summary.iloc[0]["rata_rata_ispu"]
            last_val = yearly_summary.iloc[-1]["rata_rata_ispu"]
            direction = "meningkat" if last_val > first_val else "menurun"
            st.markdown(f"<p class='small-note'>Dibanding tahun awal pada filter, rata-rata ISPU tahun terakhir terlihat <strong>{direction}</strong> sebesar {fmt_number(abs(last_val-first_val), 1)} poin.</p>", unsafe_allow_html=True)

    if not yearly_summary.empty:
        worst_row = yearly_summary.loc[yearly_summary["rata_rata_ispu"].idxmax()]
        best_row = yearly_summary.loc[yearly_summary["rata_rata_ispu"].idxmin()]
        insight_box(
            "Analisis utama",
            f"Tahun {int(worst_row['tahun'])} memiliki rata-rata ISPU tertinggi sebesar {fmt_number(worst_row['rata_rata_ispu'], 1)}, sedangkan tahun {int(best_row['tahun'])} memiliki rata-rata ISPU terendah sebesar {fmt_number(best_row['rata_rata_ispu'], 1)}. Perbandingan ini menunjukkan periode mana yang perlu ditelusuri lebih lanjut dari sisi kebijakan dan kondisi operasional.",
        )
        insight_box(
            "Insight tindak lanjut",
            f"Periode dengan lonjakan ISPU perlu dipakai sebagai kalender kewaspadaan. Saat memasuki pola waktu yang mirip dengan tahun {int(worst_row['tahun'])}, DLH dapat meningkatkan pengawasan sumber emisi, menyiapkan pesan kesehatan publik, dan memperkuat kesiapan SPKU.",
        )

# ------------------------------------------------------------
# Visualisasi 3: Perbandingan Antar Stasiun
# ------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-kicker">Visualisasi 3</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Perbandingan kualitas udara antar SPKU</h2>', unsafe_allow_html=True)

    station_summary = (
        df.groupby("stasiun", observed=True)
        .agg(
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            persen_tidak_sehat=("is_unhealthy_or_worse", lambda x: x.mean() * 100),
            jumlah_observasi=("max", "count"),
        )
        .reset_index()
        .sort_values("rata_rata_ispu", ascending=False)
    )

    fig_station = make_subplots(specs=[[{"secondary_y": True}]])
    fig_station.add_trace(
        go.Bar(
            x=station_summary["stasiun"],
            y=station_summary["rata_rata_ispu"],
            name="Rata-rata ISPU",
            marker_color=MOSS,
            text=station_summary["rata_rata_ispu"].round(1),
            textposition="outside",
        ),
        secondary_y=False,
    )
    fig_station.add_trace(
        go.Scatter(
            x=station_summary["stasiun"],
            y=station_summary["persen_tidak_sehat"],
            name="% Tidak Sehat+",
            mode="lines+markers+text",
            marker=dict(size=10, color=DANGER),
            line=dict(color=DANGER, width=3),
            text=station_summary["persen_tidak_sehat"].map(lambda x: fmt_pct(x, 1)),
            textposition="top center",
        ),
        secondary_y=True,
    )
    fig_station.update_yaxes(title_text="Rata-rata ISPU", secondary_y=False)
    fig_station.update_yaxes(title_text="% Tidak Sehat+", secondary_y=True, ticksuffix="%")
    fig_station.update_layout(title="Perbandingan SPKU menunjukkan lokasi prioritas intervensi", xaxis_title="SPKU")
    apply_chart_layout(fig_station, height=500)
    st.plotly_chart(fig_station, use_container_width=True)

    category_dist = (
        df.groupby(["stasiun", "categori"], observed=True)
        .size()
        .reset_index(name="jumlah")
    )
    category_dist["persen"] = category_dist.groupby("stasiun", observed=True)["jumlah"].transform(lambda x: x / x.sum() * 100)
    category_dist["categori"] = pd.Categorical(category_dist["categori"], categories=CATEGORY_ORDER, ordered=True)

    fig_cat = px.bar(
        category_dist.sort_values(["stasiun", "categori"]),
        x="stasiun",
        y="persen",
        color="categori",
        color_discrete_map=CATEGORY_COLORS,
        title="Distribusi kategori udara memperlihatkan profil risiko setiap SPKU",
        labels={"stasiun": "SPKU", "persen": "Persentase observasi", "categori": "Kategori"},
        text=category_dist["persen"].map(lambda x: f"{x:.0f}%"),
    )
    fig_cat.update_layout(barmode="stack", yaxis_ticksuffix="%")
    apply_chart_layout(fig_cat, height=460)
    st.plotly_chart(fig_cat, use_container_width=True)

    worst_station = station_summary.iloc[0]
    best_station = station_summary.sort_values("rata_rata_ispu", ascending=True).iloc[0]
    insight_box(
        "Analisis utama",
        f"{worst_station['stasiun']} memiliki rata-rata ISPU tertinggi sebesar {fmt_number(worst_station['rata_rata_ispu'], 1)} dengan {fmt_pct(worst_station['persen_tidak_sehat'], 1)} observasi Tidak Sehat atau lebih buruk. Sebaliknya, {best_station['stasiun']} menunjukkan rata-rata ISPU terendah sebesar {fmt_number(best_station['rata_rata_ispu'], 1)}.",
    )
    insight_box(
        "Insight tindak lanjut",
        f"Intervensi tidak perlu dibuat seragam untuk semua wilayah. Stasiun dengan kombinasi rata-rata ISPU tinggi dan proporsi Tidak Sehat tinggi dapat menjadi prioritas pemeriksaan sumber emisi, evaluasi kepadatan aktivitas, dan penajaman program pengendalian pencemaran udara setempat.",
    )

# ------------------------------------------------------------
# Visualisasi 4: Parameter Pencemar Kritis
# ------------------------------------------------------------
with tab4:
    st.markdown('<div class="section-kicker">Visualisasi 4</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Analisis parameter pencemar kritis</h2>', unsafe_allow_html=True)

    crit_counts = df["critical"].value_counts().reset_index()
    crit_counts.columns = ["critical", "jumlah"]
    crit_counts["persen"] = crit_counts["jumlah"] / crit_counts["jumlah"].sum() * 100

    col_a, col_b = st.columns([0.42, 0.58], gap="large")
    with col_a:
        fig_donut = px.pie(
            crit_counts,
            names="critical",
            values="jumlah",
            hole=0.52,
            color="critical",
            color_discrete_map=CRITICAL_COLORS,
            title="Komposisi pencemar kritis menunjukkan fokus pengurangan emisi",
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        apply_chart_layout(fig_donut, height=480)
        st.plotly_chart(fig_donut, use_container_width=True)
    with col_b:
        crit_station = (
            df.groupby(["stasiun", "critical"], observed=True)
            .size()
            .reset_index(name="jumlah")
        )
        crit_station["persen"] = crit_station.groupby("stasiun", observed=True)["jumlah"].transform(lambda x: x / x.sum() * 100)
        fig_crit_station = px.bar(
            crit_station,
            x="stasiun",
            y="persen",
            color="critical",
            color_discrete_map=CRITICAL_COLORS,
            title="Karakteristik pencemar tidak selalu sama antar SPKU",
            labels={"stasiun": "SPKU", "persen": "Persentase kemunculan", "critical": "Pencemar kritis"},
        )
        fig_crit_station.update_layout(barmode="stack", yaxis_ticksuffix="%")
        apply_chart_layout(fig_crit_station, height=480)
        st.plotly_chart(fig_crit_station, use_container_width=True)

    tmp_crit = df.copy()
    tmp_crit["periode_bulan"] = tmp_crit["tanggal"].dt.to_period("M").dt.to_timestamp()
    crit_trend = tmp_crit.groupby(["periode_bulan", "critical"], observed=True).size().reset_index(name="jumlah")
    fig_crit_trend = px.area(
        crit_trend,
        x="periode_bulan",
        y="jumlah",
        color="critical",
        color_discrete_map=CRITICAL_COLORS,
        title="Tren kemunculan pencemar kritis memperlihatkan kapan tiap polutan mendominasi",
        labels={"periode_bulan": "Bulan", "jumlah": "Jumlah kemunculan", "critical": "Pencemar kritis"},
    )
    apply_chart_layout(fig_crit_trend, height=460)
    st.plotly_chart(fig_crit_trend, use_container_width=True)

    top_crit = crit_counts.iloc[0]
    station_top = (
        crit_station.sort_values(["stasiun", "persen"], ascending=[True, False])
        .groupby("stasiun", observed=True)
        .head(1)
    )
    station_top_text = "; ".join([f"{r.stasiun}: {r.critical}" for r in station_top.itertuples()])
    insight_box(
        "Analisis utama",
        f"Parameter {top_crit['critical']} menjadi pencemar kritis paling dominan dengan kontribusi {fmt_pct(top_crit['persen'], 1)} dari seluruh observasi pada filter aktif. Komposisi per stasiun memperlihatkan apakah tekanan polusi bersifat seragam atau berbeda antar lokasi.",
    )
    insight_box(
        "Insight tindak lanjut",
        f"Program pengurangan emisi perlu disesuaikan dengan pencemar dominan masing-masing SPKU. Pola dominan saat ini: {station_top_text}. Pendekatan ini membantu DLH menempatkan intervensi berdasarkan karakteristik pencemar, bukan hanya berdasarkan rata-rata ISPU.",
    )

# ------------------------------------------------------------
# Visualisasi 5: Pola Musiman
# ------------------------------------------------------------
with tab5:
    st.markdown('<div class="section-kicker">Visualisasi 5</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Pola musiman kualitas udara</h2>', unsafe_allow_html=True)

    seasonal = (
        df.groupby(["tahun", "nama_bulan"], observed=True)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat=("is_unhealthy_or_worse", lambda x: x.mean() * 100), n=("max", "count"))
        .reset_index()
    )
    heat = seasonal.pivot(index="nama_bulan", columns="tahun", values="rata_rata_ispu").reindex(MONTH_ORDER)
    fig_heat = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale=[[0, "#2F9E44"], [0.45, "#E3A539"], [0.72, "#D77A3D"], [1, "#B84A4A"]],
        title="Heatmap bulanan menandai musim dengan tekanan polusi tertinggi",
        labels=dict(x="Tahun", y="Bulan", color="Rata-rata ISPU"),
    )
    fig_heat.update_traces(hovertemplate="Bulan: %{y}<br>Tahun: %{x}<br>Rata-rata ISPU: %{z:.1f}<extra></extra>")
    apply_chart_layout(fig_heat, height=560)
    st.plotly_chart(fig_heat, use_container_width=True)

    month_profile = (
        df.groupby("nama_bulan", observed=True)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat=("is_unhealthy_or_worse", lambda x: x.mean() * 100), jumlah_observasi=("max", "count"))
        .reset_index()
    )
    month_profile["nama_bulan"] = pd.Categorical(month_profile["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    month_profile = month_profile.sort_values("nama_bulan")

    fig_month = make_subplots(specs=[[{"secondary_y": True}]])
    fig_month.add_trace(
        go.Bar(
            x=month_profile["nama_bulan"],
            y=month_profile["rata_rata_ispu"],
            marker_color=AMBER,
            name="Rata-rata ISPU",
            text=month_profile["rata_rata_ispu"].round(1),
            textposition="outside",
        ),
        secondary_y=False,
    )
    fig_month.add_trace(
        go.Scatter(
            x=month_profile["nama_bulan"],
            y=month_profile["persen_tidak_sehat"],
            marker=dict(color=DANGER, size=10),
            line=dict(color=DANGER, width=3),
            mode="lines+markers",
            name="% Tidak Sehat+",
        ),
        secondary_y=True,
    )
    fig_month.update_layout(title="Profil bulanan membantu menyusun kalender antisipasi kualitas udara", xaxis_title="Bulan")
    fig_month.update_yaxes(title_text="Rata-rata ISPU", secondary_y=False)
    fig_month.update_yaxes(title_text="% Tidak Sehat+", ticksuffix="%", secondary_y=True)
    apply_chart_layout(fig_month, height=460)
    st.plotly_chart(fig_month, use_container_width=True)

    worst_month = month_profile.loc[month_profile["rata_rata_ispu"].idxmax()]
    best_month = month_profile.loc[month_profile["rata_rata_ispu"].idxmin()]
    insight_box(
        "Analisis utama",
        f"Bulan {worst_month['nama_bulan']} memiliki rata-rata ISPU tertinggi sebesar {fmt_number(worst_month['rata_rata_ispu'], 1)}, sedangkan bulan {best_month['nama_bulan']} memiliki rata-rata ISPU terendah sebesar {fmt_number(best_month['rata_rata_ispu'], 1)}. Pola ini menunjukkan kapan risiko kualitas udara cenderung meningkat dalam satu siklus tahunan.",
    )
    insight_box(
        "Insight tindak lanjut",
        f"Menjelang bulan {worst_month['nama_bulan']}, DLH dapat memperkuat operasi pemantauan, inspeksi sumber emisi prioritas, koordinasi pembatasan aktivitas berisiko, dan komunikasi kewaspadaan publik. Pola musiman ini dapat dipakai sebagai kalender kerja pengendalian pencemaran udara.",
    )

# ============================================================
# Data preview dan download
# ============================================================
if show_data:
    st.markdown('<h2 class="section-title">Data hasil filter</h2>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Unduh data hasil filter (.csv)",
    data=csv_bytes,
    file_name="ispu_jakarta_hasil_filter_dashboard.csv",
    mime="text/csv",
)

st.markdown(
    """
    <div class="footer-note">
        Dashboard disusun untuk demonstrasi Business Intelligence pada analisis kualitas udara Jakarta berbasis data ISPU. Seluruh indikator pada dashboard menggunakan dataset bersih hasil validasi Tugas 3–5.
    </div>
    """,
    unsafe_allow_html=True,
)
