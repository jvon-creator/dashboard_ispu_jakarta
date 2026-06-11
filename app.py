from __future__ import annotations

from pathlib import Path
from typing import Iterable

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
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Design tokens: dark-mode identity
# ============================================================
DATA_PATH = Path(__file__).parent / "data" / "ispu_jakarta_bersih.csv"

CATEGORY_ORDER = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CATEGORY_COLORS = {
    "BAIK": "#32D583",
    "SEDANG": "#FEC84B",
    "TIDAK SEHAT": "#FB923C",
    "SANGAT TIDAK SEHAT": "#F04438",
    "BERBAHAYA": "#B42318",
}
CRITICAL_COLORS = {
    "PM10": "#B98E5A",
    "PM2.5": "#6EE7F9",
    "O3": "#9FE870",
    "CO": "#F472B6",
    "SO2": "#A3A3A3",
    "NO2": "#C084FC",
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
# CSS: dark visual system
# ============================================================
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

        :root {
            --night: #071013;
            --deep: #0B171B;
            --panel: rgba(13, 28, 34, 0.78);
            --panel-strong: rgba(18, 38, 45, 0.92);
            --stroke: rgba(165, 243, 252, 0.16);
            --text: #ECFEFF;
            --muted: #95B6BE;
            --dim: #6C8790;
            --cyan: #67E8F9;
            --cyan-soft: rgba(103, 232, 249, .16);
            --lime: #A3E635;
            --amber: #FACC15;
            --orange: #FB923C;
            --red: #F04438;
            --purple: #C084FC;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: var(--text);
        }

        .stApp {
            background:
                radial-gradient(circle at 14% 0%, rgba(103, 232, 249, .18), transparent 28%),
                radial-gradient(circle at 90% 10%, rgba(192, 132, 252, .13), transparent 26%),
                radial-gradient(circle at 78% 84%, rgba(163, 230, 53, .10), transparent 24%),
                linear-gradient(180deg, #071013 0%, #0B171B 52%, #071013 100%);
        }

        .block-container {
            max-width: 1480px;
            padding-top: 1.6rem;
            padding-bottom: 3rem;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(4, 12, 15, .98) 0%, rgba(9, 24, 29, .98) 70%, rgba(11, 33, 37, .98) 100%);
            border-right: 1px solid var(--stroke);
        }
        section[data-testid="stSidebar"] * { color: var(--text) !important; }
        section[data-testid="stSidebar"] label {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: .78rem !important;
            letter-spacing: .04em !important;
            color: #BDEFFF !important;
        }
        section[data-testid="stSidebar"] [data-baseweb="tag"] {
            background: rgba(103, 232, 249, .14) !important;
            border: 1px solid rgba(103, 232, 249, .20) !important;
            border-radius: 999px !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
            color: #9BC4CD !important;
            line-height: 1.6;
        }

        /* Aesthetic risk: a subtle "air-quality radar" hero that behaves like an instrument panel. */
        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--stroke);
            background:
                linear-gradient(135deg, rgba(14, 36, 44, .92) 0%, rgba(8, 19, 23, .96) 60%, rgba(5, 15, 18, .98) 100%);
            border-radius: 30px;
            padding: 34px 36px 30px;
            box-shadow: 0 28px 90px rgba(0, 0, 0, .42), inset 0 1px 0 rgba(255,255,255,.06);
        }
        .hero:before {
            content: "";
            position: absolute;
            right: -120px;
            top: -140px;
            width: 520px;
            height: 520px;
            border-radius: 50%;
            background:
                repeating-radial-gradient(circle, rgba(103,232,249,.14) 0 1px, transparent 1px 34px),
                conic-gradient(from 110deg, rgba(103,232,249,.0), rgba(103,232,249,.26), rgba(163,230,53,.18), rgba(251,146,60,.18), rgba(103,232,249,.0));
            filter: blur(.1px);
            opacity: .78;
            pointer-events: none;
        }
        .hero:after {
            content: "ISPU / SPKU / DKI";
            position: absolute;
            right: 34px;
            bottom: 24px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: .72rem;
            letter-spacing: .22em;
            color: rgba(189, 239, 255, .35);
        }
        .eyebrow {
            font-family: 'IBM Plex Mono', monospace;
            font-size: .78rem;
            letter-spacing: .12em;
            text-transform: uppercase;
            color: var(--cyan);
            font-weight: 700;
            margin-bottom: .8rem;
        }
        .hero h1 {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(2.25rem, 5.5vw, 4.75rem);
            line-height: .92;
            letter-spacing: -.065em;
            margin: 0 0 1rem;
            max-width: 980px;
            color: var(--text);
        }
        .hero p {
            max-width: 900px;
            color: #A6C8D0;
            font-size: 1.05rem;
            line-height: 1.7;
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
            color: #DDFBFF;
            background: rgba(103, 232, 249, .10);
            border: 1px solid rgba(103, 232, 249, .18);
            border-radius: 999px;
            padding: 8px 12px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.05);
        }

        h1, h2, h3, h4 { color: var(--text); }
        .section-kicker {
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: .12em;
            text-transform: uppercase;
            color: var(--cyan);
            font-size: .74rem;
            font-weight: 700;
            margin-top: 1.4rem;
        }
        .section-title {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            font-size: clamp(1.45rem, 2.3vw, 2.15rem);
            line-height: 1.06;
            letter-spacing: -.035em;
            margin: .2rem 0 .6rem;
            color: var(--text);
        }
        .section-copy {
            color: var(--muted);
            line-height: 1.65;
            max-width: 980px;
            margin-bottom: 1rem;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin: 18px 0 12px;
        }
        @media (max-width: 980px) { .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
        @media (max-width: 640px) { .metric-grid { grid-template-columns: 1fr; } }
        .metric-card {
            background: linear-gradient(180deg, rgba(20, 43, 50, .90), rgba(12, 26, 31, .90));
            border: 1px solid var(--stroke);
            border-radius: 22px;
            padding: 18px 18px 16px;
            box-shadow: 0 18px 42px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.05);
        }
        .metric-label {
            font-family: 'IBM Plex Mono', monospace;
            color: #91E8F5;
            font-size: .74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .07em;
            margin-bottom: 9px;
        }
        .metric-value {
            font-family: 'Space Grotesk', 'Inter', sans-serif;
            color: var(--text);
            font-size: 2.14rem;
            letter-spacing: -.055em;
            font-weight: 700;
            line-height: .98;
        }
        .metric-note {
            color: var(--muted);
            font-size: .86rem;
            line-height: 1.45;
            margin-top: 10px;
        }
        .card {
            background: linear-gradient(180deg, rgba(18, 39, 46, .82), rgba(8, 20, 24, .86));
            border: 1px solid var(--stroke);
            border-radius: 22px;
            padding: 18px 20px;
            box-shadow: 0 20px 55px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.04);
            margin: 12px 0 18px;
        }
        .insight-card {
            background:
                linear-gradient(90deg, rgba(103, 232, 249, .16), rgba(163, 230, 53, .08) 52%, rgba(251, 146, 60, .09));
            border: 1px solid rgba(103, 232, 249, .23);
            border-radius: 22px;
            padding: 18px 20px;
            box-shadow: 0 20px 55px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.05);
            margin: 14px 0 20px;
        }
        .insight-title {
            font-family: 'IBM Plex Mono', monospace;
            color: #B9F7FF;
            font-size: .76rem;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-weight: 700;
            margin-bottom: 9px;
        }
        .insight-card p, .card p, .card li {
            color: #C7E5EB;
            line-height: 1.62;
            margin: 0;
        }
        .insight-card b, .card b { color: #FFFFFF; }
        .danger-tag, .good-tag, .neutral-tag {
            display: inline-block;
            border-radius: 999px;
            padding: 4px 9px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .02em;
        }
        .danger-tag { background: rgba(240, 68, 56, .15); color: #FDA29B; border: 1px solid rgba(240, 68, 56, .28); }
        .good-tag { background: rgba(50, 213, 131, .14); color: #A6F4C5; border: 1px solid rgba(50, 213, 131, .28); }
        .neutral-tag { background: rgba(103, 232, 249, .12); color: #A5F3FC; border: 1px solid rgba(103, 232, 249, .25); }

        div[data-testid="stTabs"] button {
            color: #A6C8D0;
            font-weight: 700;
            font-family: 'Inter', sans-serif;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #ECFEFF;
            border-bottom-color: #67E8F9;
        }

        [data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--stroke);
        }
        .stDownloadButton button, .stButton button {
            background: linear-gradient(90deg, rgba(103, 232, 249, .92), rgba(163, 230, 53, .85)) !important;
            color: #061013 !important;
            border: 0 !important;
            border-radius: 999px !important;
            font-weight: 800 !important;
            box-shadow: 0 12px 32px rgba(103, 232, 249, .18) !important;
        }
        footer, #MainMenu { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Utilitas data dan visualisasi
# ============================================================
@st.cache_data(show_spinner=False)
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal", "stasiun", "max", "critical", "categori"]).copy()
    df["tahun"] = df["tahun"].astype(int)
    df["bulan"] = df["bulan"].astype(int)
    df["nama_bulan"] = pd.Categorical(df["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    df["is_unhealthy_or_worse"] = df["categori"].isin(["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"])
    df["periode_harian"] = df["tanggal"].dt.date
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


def get_plot_template() -> go.layout.Template:
    template = go.layout.Template()
    template.layout = go.Layout(
        font=dict(family="Inter, Arial, sans-serif", color="#DFFBFF"),
        title=dict(font=dict(family="Space Grotesk, Inter, Arial, sans-serif", size=22, color="#ECFEFF"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(11, 23, 27, .72)",
        colorway=["#67E8F9", "#A3E635", "#FACC15", "#FB923C", "#F04438", "#C084FC", "#94A3B8"],
        xaxis=dict(gridcolor="rgba(165,243,252,.10)", zerolinecolor="rgba(165,243,252,.12)", linecolor="rgba(165,243,252,.18)"),
        yaxis=dict(gridcolor="rgba(165,243,252,.10)", zerolinecolor="rgba(165,243,252,.12)", linecolor="rgba(165,243,252,.18)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#C7E5EB")),
        margin=dict(l=30, r=30, t=70, b=35),
        hoverlabel=dict(bgcolor="#071013", bordercolor="rgba(103,232,249,.28)", font=dict(color="#ECFEFF")),
    )
    return template


PLOT_TEMPLATE = get_plot_template()


def polish_figure(fig: go.Figure, height: int = 460) -> go.Figure:
    fig.update_layout(template=PLOT_TEMPLATE, height=height)
    fig.update_xaxes(title_font=dict(color="#A6C8D0"), tickfont=dict(color="#A6C8D0"))
    fig.update_yaxes(title_font=dict(color="#A6C8D0"), tickfont=dict(color="#A6C8D0"))
    return fig


def metric_card(label: str, value: str, note: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """


def insight_card(title: str, analysis: str, action: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{title}</div>
            <p><b>Analisis utama:</b> {analysis}</p>
            <p style="margin-top:10px"><b>Insight tindak lanjut:</b> {action}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-kicker">{kicker}</div>
        <div class="section-title">{title}</div>
        <div class="section-copy">{copy}</div>
        """,
        unsafe_allow_html=True,
    )


def describe_trend(df: pd.DataFrame) -> tuple[str, float]:
    annual = df.groupby("tahun", as_index=False)["max"].mean().sort_values("tahun")
    if len(annual) < 2:
        return "belum dapat disimpulkan karena hanya ada satu tahun data pada filter ini", 0.0
    x = annual["tahun"].to_numpy(dtype=float)
    y = annual["max"].to_numpy(dtype=float)
    slope = float(np.polyfit(x, y, 1)[0])
    if slope > 0.8:
        direction = "cenderung memburuk"
    elif slope < -0.8:
        direction = "cenderung membaik"
    else:
        direction = "relatif fluktuatif/stabil"
    return direction, slope


def safe_join(items: Iterable[str], max_items: int = 3) -> str:
    selected = [str(i) for i in list(items)[:max_items]]
    if not selected:
        return "-"
    return ", ".join(selected)


# ============================================================
# Load data
# ============================================================
df = load_data()

# ============================================================
# Sidebar controls
# ============================================================
with st.sidebar:
    st.markdown("### Panel kendali")
    st.markdown("Gunakan filter ini saat presentasi untuk menunjukkan perubahan kondisi kualitas udara menurut waktu, stasiun, kategori, dan pencemar dominan.")

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
    st.caption("Dataset yang digunakan adalah clean dataset hasil validasi Tugas 3–5. Satu baris merepresentasikan satu tanggal dan satu stasiun pemantau.")

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
        <div class="eyebrow">Business Intelligence Dashboard · Kualitas Udara DKI Jakarta</div>
        <h1>Ruang kendali ISPU untuk membaca risiko udara Jakarta.</h1>
        <p>
            Dashboard ini menyatukan data harian Stasiun Pemantau Kualitas Udara untuk menjawab lima pertanyaan inti:
            kondisi umum, tren waktu, perbandingan antar stasiun, pencemar kritis, dan pola musiman. Fokusnya bukan hanya melihat angka,
            tetapi menentukan kapan, di mana, dan polutan apa yang paling perlu ditindaklanjuti.
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
    st.warning("Tidak ada data pada kombinasi filter yang dipilih. Perluas rentang tanggal atau pilih ulang stasiun/kategori/pencemar.")
    st.stop()

# ============================================================
# Global KPIs
# ============================================================
avg_ispu = fdf["max"].mean()
unhealthy_pct = fdf["is_unhealthy_or_worse"].mean()
dominant_pollutant = mode_value(fdf["critical"])
station_avg = fdf.groupby("stasiun")["max"].mean().sort_values(ascending=False)
priority_station = station_avg.index[0] if not station_avg.empty else "-"
obs_count = len(fdf)
period_label = f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"

st.markdown(
    "<div class='metric-grid'>"
    + metric_card("Rata-rata ISPU", fmt_number(avg_ispu), f"Nilai rata-rata kolom max pada {obs_count:,} observasi terfilter.".replace(",", "."))
    + metric_card("Tidak Sehat+", fmt_pct(unhealthy_pct), "Proporsi observasi TIDAK SEHAT, SANGAT TIDAK SEHAT, atau BERBAHAYA.")
    + metric_card("Pencemar dominan", dominant_pollutant, "Parameter yang paling sering menjadi penentu nilai ISPU tertinggi.")
    + metric_card("Stasiun prioritas", priority_station.replace("DKI", "DKI ", 1), "Stasiun dengan rata-rata ISPU tertinggi pada filter aktif.")
    + "</div>",
    unsafe_allow_html=True,
)

st.caption(f"Periode dashboard aktif: {period_label}. Seluruh grafik dan insight mengikuti filter yang dipilih pada panel kiri.")

# ============================================================
# Tabs visualisasi
# ============================================================
tabs = st.tabs([
    "1 · Overview",
    "2 · Tren temporal",
    "3 · Antar stasiun",
    "4 · Pencemar kritis",
    "5 · Pola musiman",
])

# ============================================================
# Visualisasi 1 — Overview
# ============================================================
with tabs[0]:
    section_header(
        "Visualisasi 1",
        "Overview kualitas udara: sebagian risiko terkonsentrasi pada stasiun tertentu.",
        "Bagian ini menunjukkan kondisi umum kualitas udara Jakarta melalui KPI utama, peta/ringkasan kondisi terkini per stasiun, dan komposisi kategori ISPU.",
    )

    latest_per_station = (
        fdf.sort_values("tanggal")
        .groupby("stasiun", as_index=False)
        .tail(1)
        .copy()
    )
    latest_per_station["status_ringkas"] = np.where(
        latest_per_station["is_unhealthy_or_worse"], "Perlu perhatian", "Relatif terkendali"
    )
    latest_per_station["size"] = latest_per_station["max"].clip(lower=12)

    col_map, col_table = st.columns([1.25, 1])
    with col_map:
        fig_map = px.scatter_mapbox(
            latest_per_station,
            lat="lat",
            lon="lon",
            color="categori",
            size="size",
            hover_name="stasiun",
            hover_data={
                "max": ":.1f",
                "critical": True,
                "tanggal": True,
                "lat": False,
                "lon": False,
                "size": False,
            },
            color_discrete_map=CATEGORY_COLORS,
            category_orders={"categori": CATEGORY_ORDER},
            zoom=9.2,
            height=520,
            title="Kondisi terkini per SPKU pada filter aktif",
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            mapbox_center={"lat": -6.22, "lon": 106.84},
            template=PLOT_TEMPLATE,
            margin=dict(l=0, r=0, t=62, b=0),
            legend_title_text="Kategori",
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_table:
        station_summary = (
            fdf.groupby("stasiun", as_index=False)
            .agg(
                rata_rata_ispu=("max", "mean"),
                persen_tidak_sehat=("is_unhealthy_or_worse", "mean"),
                pencemar_dominan=("critical", mode_value),
                observasi=("tanggal", "count"),
            )
            .sort_values("rata_rata_ispu", ascending=False)
        )
        display_station_summary = station_summary.copy()
        display_station_summary["rata_rata_ispu"] = display_station_summary["rata_rata_ispu"].round(1)
        display_station_summary["persen_tidak_sehat"] = (display_station_summary["persen_tidak_sehat"] * 100).round(1)
        display_station_summary = display_station_summary.rename(
            columns={
                "stasiun": "Stasiun",
                "rata_rata_ispu": "Rata-rata ISPU",
                "persen_tidak_sehat": "% Tidak Sehat+",
                "pencemar_dominan": "Pencemar Dominan",
                "observasi": "Observasi",
            }
        )
        st.dataframe(display_station_summary, use_container_width=True, hide_index=True, height=300)

        category_dist = (
            fdf["categori"].value_counts(normalize=True)
            .reindex(CATEGORY_ORDER)
            .dropna()
            .mul(100)
            .reset_index()
        )
        category_dist.columns = ["Kategori", "Persentase"]
        fig_cat = px.bar(
            category_dist,
            x="Kategori",
            y="Persentase",
            color="Kategori",
            color_discrete_map=CATEGORY_COLORS,
            text=category_dist["Persentase"].map(lambda x: f"{x:.1f}%"),
            title="Distribusi kategori ISPU pada data terfilter",
        )
        fig_cat.update_traces(textposition="outside", cliponaxis=False)
        fig_cat.update_layout(showlegend=False, yaxis_title="Persentase observasi", xaxis_title="Kategori")
        st.plotly_chart(polish_figure(fig_cat, height=320), use_container_width=True)

    top_station = station_summary.iloc[0]
    insight_card(
        "Analisis & insight overview",
        f"Rata-rata ISPU pada filter aktif berada di <b>{fmt_number(avg_ispu)}</b>, dengan porsi Tidak Sehat+ sebesar <b>{fmt_pct(unhealthy_pct)}</b>. Stasiun dengan rata-rata tertinggi adalah <b>{top_station['stasiun']}</b> dan pencemar dominan keseluruhan adalah <b>{dominant_pollutant}</b>.",
        f"Prioritaskan pemantauan dan respons operasional pada <b>{top_station['stasiun']}</b>, terutama ketika parameter <b>{dominant_pollutant}</b> kembali menjadi pencemar dominan. Ringkasan ini dapat menjadi dasar briefing harian pimpinan.",
    )

# ============================================================
# Visualisasi 2 — Tren Temporal
# ============================================================
with tabs[1]:
    section_header(
        "Visualisasi 2",
        "Tren temporal: arah risiko terlihat saat data dibaca menurut granularitas waktu.",
        "Gunakan pilihan granularitas pada panel kiri untuk melihat pola harian, bulanan, atau tahunan. Grafik ini membantu membedakan fluktuasi jangka pendek dengan perubahan jangka panjang.",
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
    annual_rank = fdf.groupby("tahun", as_index=False)["max"].mean().sort_values("max")
    best_year = int(annual_rank.iloc[0]["tahun"]) if not annual_rank.empty else None
    worst_year = int(annual_rank.iloc[-1]["tahun"]) if not annual_rank.empty else None

    fig_trend = px.line(
        trend_df,
        x="periode",
        y="rata_rata_ispu",
        color="stasiun",
        markers=(granularity == "Tahunan"),
        title=f"Tren {granularity.lower()} menunjukkan kualitas udara {direction}",
        labels={"periode": "Periode", "rata_rata_ispu": "Rata-rata ISPU", "stasiun": "Stasiun"},
    )
    fig_trend.add_hrect(y0=101, y1=199, line_width=0, fillcolor="rgba(251,146,60,.10)", annotation_text="Zona Tidak Sehat", annotation_position="top left")
    fig_trend.add_hline(y=100, line_dash="dash", line_color="rgba(251, 146, 60, .78)", annotation_text="Batas SEDANG/TIDAK SEHAT")
    fig_trend.update_traces(line_width=2.6)
    st.plotly_chart(polish_figure(fig_trend, height=560), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        yearly = fdf.groupby("tahun", as_index=False).agg(rata_rata_ispu=("max", "mean"), tidak_sehat=("is_unhealthy_or_worse", "mean"))
        fig_year = px.bar(
            yearly,
            x="tahun",
            y="rata_rata_ispu",
            color="rata_rata_ispu",
            color_continuous_scale=["#32D583", "#FACC15", "#FB923C", "#F04438"],
            title=f"Tahun terbaik: {best_year} · tahun terburuk: {worst_year}",
            labels={"tahun": "Tahun", "rata_rata_ispu": "Rata-rata ISPU"},
        )
        fig_year.update_layout(coloraxis_showscale=False)
        st.plotly_chart(polish_figure(fig_year, height=380), use_container_width=True)
    with col_b:
        unhealthy_year = yearly.copy()
        unhealthy_year["persen"] = unhealthy_year["tidak_sehat"] * 100
        fig_unhealthy_year = px.area(
            unhealthy_year,
            x="tahun",
            y="persen",
            title="Proporsi Tidak Sehat+ per tahun",
            labels={"tahun": "Tahun", "persen": "% Tidak Sehat+"},
        )
        fig_unhealthy_year.update_traces(line_color="#F04438", fillcolor="rgba(240,68,56,.18)")
        st.plotly_chart(polish_figure(fig_unhealthy_year, height=380), use_container_width=True)

    insight_card(
        "Analisis & insight tren temporal",
        f"Secara tahunan, pola ISPU pada filter aktif <b>{direction}</b> dengan kemiringan tren sekitar <b>{slope:.2f}</b> poin ISPU per tahun. Tahun dengan rata-rata ISPU terendah adalah <b>{best_year}</b>, sedangkan rata-rata tertinggi terjadi pada <b>{worst_year}</b>.",
        f"Gunakan perbandingan tahun terbaik-terburuk untuk mengevaluasi periode kebijakan dan menetapkan target penurunan ISPU. Saat tren memburuk atau % Tidak Sehat+ meningkat, DLH dapat mengaktifkan pemantauan lebih rapat dan koordinasi lintas sektor pada periode tersebut.",
    )

# ============================================================
# Visualisasi 3 — Perbandingan antar stasiun
# ============================================================
with tabs[2]:
    section_header(
        "Visualisasi 3",
        "Perbandingan antar stasiun: prioritas intervensi tidak merata di seluruh Jakarta.",
        "Perbandingan ini membantu memilih lokasi prioritas berdasarkan rata-rata ISPU dan komposisi kategori risiko di masing-masing SPKU.",
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
            color_continuous_scale=["#32D583", "#FACC15", "#FB923C", "#F04438"],
            text=station_metric["rata_rata_ispu"].map(lambda x: f"{x:.1f}"),
            title=f"{worst_station} memiliki rata-rata ISPU tertinggi",
            labels={"stasiun": "Stasiun", "rata_rata_ispu": "Rata-rata ISPU"},
        )
        fig_station.update_traces(textposition="outside", cliponaxis=False)
        fig_station.update_layout(coloraxis_showscale=False)
        st.plotly_chart(polish_figure(fig_station, height=480), use_container_width=True)

    with col2:
        station_category = (
            fdf.groupby(["stasiun", "categori"], as_index=False)
            .size()
            .rename(columns={"size": "jumlah"})
        )
        station_total = station_category.groupby("stasiun")["jumlah"].transform("sum")
        station_category["persentase"] = station_category["jumlah"] / station_total * 100
        fig_stack = px.bar(
            station_category,
            y="stasiun",
            x="persentase",
            color="categori",
            orientation="h",
            category_orders={"categori": CATEGORY_ORDER},
            color_discrete_map=CATEGORY_COLORS,
            title="Komposisi kategori ISPU per stasiun",
            labels={"stasiun": "Stasiun", "persentase": "Persentase", "categori": "Kategori"},
        )
        fig_stack.update_layout(barmode="stack")
        st.plotly_chart(polish_figure(fig_stack, height=480), use_container_width=True)

    display_metric = station_metric.sort_values("rata_rata_ispu", ascending=False).copy()
    display_metric["rata_rata_ispu"] = display_metric["rata_rata_ispu"].round(1)
    display_metric["median_ispu"] = display_metric["median_ispu"].round(1)
    display_metric["tidak_sehat"] = (display_metric["tidak_sehat"] * 100).round(1)
    display_metric = display_metric.rename(columns={"stasiun": "Stasiun", "rata_rata_ispu": "Rata-rata ISPU", "median_ispu": "Median ISPU", "tidak_sehat": "% Tidak Sehat+", "observasi": "Observasi"})
    st.dataframe(display_metric, use_container_width=True, hide_index=True)

    insight_card(
        "Analisis & insight antar stasiun",
        f"Stasiun dengan rata-rata ISPU tertinggi adalah <b>{worst_station}</b>, sedangkan yang terendah adalah <b>{best_station}</b>. Komposisi kategori menunjukkan apakah risiko di suatu lokasi hanya sesekali meningkat atau konsisten berada pada kategori yang lebih berat.",
        f"DLH dapat menempatkan intervensi pengendalian polusi secara bertahap: mulai dari <b>{worst_station}</b> sebagai lokasi prioritas, lalu membandingkan pola kategorinya dengan <b>{best_station}</b> untuk memahami praktik atau karakteristik lokasi yang lebih terkendali.",
    )

# ============================================================
# Visualisasi 4 — Parameter pencemar kritis
# ============================================================
with tabs[3]:
    section_header(
        "Visualisasi 4",
        "Pencemar kritis: program pengurangan emisi perlu mengikuti parameter dominan.",
        "Analisis ini menunjukkan parameter yang paling sering menjadi penentu nilai ISPU tertinggi dan bagaimana kemunculannya berubah menurut stasiun dan periode.",
    )

    critical_count = fdf["critical"].value_counts().reset_index()
    critical_count.columns = ["critical", "jumlah"]
    critical_count["persentase"] = critical_count["jumlah"] / critical_count["jumlah"].sum() * 100
    top_critical = critical_count.iloc[0]["critical"] if not critical_count.empty else "-"

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
        crit_station = (
            fdf.groupby(["stasiun", "critical"], as_index=False).size().rename(columns={"size": "jumlah"})
        )
        fig_heat = px.density_heatmap(
            crit_station,
            x="critical",
            y="stasiun",
            z="jumlah",
            histfunc="sum",
            color_continuous_scale=["#0B171B", "#14515E", "#67E8F9", "#A3E635", "#FACC15"],
            title="Karakteristik pencemar kritis berbeda antar stasiun",
            labels={"critical": "Pencemar", "stasiun": "Stasiun", "jumlah": "Frekuensi"},
        )
        st.plotly_chart(polish_figure(fig_heat, height=470), use_container_width=True)

    crit_trend = (
        fdf.groupby(["tahun", "critical"], as_index=False)
        .size()
        .rename(columns={"size": "jumlah"})
    )
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
    st.plotly_chart(polish_figure(fig_crit_trend, height=430), use_container_width=True)

    top_crit_pct = critical_count.iloc[0]["persentase"] if not critical_count.empty else np.nan
    station_top_critical = (
        fdf.groupby(["stasiun", "critical"]).size().reset_index(name="jumlah")
        .sort_values(["stasiun", "jumlah"], ascending=[True, False])
        .groupby("stasiun")
        .head(1)
    )
    dominant_pairs = "; ".join([f"{row.stasiun}: {row.critical}" for row in station_top_critical.itertuples(index=False)])

    insight_card(
        "Analisis & insight pencemar kritis",
        f"Parameter <b>{top_critical}</b> menjadi pencemar kritis paling dominan dengan porsi sekitar <b>{top_crit_pct:.1f}%</b> dari observasi terfilter. Namun heatmap memperlihatkan bahwa pencemar dominan tidak selalu sama di setiap stasiun.",
        f"Program pengurangan emisi perlu dibedakan menurut karakteristik lokasi. Ringkasan pencemar dominan per SPKU adalah: <b>{dominant_pairs}</b>. Ini dapat menjadi dasar penentuan fokus inspeksi, kampanye, dan koordinasi sumber emisi.",
    )

# ============================================================
# Visualisasi 5 — Pola musiman
# ============================================================
with tabs[4]:
    section_header(
        "Visualisasi 5",
        "Pola musiman: periode rawan polusi dapat diprediksi dan dipersiapkan.",
        "Pola bulanan membantu mengidentifikasi kapan kualitas udara cenderung memburuk. Ini berguna untuk menyusun kalender kewaspadaan dan operasi pengendalian pencemaran.",
    )

    seasonal = (
        fdf.groupby(["tahun", "bulan", "nama_bulan"], as_index=False)
        .agg(rata_rata_ispu=("max", "mean"), tidak_sehat=("is_unhealthy_or_worse", "mean"), observasi=("max", "count"))
    )
    heat = seasonal.pivot_table(index="tahun", columns="nama_bulan", values="rata_rata_ispu", aggfunc="mean")
    heat = heat.reindex(columns=MONTH_ORDER)

    col1, col2 = st.columns([1.24, 1])
    with col1:
        fig_heatmap = px.imshow(
            heat,
            aspect="auto",
            color_continuous_scale=["#32D583", "#FACC15", "#FB923C", "#F04438", "#7A271A"],
            title="Heatmap rata-rata ISPU per bulan dan tahun",
            labels=dict(x="Bulan", y="Tahun", color="Rata-rata ISPU"),
        )
        fig_heatmap.update_xaxes(side="top")
        st.plotly_chart(polish_figure(fig_heatmap, height=530), use_container_width=True)

    with col2:
        monthly = (
            fdf.groupby(["bulan", "nama_bulan"], as_index=False)
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
            color_continuous_scale=["#32D583", "#FACC15", "#FB923C", "#F04438"],
            title=f"Bulan terburuk: {worst_month['nama_bulan']} · terbaik: {best_month['nama_bulan']}",
            labels={"nama_bulan": "Bulan", "rata_rata_ispu": "Rata-rata ISPU"},
        )
        fig_month.update_layout(coloraxis_showscale=False)
        fig_month.update_xaxes(tickangle=-45)
        st.plotly_chart(polish_figure(fig_month, height=530), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig_month_unhealthy = px.line(
            monthly,
            x="nama_bulan",
            y="persen_tidak_sehat",
            markers=True,
            title="Proporsi Tidak Sehat+ menurut bulan",
            labels={"nama_bulan": "Bulan", "persen_tidak_sehat": "% Tidak Sehat+"},
        )
        fig_month_unhealthy.update_traces(line_color="#F04438", line_width=3, marker_size=9)
        fig_month_unhealthy.update_xaxes(tickangle=-45)
        st.plotly_chart(polish_figure(fig_month_unhealthy, height=360), use_container_width=True)
    with col4:
        st.markdown(
            f"""
            <div class="card">
                <div class="insight-title">Kalender kewaspadaan</div>
                <p><span class="danger-tag">Prioritas</span> <b>{worst_month['nama_bulan']}</b> memiliki rata-rata ISPU tertinggi, yaitu <b>{fmt_number(worst_month['rata_rata_ispu'])}</b>.</p>
                <p style="margin-top:10px"><span class="good-tag">Relatif lebih baik</span> <b>{best_month['nama_bulan']}</b> memiliki rata-rata ISPU terendah, yaitu <b>{fmt_number(best_month['rata_rata_ispu'])}</b>.</p>
                <p style="margin-top:10px"><span class="neutral-tag">Operasional</span> Periode dengan kenaikan bulanan dapat dipakai untuk mengatur jadwal inspeksi, edukasi publik, dan koordinasi pengendalian emisi lebih awal.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    insight_card(
        "Analisis & insight pola musiman",
        f"Pola musiman menunjukkan bahwa <b>{worst_month['nama_bulan']}</b> menjadi bulan dengan rata-rata ISPU tertinggi, sedangkan <b>{best_month['nama_bulan']}</b> menjadi bulan dengan rata-rata terendah pada filter aktif. Heatmap memperlihatkan apakah pola tersebut berulang lintas tahun atau hanya terjadi pada tahun tertentu.",
        f"DLH dapat menetapkan <b>kalender operasi kualitas udara</b>: peningkatan pemantauan, kampanye pengurangan emisi, dan koordinasi lintas sektor dimulai sebelum bulan berisiko tinggi, bukan setelah kondisi buruk muncul di publik.",
    )

# ============================================================
# Data table and export
# ============================================================
st.markdown("---")
section_header(
    "Lampiran dashboard",
    "Data terfilter dan ringkasan penggunaan",
    "Bagian ini membantu saat demonstrasi: pengguna dapat menunjukkan bahwa seluruh visualisasi mengikuti filter yang sama dan data dapat diekspor untuk analisis lanjutan.",
)

with st.expander("Lihat data terfilter"):
    st.dataframe(
        fdf[["tanggal", "stasiun", "pm10", "pm25", "so2", "co", "o3", "no2", "max", "critical", "categori", "quality_notes"]].sort_values(["tanggal", "stasiun"]),
        use_container_width=True,
        hide_index=True,
        height=420,
    )
    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button("Unduh data terfilter (.csv)", csv, "ispu_jakarta_data_terfilter.csv", "text/csv")

st.markdown(
    """
    <div class="card">
        <p><b>Catatan interpretasi:</b> Dashboard ini bersifat deskriptif dan diagnostik. Hasilnya dapat menunjukkan lokasi, waktu, dan parameter yang perlu diprioritaskan, tetapi analisis penyebab memerlukan data tambahan seperti meteorologi, lalu lintas, aktivitas industri, dan sumber emisi lain.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
