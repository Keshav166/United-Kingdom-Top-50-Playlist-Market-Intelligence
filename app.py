"""
==========================================================================================
 ATLANTIC RECORDING CORPORATION
 United Kingdom Top 50 Playlist — Market Structure, Artist Diversity & Content
 Localization Analysis
 Executive Business Intelligence Dashboard
==========================================================================================
Author : Data Science / BI Engineering
Stack  : Streamlit + Plotly + NetworkX + Pandas
Notes  : Modular, cached, production-style layout. All BI metrics are computed
         directly from the filtered dataset (nothing hardcoded).
==========================================================================================
"""

import io
from collections import Counter
from itertools import combinations

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================================================
# 1. PAGE CONFIGURATION
# ==========================================================================================
st.set_page_config(
    page_title="Atlantic UK Market Intelligence",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "Atlantic_United_Kingdom.csv"

BRAND_PRIMARY = "#6C5CE7"
BRAND_SECONDARY = "#00D2A0"
BRAND_DARK = "#12141D"
BRAND_ACCENT = "#FF6B6B"
PALETTE = ["#6C5CE7", "#00D2A0", "#FF6B6B", "#FFC048", "#48A9FF", "#FF7EDB", "#7BED9F", "#A29BFE"]


# ==========================================================================================
# 2. CUSTOM CSS — PREMIUM ENTERPRISE LOOK
# ==========================================================================================
def inject_css() -> None:
    """Injects custom CSS to override Streamlit's default look with a premium BI theme."""
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Inter', sans-serif;
            }}

            .main,
            .stApp,
            [data-testid="stAppViewContainer"],
            [data-testid="stMain"] {{
                background: radial-gradient(circle at top left, #161824 0%, #0d0e15 100%) !important;
                color: #eef0fa !important;
            }}

            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #14151f 0%, #0d0e15 100%) !important;
                border-right: 1px solid rgba(255,255,255,0.06);
            }}
            [data-testid="stSidebar"] * {{
                color: #eef0fa;
            }}
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea {{
                background-color: #1b1e2b !important;
                color: #eef0fa !important;
            }}

            /* ---------- Top header/toolbar strip ---------- */
            [data-testid="stHeader"] {{
                background: #0d0e15 !important;
            }}
            [data-testid="stToolbar"],
            [data-testid="stDecoration"],
            [data-testid="stStatusWidget"] {{
                background: transparent !important;
            }}
            [data-testid="stHeader"] * {{
                color: #eef0fa !important;
            }}

            /* ---------- Multiselect / select widgets (Album Type, etc.) ---------- */
            [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
            [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
                background-color: #1b1e2b !important;
                border-color: rgba(255,255,255,0.12) !important;
            }}
            [data-baseweb="popover"] ul,
            [data-baseweb="menu"] {{
                background-color: #1b1e2b !important;
            }}
            [data-baseweb="popover"] li,
            [data-baseweb="menu"] li {{
                color: #eef0fa !important;
            }}
            [data-baseweb="tag"] {{
                background-color: {BRAND_ACCENT} !important;
            }}

            /* ---------- Hero header ---------- */
            .hero-header {{
                background: linear-gradient(120deg, {BRAND_PRIMARY} 0%, #4834d4 45%, {BRAND_SECONDARY} 100%);
                padding: 34px 40px;
                border-radius: 20px;
                box-shadow: 0 12px 35px rgba(108, 92, 231, 0.35);
                margin-bottom: 22px;
            }}
            .hero-title {{
                color: white;
                font-size: 30px;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.5px;
            }}
            .hero-subtitle {{
                color: rgba(255,255,255,0.88);
                font-size: 14.5px;
                margin-top: 6px;
                font-weight: 500;
            }}
            .hero-tag {{
                display: inline-block;
                background: rgba(255,255,255,0.18);
                color: white;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 12px;
                backdrop-filter: blur(6px);
            }}

            /* ---------- KPI Cards ---------- */
            .kpi-card {{
                background: linear-gradient(160deg, #1b1e2b 0%, #14151f 100%);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 18px 20px 16px 20px;
                box-shadow: 0 8px 22px rgba(0,0,0,0.35);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                min-height: 152px;
                margin-bottom: 18px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}
            .kpi-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 14px 30px rgba(108, 92, 231, 0.25);
            }}
            .kpi-icon {{ font-size: 20px; opacity: 0.9; line-height: 1; }}
            .kpi-label {{
                color: #9aa0b4;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.4px;
                margin-top: 8px;
                line-height: 1.35;
                min-height: 32px;
            }}
            .kpi-value {{
                color: #ffffff;
                font-size: 24px;
                font-weight: 800;
                margin-top: 4px;
                line-height: 1.2;
            }}
            .kpi-delta-up {{ color: {BRAND_SECONDARY}; font-size: 12px; font-weight: 700; margin-top: 8px; }}
            .kpi-delta-down {{ color: {BRAND_ACCENT}; font-size: 12px; font-weight: 700; margin-top: 8px; }}
            .kpi-delta-flat {{ color: #9aa0b4; font-size: 12px; font-weight: 700; margin-top: 8px; }}

            /* ---------- Section headers ---------- */
            .section-header {{
                color: #ffffff;
                font-size: 21px;
                font-weight: 800;
                margin-top: 6px;
                margin-bottom: 2px;
                border-left: 5px solid {BRAND_PRIMARY};
                padding-left: 12px;
            }}
            .section-sub {{
                color: #9aa0b4;
                font-size: 13px;
                margin-left: 17px;
                margin-bottom: 14px;
            }}

            /* ---------- Insight / recommendation cards ---------- */
            .insight-card {{
                background: linear-gradient(135deg, rgba(108,92,231,0.14), rgba(0,210,160,0.07));
                border: 1px solid rgba(108,92,231,0.28);
                border-radius: 14px;
                padding: 14px 18px;
                margin-bottom: 10px;
                color: #e4e6f0;
                font-size: 14px;
            }}
            .rec-card {{
                background: #171926;
                border-left: 4px solid {BRAND_SECONDARY};
                border-radius: 10px;
                padding: 16px 18px;
                margin-bottom: 12px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.3);
            }}
            .rec-title {{ color: {BRAND_SECONDARY}; font-weight: 800; font-size: 14.5px; margin-bottom: 4px;}}
            .rec-body {{ color: #cfd2e2; font-size: 13.5px; line-height: 1.5;}}

            .metric-pill {{
                display:inline-block; background: rgba(108,92,231,0.18); color:#c7c1ff;
                padding: 3px 12px; border-radius: 20px; font-size: 11.5px; font-weight: 700;
                margin-right: 6px;
            }}

            .footer-box {{
                text-align:center; color:#6b7086; font-size:12.5px; padding: 22px 0 10px 0;
                border-top: 1px solid rgba(255,255,255,0.07); margin-top: 30px;
            }}

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
            .stTabs [data-baseweb="tab"] {{
                background-color: #171926; border-radius: 10px 10px 0 0; padding: 8px 16px;
                color: #9aa0b4; font-weight: 600;
            }}
            .stTabs [aria-selected="true"] {{
                background-color: {BRAND_PRIMARY} !important; color: white !important;
            }}

            /* ---------- Executive Decision Center ---------- */
            .decision-card {{
                background: linear-gradient(160deg, #1b1e2b 0%, #14151f 100%);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 18px;
                margin-bottom: 20px;
                overflow: hidden;
                box-shadow: 0 10px 26px rgba(0,0,0,0.35);
            }}
            .decision-header {{
                padding: 14px 20px;
                font-weight: 800;
                font-size: 15px;
                color: white;
            }}
            .decision-body {{ padding: 14px 20px 20px 20px; }}
            .decision-label {{
                color: #9aa0b4; font-size: 11px; font-weight: 700; text-transform: uppercase;
                letter-spacing: 0.5px; margin-top: 10px; margin-bottom: 3px;
            }}
            .decision-value {{ color: #ffffff; font-size: 15.5px; font-weight: 700; line-height: 1.4; }}
            .decision-reason {{ color: #cfd2e2; font-size: 13.5px; line-height: 1.55; }}
            .decision-impact {{ color: #cfd2e2; font-size: 13.5px; line-height: 1.5; }}

            .badge {{
                display: inline-block; padding: 3px 12px; border-radius: 20px;
                font-size: 11px; font-weight: 800; letter-spacing: 0.3px;
            }}
            .badge-green {{ background: rgba(0,210,160,0.18); color: {BRAND_SECONDARY}; }}
            .badge-yellow {{ background: rgba(255,192,72,0.18); color: #FFC048; }}
            .badge-red {{ background: rgba(255,107,107,0.18); color: {BRAND_ACCENT}; }}
            .badge-purple {{ background: rgba(108,92,231,0.2); color: #b6a8ff; }}

            .conf-track {{
                width: 100%; height: 8px; border-radius: 6px; background: rgba(255,255,255,0.08);
                margin-top: 6px; overflow: hidden;
            }}
            .conf-fill {{ height: 100%; border-radius: 6px; }}

            .alert-card {{
                border-radius: 14px; padding: 14px 18px; margin-bottom: 12px;
                font-size: 13.5px; line-height: 1.5; border-left: 5px solid;
            }}
            .alert-green {{ background: rgba(0,210,160,0.08); border-color: {BRAND_SECONDARY}; color: #d7fff2; }}
            .alert-yellow {{ background: rgba(255,192,72,0.08); border-color: #FFC048; color: #fff3d9; }}
            .alert-red {{ background: rgba(255,107,107,0.08); border-color: {BRAND_ACCENT}; color: #ffe1e1; }}
            .alert-title {{ font-weight: 800; font-size: 14px; margin-bottom: 4px; }}

            .exec-summary-box {{
                background: linear-gradient(135deg, rgba(108,92,231,0.16), rgba(0,210,160,0.08));
                border: 1px solid rgba(108,92,231,0.3); border-radius: 16px;
                padding: 22px 26px; font-size: 14.5px; line-height: 1.7; color: #eef0fa;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(col, icon: str, label: str, value: str, delta: float = None, delta_suffix: str = "pp") -> None:
    """Renders a single premium KPI card with an optional trend indicator."""
    if delta is None:
        delta_html = '<div class="kpi-delta-flat">— no comparison period</div>'
    elif delta > 0.001:
        delta_html = f'<div class="kpi-delta-up">▲ {delta:+.1f}{delta_suffix} vs. full dataset</div>'
    elif delta < -0.001:
        delta_html = f'<div class="kpi-delta-down">▼ {delta:+.1f}{delta_suffix} vs. full dataset</div>'
    else:
        delta_html = '<div class="kpi-delta-flat">▬ flat vs. full dataset</div>'

    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def sub_section(title: str) -> None:
    st.markdown(f'<div class="section-header" style="font-size:17px;">{title}</div>', unsafe_allow_html=True)


def badge(text: str, level: str) -> str:
    """Small colored status pill used inside decision cards (green/yellow/red/purple)."""
    return f'<span class="badge badge-{level}">{text}</span>'


def confidence_bar(score: float) -> str:
    """Renders a horizontal confidence progress bar, colored by score band."""
    score = max(0.0, min(100.0, score))
    color = BRAND_SECONDARY if score >= 75 else "#FFC048" if score >= 55 else BRAND_ACCENT
    return (f'<div class="conf-track"><div class="conf-fill" '
            f'style="width:{score}%; background:{color};"></div></div>')


def decision_card(col, icon: str, title: str, decision: str, reason: str, confidence: float,
                   impact: str) -> None:
    """Renders a single premium executive decision card: decision, reason, impact, confidence bar."""
    col.markdown(
        f"""
        <div class="decision-card">
            <div class="decision-header" style="background: linear-gradient(120deg, {BRAND_PRIMARY}, #4834d4);">
                {icon} {title}
            </div>
            <div class="decision-body">
                <div class="decision-label">Decision</div>
                <div class="decision-value">{decision}</div>
                <div class="decision-label">Reason</div>
                <div class="decision-reason">{reason}</div>
                <div class="decision-label">Expected Business Impact</div>
                <div class="decision-impact">{impact}</div>
                <div class="decision-label">Confidence Score — {confidence:.0f}%</div>
                {confidence_bar(confidence)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(level: str, icon: str, title: str, body: str) -> None:
    """Renders a colored decision alert (🟢 opportunity / 🟡 warning / 🔴 risk)."""
    st.markdown(
        f'<div class="alert-card alert-{level}"><div class="alert-title">{icon} {title}</div>{body}</div>',
        unsafe_allow_html=True,
    )


# ==========================================================================================
# 3. DATA LOADING & FEATURE ENGINEERING
# ==========================================================================================
@st.cache_data(show_spinner=False)
def load_raw_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Builds every derived column used across the dashboard, once, with caching."""
    df = df.copy()

    # Robust date parsing (source format is DD-MM-YYYY)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["date"])

    df["duration_min"] = df["duration_ms"] / 60000
    df["artist_list"] = df["artist"].str.split("&").apply(lambda lst: [a.strip() for a in lst])
    df["artist_count"] = df["artist_list"].apply(len)
    df["Collaboration"] = np.where(df["artist_count"] == 1, "Solo", "Collaboration")
    df["primary_artist"] = df["artist_list"].apply(lambda lst: lst[0])

    df["Rank_Group"] = pd.cut(
        df["position"], bins=[0, 10, 25, 50], labels=["Top 10", "11-25", "26-50"]
    )

    df["Duration_Bucket"] = pd.cut(
        df["duration_min"],
        bins=[0, 2.5, 3.5, 4.5, 100],
        labels=["Short (<2.5m)", "Medium (2.5-3.5m)", "Long (3.5-4.5m)", "Extended (>4.5m)"],
    )

    df["Explicit_Label"] = df["is_explicit"].map({True: "Explicit", False: "Clean"})
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["weekday"] = df["date"].dt.day_name()
    df["week"] = df["date"].dt.isocalendar().week

    return df


# ==========================================================================================
# 4. SIDEBAR — FILTERS
# ==========================================================================================
def build_sidebar(df: pd.DataFrame) -> dict:
    st.sidebar.markdown(
        f"""
        <div style="text-align:center; padding: 6px 0 16px 0;">
            <div style="font-size:34px;">🎧</div>
            <div style="color:white; font-weight:800; font-size:16px;">ATLANTIC RECORDING</div>
            <div style="color:{BRAND_SECONDARY}; font-size:11.5px; font-weight:700; letter-spacing:1px;">
                UK MARKET INTELLIGENCE
            </div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.08);">
        """,
        unsafe_allow_html=True,
    )

    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    min_pop, max_pop = int(df["popularity"].min()), int(df["popularity"].max())
    min_dur, max_dur = float(df["duration_min"].min()), float(df["duration_min"].max())

    defaults = {
        "date_range": (min_date, max_date),
        "artist_search": "",
        "album_types": sorted(df["album_type"].unique().tolist()),
        "explicit_choice": ["Explicit", "Clean"],
        "collab_choice": ["Solo", "Collaboration"],
        "pop_range": (min_pop, max_pop),
        "dur_range": (round(min_dur, 1), round(max_dur, 1)),
    }

    if "filters_initialized" not in st.session_state:
        for k, v in defaults.items():
            st.session_state[k] = v
        st.session_state["filters_initialized"] = True

    def reset_filters():
        for k, v in defaults.items():
            st.session_state[k] = v

    st.sidebar.markdown("**📅 Date Range**")
    date_range = st.sidebar.date_input(
        "Select period", value=st.session_state["date_range"],
        min_value=min_date, max_value=max_date, key="date_range", label_visibility="collapsed"
    )

    st.sidebar.markdown("**🔎 Artist Search**")
    artist_search = st.sidebar.text_input(
        "Search artist", value=st.session_state["artist_search"],
        key="artist_search", placeholder="e.g. Dua Lipa", label_visibility="collapsed"
    )

    st.sidebar.markdown("**💿 Album Type**")
    album_types = st.sidebar.multiselect(
        "Album type", options=sorted(df["album_type"].unique().tolist()),
        default=st.session_state["album_types"], key="album_types", label_visibility="collapsed"
    )

    st.sidebar.markdown("**🚫 Explicit Content**")
    explicit_choice = st.sidebar.multiselect(
        "Explicit", options=["Explicit", "Clean"],
        default=st.session_state["explicit_choice"], key="explicit_choice", label_visibility="collapsed"
    )

    st.sidebar.markdown("**🤝 Collaboration Type**")
    collab_choice = st.sidebar.multiselect(
        "Collaboration", options=["Solo", "Collaboration"],
        default=st.session_state["collab_choice"], key="collab_choice", label_visibility="collapsed"
    )

    st.sidebar.markdown("**⭐ Popularity Range**")
    pop_range = st.sidebar.slider(
        "Popularity", min_value=min_pop, max_value=max_pop,
        value=st.session_state["pop_range"], key="pop_range", label_visibility="collapsed"
    )

    st.sidebar.markdown("**⏱️ Duration Range (minutes)**")
    dur_range = st.sidebar.slider(
        "Duration", min_value=round(min_dur, 1), max_value=round(max_dur, 1),
        value=st.session_state["dur_range"], step=0.1, key="dur_range", label_visibility="collapsed"
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.button("↺ Reset All Filters", on_click=reset_filters, use_container_width=True)

    st.sidebar.markdown(
        f"""
        <hr style="border-color: rgba(255,255,255,0.08);">
        <div style="color:#6b7086; font-size:11px; text-align:center;">
        Dataset span: {min_date.strftime('%d/%m/%Y')} – {max_date.strftime('%d/%m/%Y')}<br>
        {len(df):,} chart entries loaded
        </div>
        """,
        unsafe_allow_html=True,
    )

    return dict(
        date_range=date_range, artist_search=artist_search, album_types=album_types,
        explicit_choice=explicit_choice, collab_choice=collab_choice,
        pop_range=pop_range, dur_range=dur_range,
    )


def apply_filters(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    out = df.copy()

    if isinstance(f["date_range"], tuple) and len(f["date_range"]) == 2:
        start, end = f["date_range"]
        out = out[(out["date"].dt.date >= start) & (out["date"].dt.date <= end)]

    if f["artist_search"]:
        out = out[out["artist"].str.contains(f["artist_search"], case=False, na=False)]

    if f["album_types"]:
        out = out[out["album_type"].isin(f["album_types"])]

    if f["explicit_choice"]:
        out = out[out["Explicit_Label"].isin(f["explicit_choice"])]

    if f["collab_choice"]:
        out = out[out["Collaboration"].isin(f["collab_choice"])]

    out = out[(out["popularity"] >= f["pop_range"][0]) & (out["popularity"] <= f["pop_range"][1])]
    out = out[(out["duration_min"] >= f["dur_range"][0]) & (out["duration_min"] <= f["dur_range"][1])]

    return out


# ==========================================================================================
# 5. BUSINESS INTELLIGENCE METRIC ENGINE  (20 decision-making metrics)
# ==========================================================================================
@st.cache_data(show_spinner=False)
def compute_bi_metrics(df: pd.DataFrame) -> dict:
    m = {}
    n = len(df)
    if n == 0:
        return {"empty": True}

    exploded = df.explode("artist_list")
    artist_counts = exploded["artist_list"].value_counts()
    total_appearances = artist_counts.sum()

    # 1-3: Concentration metrics
    m["artist_market_share"] = (artist_counts / total_appearances * 100).round(2)
    m["top5_concentration"] = round(artist_counts.head(5).sum() / total_appearances * 100, 2)
    m["top10_concentration"] = round(artist_counts.head(10).sum() / total_appearances * 100, 2)

    # 4: Market Diversity Index (normalized Shannon entropy, 0-100)
    p = artist_counts / total_appearances
    entropy = -(p * np.log(p)).sum()
    max_entropy = np.log(len(artist_counts)) if len(artist_counts) > 1 else 1
    m["diversity_index"] = round((entropy / max_entropy) * 100, 2) if max_entropy > 0 else 0.0

    # Dynamic "hit" threshold = 75th percentile of popularity in current view
    hit_threshold = df["popularity"].quantile(0.75)
    m["hit_threshold"] = round(hit_threshold, 1)

    # 5-7: Success rates
    collab_df = df[df["Collaboration"] == "Collaboration"]
    solo_df = df[df["Collaboration"] == "Solo"]
    m["collab_success_rate"] = round((collab_df["popularity"] >= hit_threshold).mean() * 100, 2) if len(collab_df) else 0.0
    m["solo_success_rate"] = round((solo_df["popularity"] >= hit_threshold).mean() * 100, 2) if len(solo_df) else 0.0

    explicit_df = df[df["Explicit_Label"] == "Explicit"]
    clean_df = df[df["Explicit_Label"] == "Clean"]
    m["explicit_success_rate"] = round((explicit_df["popularity"] >= hit_threshold).mean() * 100, 2) if len(explicit_df) else 0.0
    m["clean_success_rate"] = round((clean_df["popularity"] >= hit_threshold).mean() * 100, 2) if len(clean_df) else 0.0

    # 8-9: Album vs Single success scores (avg popularity)
    album_df = df[df["album_type"] == "album"]
    single_df = df[df["album_type"] == "single"]
    m["album_success_score"] = round(album_df["popularity"].mean(), 2) if len(album_df) else 0.0
    m["single_success_score"] = round(single_df["popularity"].mean(), 2) if len(single_df) else 0.0

    # 10: Avg popularity by album type
    m["pop_by_album_type"] = df.groupby("album_type")["popularity"].mean().round(2)

    # 11: Avg popularity by duration bucket
    m["pop_by_duration_bucket"] = df.groupby("Duration_Bucket", observed=True)["popularity"].mean().round(2)

    # 12: Hit probability by duration bucket
    m["hit_prob_by_duration"] = (
        df.groupby("Duration_Bucket", observed=True)["popularity"]
        .apply(lambda s: (s >= hit_threshold).mean() * 100)
        .round(2)
    )

    # 13: Rank distribution
    m["rank_distribution"] = df["Rank_Group"].value_counts(normalize=True).mul(100).round(2)

    # 14: Artist repeat frequency
    unique_artists = artist_counts.shape[0]
    m["unique_artists"] = unique_artists
    m["artist_repeat_frequency"] = round(total_appearances / unique_artists, 2) if unique_artists else 0.0

    # 15: Market saturation index
    m["market_saturation_index"] = round((1 - unique_artists / n) * 100, 2)

    # 16: Playlist balance index (diversity + solo/collab balance, averaged)
    collab_ratio = (df["Collaboration"] == "Collaboration").mean() * 100
    m["collaboration_ratio"] = round(collab_ratio, 2)
    collab_balance = 100 - abs(collab_ratio - 50) * 2
    m["playlist_balance_index"] = round((m["diversity_index"] + collab_balance) / 2, 2)

    # 17: Release strategy score (positive => favor albums, negative => favor singles)
    m["release_strategy_gap"] = round(m["album_success_score"] - m["single_success_score"], 2)

    # 18: Artist opportunity score — artists below median appearances but popularity above 75th pct
    artist_pop = exploded.groupby("artist_list")["popularity"].mean()
    median_appearances = artist_counts.median()
    opportunity_mask = (artist_counts < median_appearances) & (artist_pop.reindex(artist_counts.index) >= hit_threshold)
    opportunity_artists = artist_counts[opportunity_mask].index.tolist()
    m["opportunity_artists"] = opportunity_artists[:15]
    m["artist_opportunity_score"] = round(len(opportunity_artists) / unique_artists * 100, 2) if unique_artists else 0.0

    # 19: UK listener preference score — best-performing content combination
    combo = df.groupby(["album_type", "Collaboration", "Explicit_Label"])["popularity"].mean().sort_values(ascending=False)
    m["top_combo"] = combo.index[0] if len(combo) else ("-", "-", "-")
    m["top_combo_score"] = round(combo.iloc[0], 2) if len(combo) else 0.0

    # 20: Market competition score (inverse of top10 concentration)
    m["market_competition_score"] = round(100 - m["top10_concentration"], 2)

    # Supporting aggregates for charts
    m["artist_counts"] = artist_counts
    m["avg_popularity"] = round(df["popularity"].mean(), 2)
    m["avg_duration"] = round(df["duration_min"].mean(), 2)
    m["explicit_share"] = round((df["Explicit_Label"] == "Explicit").mean() * 100, 2)

    return m


@st.cache_data(show_spinner=False)
def compute_deltas(filtered_metrics: dict, full_metrics: dict) -> dict:
    """Computes percentage-point deltas of filtered view vs. the full dataset for KPI trend arrows."""
    keys = [
        "avg_popularity", "unique_artists", "top10_concentration", "collaboration_ratio",
        "explicit_share", "diversity_index", "avg_duration",
    ]
    deltas = {}
    for k in keys:
        try:
            deltas[k] = filtered_metrics[k] - full_metrics[k]
        except Exception:
            deltas[k] = None
    return deltas


# ==========================================================================================
# 5B. EXECUTIVE DECISION ENGINE  (converts BI metrics into CEO-facing decisions)
# ==========================================================================================
@st.cache_data(show_spinner=False)
def compute_executive_decisions(df: pd.DataFrame, m: dict) -> dict:
    """
    Translates the BI metric engine's output into business decisions using threshold-based
    logic. Every decision, confidence score, and impact statement below is derived live from
    the filtered dataset — nothing is a hardcoded recommendation independent of the metrics.
    """
    d = {}

    # ---------------- 1. ARTIST SIGNING STRATEGY ----------------
    conc10 = m["top10_concentration"]
    div = m["diversity_index"]
    uniq = m["unique_artists"]
    sat = m["market_saturation_index"]

    if conc10 >= 50:
        signing_decision = "Focus on Superstar Artists"
        signing_reason = (f"The top 10 artists already control {conc10:.1f}% of all chart appearances. "
                           f"With diversity at {div:.1f}/100, the market currently rewards concentrated star "
                           f"power — doubling down on proven headline acts is the lower-risk path.")
        signing_impact = "High near-term ROI from proven demand, but increases long-term dependency on a small roster."
        signing_conf = 58 + (conc10 - 50) * 0.9
    elif conc10 <= 30 and div >= 55:
        signing_decision = "Sign More Emerging Artists"
        signing_reason = (f"Concentration is low ({conc10:.1f}%) and diversity is high ({div:.1f}/100) across "
                           f"{uniq} unique charting artists — the market has room and rewards new voices.")
        signing_impact = "Lower cost-per-signing with strong upside if even a few emerging acts break out."
        signing_conf = 58 + (55 - conc10) * 0.5 + (div - 55) * 0.3
    else:
        signing_decision = "Balanced Strategy — Mix Emerging & Established"
        signing_reason = (f"Concentration ({conc10:.1f}%) and diversity ({div:.1f}/100) sit in a moderate band, "
                           f"so neither a pure superstar bet nor a pure emerging-artist bet is clearly favored.")
        signing_impact = "Balanced risk/return; guards against both over-reliance and roster dilution."
        signing_conf = 60 + (10 - abs(conc10 - 40)) * 0.5

    d["artist_signing"] = dict(
        decision=signing_decision, reason=signing_reason, impact=signing_impact,
        confidence=round(max(50.0, min(98.0, signing_conf)), 1),
        is_saturated=sat > 65, saturation=sat,
    )

    # ---------------- 2. RELEASE STRATEGY ----------------
    type_counts = df["album_type"].value_counts(normalize=True) * 100
    album_share = float(type_counts.get("album", 0.0))
    single_share = float(type_counts.get("single", 0.0))
    compilation_share = float(type_counts.get("compilation", 0.0))
    gap = m["release_strategy_gap"]

    if gap > 1.5:
        release_decision = "Prioritize Album Releases"
        release_reason = (f"Albums outperform singles by {gap:.1f} popularity points on average "
                           f"({m['album_success_score']:.1f} vs {m['single_success_score']:.1f}), and albums "
                           f"already represent {album_share:.1f}% of chart entries.")
        release_impact = "Higher per-release popularity, deeper catalog value, stronger streaming stickiness."
        release_conf = 60 + gap * 3
    elif gap < -1.5:
        release_decision = "Prioritize Single Releases"
        release_reason = (f"Singles outperform albums by {abs(gap):.1f} popularity points on average "
                           f"({m['single_success_score']:.1f} vs {m['album_success_score']:.1f}); singles make up "
                           f"{single_share:.1f}% of the current chart.")
        release_impact = "Faster time-to-market, lower production risk, better playlist-placement velocity."
        release_conf = 60 + abs(gap) * 3
    else:
        release_decision = "Balanced Album/Single Cadence"
        release_reason = (f"Album and single popularity are within {abs(gap):.1f} points of each other — "
                           f"format choice can follow artist strategy rather than market pressure.")
        release_impact = "Flexibility to sequence singles ahead of an album without a popularity trade-off."
        release_conf = 62.0

    ep_signal = compilation_share < 5 and album_share > 40
    d["release_strategy"] = dict(
        decision=release_decision, reason=release_reason, impact=release_impact,
        confidence=round(max(50.0, min(97.0, release_conf)), 1),
        album_share=round(album_share, 1), single_share=round(single_share, 1),
        compilation_share=round(compilation_share, 1), suggest_eps=ep_signal,
    )

    # ---------------- 3. COLLABORATION STRATEGY ----------------
    collab_gap = m["collab_success_rate"] - m["solo_success_rate"]
    collab_ratio = m["collaboration_ratio"]

    if collab_gap > 5:
        collab_decision = "Increase Collaborations"
        collab_reason = (f"Collaboration hit-rate is {m['collab_success_rate']:.1f}% vs {m['solo_success_rate']:.1f}% "
                          f"for solo tracks — a {collab_gap:.1f}-point edge — while collaborations are currently "
                          f"only {collab_ratio:.1f}% of releases.")
        collab_impact = "Higher hit probability per release and cross-audience exposure via featured artists."
        collab_conf = 58 + collab_gap * 2
    elif collab_gap < -5:
        collab_decision = "Reduce Collaborations"
        collab_reason = (f"Solo tracks hit-rate is {m['solo_success_rate']:.1f}% vs {m['collab_success_rate']:.1f}% "
                          f"for collaborations — protecting solo brand identity currently converts better.")
        collab_impact = "Stronger individual artist brand equity; reduces royalty and rights complexity."
        collab_conf = 58 + abs(collab_gap) * 2
    else:
        collab_decision = "Maintain Current Collaboration Mix"
        collab_reason = (f"Collaboration ({m['collab_success_rate']:.1f}%) and solo ({m['solo_success_rate']:.1f}%) "
                          f"hit-rates are within {abs(collab_gap):.1f} points — the current {collab_ratio:.1f}% "
                          f"collaboration mix is already well calibrated.")
        collab_impact = "Stable performance; no strategic shift required at this time."
        collab_conf = 64.0

    d["collaboration_strategy"] = dict(
        decision=collab_decision, reason=collab_reason, impact=collab_impact,
        confidence=round(max(50.0, min(96.0, collab_conf)), 1), collab_ratio=collab_ratio,
    )

    # ---------------- 4. CONTENT STRATEGY ----------------
    exp_gap = m["explicit_success_rate"] - m["clean_success_rate"]
    exp_share = m["explicit_share"]

    if exp_gap > 5:
        content_decision = "Increase Explicit Releases (Streaming-Led)"
        content_reason = (f"Explicit content hit-rate is {m['explicit_success_rate']:.1f}% vs "
                           f"{m['clean_success_rate']:.1f}% for clean versions — a {exp_gap:.1f}-point edge — "
                           f"with explicit content currently at {exp_share:.1f}% of the catalog.")
    elif exp_gap < -5:
        content_decision = "Favor Clean Versions"
        content_reason = (f"Clean content hit-rate is {m['clean_success_rate']:.1f}% vs "
                           f"{m['explicit_success_rate']:.1f}% for explicit versions — clean edits should lead "
                           f"playlist pitching.")
    else:
        content_decision = "Maintain Balanced Explicit/Clean Mix"
        content_reason = (f"Explicit ({m['explicit_success_rate']:.1f}%) and clean ({m['clean_success_rate']:.1f}%) "
                           f"hit-rates are within {abs(exp_gap):.1f} points of each other.")

    d["content_strategy"] = dict(
        decision=content_decision, reason=content_reason,
        confidence=round(max(50.0, min(95.0, 60 + abs(exp_gap) * 2)), 1),
        impact=(f"Streaming: lead with {'explicit' if exp_gap > 0 else 'clean'} versions to maximize engagement. "
                f"Radio: lead with clean edits regardless of streaming performance, per broadcast norms. "
                f"Family audience: clean-only, cross-promoted via family/kids playlists."),
        explicit_share=exp_share,
    )

    # ---------------- 5. MARKETING STRATEGY ----------------
    top5 = m["top5_concentration"]
    if top5 > 25:
        budget_split = f"{min(75, 50 + top5 * 0.5):.0f}% top artists / {max(25, 50 - top5 * 0.5):.0f}% emerging roster"
        campaign_type = "Conversion-focused campaigns built around proven top-5 artists"
    else:
        budget_split = "55% broad-roster awareness / 45% targeted emerging-artist pushes"
        campaign_type = "Awareness-focused campaigns to build reach across a diversified roster"

    priority_artists = m["artist_counts"].head(5).index.tolist()
    d["marketing_strategy"] = dict(
        budget_split=budget_split, campaign_type=campaign_type, priority_artists=priority_artists,
        audience_targeting=("Streaming-first, playlist-pitch-led targeting" if exp_gap >= 0
                             else "Cross-channel targeting balancing streaming and radio-safe content"),
        confidence=round(max(50.0, min(92.0, 55 + top5 * 1.2)), 1),
    )

    # ---------------- 6. UK MARKET HEALTH SCORE ----------------
    openness = 100 - conc10
    health_score = round(
        div * 0.30 + openness * 0.25 + m["playlist_balance_index"] * 0.25 + m["market_competition_score"] * 0.20, 1
    )
    if health_score >= 80:
        health_band, health_level = "Excellent", "green"
    elif health_score >= 60:
        health_band, health_level = "Good", "green"
    elif health_score >= 40:
        health_band, health_level = "Moderate", "yellow"
    else:
        health_band, health_level = "Weak", "red"
    d["market_health"] = dict(score=health_score, band=health_band, level=health_level)

    # ---------------- 7. ARTIST OPPORTUNITY SCORE ----------------
    opp_composite = div * 0.35 + openness * 0.35 + m["market_competition_score"] * 0.30
    opp_blended = round((opp_composite + m["artist_opportunity_score"]) / 2, 1)
    if opp_blended >= 70:
        opp_band = "Highly Accessible"
    elif opp_blended >= 45:
        opp_band = "Moderately Accessible"
    else:
        opp_band = "Difficult to Enter"
    d["artist_opportunity"] = dict(score=opp_blended, band=opp_band,
                                    contributing_artists=m["opportunity_artists"][:8])

    # ---------------- 8. MARKET COMPETITION GAUGE ----------------
    d["market_competition"] = dict(score=m["market_competition_score"])

    # ---------------- 9. PLAYLIST BALANCE SCORE ----------------
    type_p = df["album_type"].value_counts(normalize=True)
    type_entropy = -(type_p * np.log(type_p)).sum()
    type_max_entropy = np.log(len(type_p)) if len(type_p) > 1 else 1
    type_variety = round((type_entropy / type_max_entropy) * 100, 1) if type_max_entropy > 0 else 0.0

    explicit_balance = 100 - abs(exp_share - 50) * 2

    dur_p = df["Duration_Bucket"].value_counts(normalize=True, dropna=True)
    dur_p = dur_p[dur_p > 0]
    dur_entropy = -(dur_p * np.log(dur_p)).sum()
    dur_max_entropy = np.log(len(dur_p)) if len(dur_p) > 1 else 1
    dur_variety = round((dur_entropy / dur_max_entropy) * 100, 1) if dur_max_entropy > 0 else 0.0

    balance_score = round((type_variety + explicit_balance + div + dur_variety) / 4, 1)
    d["playlist_balance"] = dict(
        score=balance_score, type_variety=type_variety, explicit_balance=round(explicit_balance, 1),
        diversity=div, duration_variety=dur_variety,
    )

    # ---------------- 12. DECISION ALERTS ----------------
    alerts = []
    if div > 65:
        alerts.append(("green", "🟢", "Opportunity",
                        f"High artist diversity detected ({div:.1f}/100). Emerging artists have strong growth "
                        f"potential in the current UK playlist environment."))
    if album_share - single_share > 20:
        alerts.append(("yellow", "🟡", "Warning",
                        f"Album releases dominate the chart ({album_share:.1f}% vs {single_share:.1f}% singles). "
                        f"A single-only strategy may underperform relative to the current market mix."))
    if conc10 > 55:
        alerts.append(("red", "🔴", "Risk",
                        f"Artist Concentration Index is {conc10:.1f}%, above the 55% overdependence threshold. "
                        f"Revenue is materially exposed to a small group of top artists."))
    if sat > 65:
        alerts.append(("red", "🔴", "Risk",
                        f"Market Saturation Index is {sat:.1f}%. The chart is dominated by repeat artists, "
                        f"limiting organic discovery of new talent."))
    if exp_share > 70:
        alerts.append(("yellow", "🟡", "Warning",
                        f"Explicit content share is {exp_share:.1f}% of the catalog — radio and family-audience "
                        f"reach may be constrained without clean edits."))
    if not alerts:
        alerts.append(("green", "🟢", "Opportunity",
                        "No critical thresholds breached — current market structure is stable across all "
                        "monitored metrics."))
    d["alerts"] = alerts

    # ---------------- 13. PREDICTIVE RECOMMENDATION ENGINE ----------------
    overall_conf = round(float(np.mean([
        d["artist_signing"]["confidence"], d["release_strategy"]["confidence"],
        d["collaboration_strategy"]["confidence"], d["content_strategy"]["confidence"],
    ])), 1)
    d["predictive_engine"] = dict(
        best_release=release_decision, best_artist=signing_decision,
        best_content=content_decision, best_collaboration=collab_decision,
        overall_confidence=overall_conf,
    )

    # ---------------- 10. EXECUTIVE AI SUMMARY ----------------
    diversity_phrase = "exceptionally high" if div >= 75 else "solid" if div >= 55 else "limited"
    concentration_phrase = ("highly concentrated" if conc10 >= 50 else
                             "moderately concentrated" if conc10 >= 30 else
                             "low-concentration, highly competitive")
    release_phrase = ("album releases currently outperform standalone singles" if gap > 1.5 else
                       "singles currently outperform album releases" if gap < -1.5 else
                       "albums and singles perform comparably")
    explicit_phrase = ("a strong performance driver" if exp_gap > 5 else
                        "a modest contributor, trailing clean content" if exp_gap < -5 else
                        "a moderate contributor to playlist success")

    summary = (
        f"The UK playlist demonstrates {diversity_phrase} artist diversity ({div:.1f}/100) and a "
        f"{concentration_phrase} market ({conc10:.1f}% top-10 share), placing the UK Market Health Score at "
        f"{health_score:.1f}/100 ({health_band}). {release_phrase.capitalize()}, while explicit content remains "
        f"{explicit_phrase} ({exp_share:.1f}% share). Atlantic should pursue a '{signing_decision.lower()}' "
        f"posture on A&R, a '{release_decision.lower()}' release cadence, and a '{collab_decision.lower()}' "
        f"collaboration approach. The Artist Opportunity Score of {opp_blended:.1f}/100 suggests the UK market is "
        f"currently '{opp_band.lower()}' for new signings, and overall predictive confidence across these "
        f"recommendations stands at {overall_conf:.1f}%."
    )
    d["executive_summary"] = summary

    return d


def generate_strategic_recommendations(m: dict, d: dict) -> list:
    """Item 11 — Strategic Recommendations across the 11 requested executive focus areas,
    each derived directly from the metric engine and the Executive Decision Engine above."""
    recs = [
        ("Artist Acquisition", d["artist_signing"]["reason"] + " " + d["artist_signing"]["impact"]),
        ("Release Planning", d["release_strategy"]["reason"] + " " + d["release_strategy"]["impact"]),
        ("Marketing", f"Allocate budget as {d['marketing_strategy']['budget_split']}, using "
                      f"{d['marketing_strategy']['campaign_type'].lower()}."),
        ("Promotion", f"Prioritize promotional spend on: {', '.join(d['marketing_strategy']['priority_artists'])}."),
        ("Radio Strategy", "Lead all radio pitching with clean edits regardless of streaming explicit "
                            "performance, to maximize broadcast compliance and reach."),
        ("Streaming Strategy", f"On streaming platforms, lean toward "
                                f"{'explicit' if m['explicit_success_rate'] >= m['clean_success_rate'] else 'clean'} "
                                f"versions, which currently convert to hits at a higher rate."),
        ("Content Localization", f"UK listeners respond best to {m['top_combo'][0]} / {m['top_combo'][1]} / "
                                  f"{m['top_combo'][2]} content (avg. popularity {m['top_combo_score']:.1f}) — "
                                  f"localize release plans around this combination."),
        ("Investment Priorities", f"Top-5 artist concentration is {m['top5_concentration']:.1f}%; " +
         ("prioritize retention deals for anchor artists." if m['top5_concentration'] > 25 else
          "spread investment evenly across the roster.")),
        ("Growth Opportunities", (
            f"{len(m['opportunity_artists'])} emerging artists ({m['artist_opportunity_score']:.1f}% of roster) "
            f"show high popularity despite low chart frequency — strong candidates for promotional investment."
        ) if m["opportunity_artists"] else "No standout low-frequency/high-popularity outliers detected under "
                                            "current filters."),
        ("Risk Management", f"Market Saturation Index is {m['market_saturation_index']:.1f}%; " +
         ("hedge overdependence risk with A&R investment in emerging talent." if m['market_saturation_index'] > 65
          else "artist turnover is healthy, spreading commercial risk broadly.")),
        ("Future UK Expansion", f"Market Competition Score is {m['market_competition_score']:.1f}/100; " +
         ("the market remains highly contestable — an aggressive release push can capture share quickly."
          if m['market_competition_score'] > 60 else
          "competition for chart slots is intense — expansion should lean on proven artists and formats.")),
    ]
    return recs


def render_executive_decision_center(m: dict, d: dict) -> list:
    """Renders the full 🎯 Executive Decision Center: AI summary, alerts, gauges, decision
    cards, and the expandable strategic recommendation set. Returns the recommendation list
    so it can also be reused in the Export tab."""
    section("🎯 Executive Decision Center",
            "Analytics converted into CEO-ready decisions — generated live from the current filter selection")

    st.markdown(f'<div class="exec-summary-box">🧠 <b>Executive AI Summary</b><br><br>{d["executive_summary"]}</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)

    sub_section("🚨 Decision Alerts")
    for level, icon, title, body in d["alerts"]:
        alert_card(level, icon, title, body)
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    sub_section("📟 Executive Scorecards")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.plotly_chart(chart_gauge(d["market_health"]["score"], "UK Market Health Score"), use_container_width=True)
        st.markdown(f'<div style="text-align:center;">{badge(d["market_health"]["band"], d["market_health"]["level"])}</div>',
                    unsafe_allow_html=True)
    with g2:
        st.plotly_chart(chart_gauge(d["market_competition"]["score"], "Market Competition Gauge"), use_container_width=True)
    with g3:
        st.plotly_chart(chart_gauge(d["artist_opportunity"]["score"], "Artist Opportunity Score"), use_container_width=True)
        st.markdown(f'<div style="text-align:center;">{badge(d["artist_opportunity"]["band"], "purple")}</div>',
                    unsafe_allow_html=True)
    with g4:
        st.plotly_chart(chart_gauge(d["playlist_balance"]["score"], "Playlist Balance Score"), use_container_width=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    sub_section("🧩 Strategic Decision Cards")
    row1 = st.columns(2)
    decision_card(row1[0], "🎤", "Artist Signing Strategy", d["artist_signing"]["decision"],
                  d["artist_signing"]["reason"], d["artist_signing"]["confidence"], d["artist_signing"]["impact"])
    decision_card(row1[1], "💿", "Release Strategy", d["release_strategy"]["decision"],
                  d["release_strategy"]["reason"], d["release_strategy"]["confidence"], d["release_strategy"]["impact"])

    row2 = st.columns(2)
    decision_card(row2[0], "🤝", "Collaboration Strategy", d["collaboration_strategy"]["decision"],
                  d["collaboration_strategy"]["reason"], d["collaboration_strategy"]["confidence"],
                  d["collaboration_strategy"]["impact"])
    decision_card(row2[1], "🔞", "Content Strategy", d["content_strategy"]["decision"],
                  d["content_strategy"]["reason"], d["content_strategy"]["confidence"], d["content_strategy"]["impact"])

    row3 = st.columns(2)
    decision_card(
        row3[0], "📢", "Marketing Strategy", f"Budget: {d['marketing_strategy']['budget_split']}",
        f"{d['marketing_strategy']['campaign_type']}. Audience targeting: "
        f"{d['marketing_strategy']['audience_targeting']}.",
        d["marketing_strategy"]["confidence"],
        f"Priority artists this cycle: {', '.join(d['marketing_strategy']['priority_artists'])}.",
    )
    decision_card(
        row3[1], "🔮", "Predictive Recommendation Engine",
        f"Release → {d['predictive_engine']['best_release']}  |  Artist → {d['predictive_engine']['best_artist']}",
        f"Content → {d['predictive_engine']['best_content']}  |  Collaboration → "
        f"{d['predictive_engine']['best_collaboration']}",
        d["predictive_engine"]["overall_confidence"],
        "Consolidated, cross-metric prediction combining all four strategic decision engines above.",
    )

    sub_section("📋 Strategic Recommendations")
    strategic_recs = generate_strategic_recommendations(m, d)
    with st.expander("Expand full strategic recommendation set (11 focus areas)"):
        for title, body in strategic_recs:
            st.markdown(
                f'<div class="rec-card"><div class="rec-title">🔹 {title}</div><div class="rec-body">{body}</div></div>',
                unsafe_allow_html=True,
            )

    if d["artist_opportunity"]["contributing_artists"]:
        with st.expander("🌱 Artists Contributing to the Opportunity Score"):
            st.write(", ".join(d["artist_opportunity"]["contributing_artists"]))

    return strategic_recs


# ==========================================================================================
# 6. SMART INSIGHTS & EXECUTIVE RECOMMENDATIONS (fully data-driven)
# ==========================================================================================
def generate_insights(df: pd.DataFrame, m: dict) -> list:
    insights = []

    top_artist = m["artist_counts"].index[0]
    insights.append(f"🏆 <b>{top_artist}</b> is the most dominant artist, appearing in "
                     f"{m['artist_counts'].iloc[0]} chart entries "
                     f"({m['artist_market_share'].iloc[0]:.1f}% market share).")

    daily_counts = df.groupby(df["date"].dt.date)["artist"].nunique()
    if len(daily_counts):
        most_competitive_day = daily_counts.idxmax()
        insights.append(f"⚔️ The most competitive day was <b>{most_competitive_day.strftime('%d/%m/%Y')}</b>, "
                         f"featuring {int(daily_counts.max())} unique artists on the chart.")

    monthly_div = df.groupby("month").apply(
        lambda g: len(set(a for lst in g["artist_list"] for a in lst))
    )
    if len(monthly_div):
        least_diverse_month = monthly_div.idxmin()
        insights.append(f"📉 <b>{least_diverse_month}</b> was the least diverse period, with only "
                         f"{int(monthly_div.min())} distinct artists charting.")

    daily_explicit = df.groupby(df["date"].dt.date)["is_explicit"].mean()
    if len(daily_explicit):
        highest_explicit_day = daily_explicit.idxmax()
        insights.append(f"🔞 <b>{highest_explicit_day.strftime('%d/%m/%Y')}</b> recorded the highest explicit-content "
                         f"share at {daily_explicit.max()*100:.1f}%.")

    if m["album_success_score"] >= m["single_success_score"]:
        insights.append(f"💿 Albums are outperforming singles on average popularity "
                         f"({m['album_success_score']:.1f} vs {m['single_success_score']:.1f}) — "
                         f"favor full-album releases for upcoming drops.")
    else:
        insights.append(f"🎵 Singles are outperforming albums on average popularity "
                         f"({m['single_success_score']:.1f} vs {m['album_success_score']:.1f}) — "
                         f"a singles-first release cadence is currently more effective.")

    if m["collab_success_rate"] >= m["solo_success_rate"]:
        insights.append(f"🤝 Collaborations post a higher hit-rate than solo tracks "
                         f"({m['collab_success_rate']:.1f}% vs {m['solo_success_rate']:.1f}%) — "
                         f"prioritize featured collaborations.")
    else:
        insights.append(f"🎤 Solo tracks post a higher hit-rate than collaborations "
                         f"({m['solo_success_rate']:.1f}% vs {m['collab_success_rate']:.1f}%).")

    combo = m["top_combo"]
    insights.append(f"👂 UK listeners respond best to <b>{combo[0]} / {combo[1]} / {combo[2]}</b> content "
                     f"(avg. popularity {m['top_combo_score']:.1f}).")

    insights.append(f"📊 The top 10 artists control <b>{m['top10_concentration']:.1f}%</b> of all chart appearances — "
                     f"market concentration is {'high' if m['top10_concentration'] > 50 else 'moderate' if m['top10_concentration'] > 30 else 'low'}.")

    return insights


def generate_recommendations(df: pd.DataFrame, m: dict) -> list:
    recs = []

    # Artist Signing Strategy
    recs.append(("Artist Signing Strategy",
                 f"Market concentration among the top 10 artists stands at {m['top10_concentration']:.1f}%. "
                 + ("Diversify the roster — signing mid-tier or opportunity artists reduces dependency risk."
                    if m['top10_concentration'] > 45 else
                    "Concentration is healthy; continued investment in current top performers is low-risk.")))

    # Marketing Strategy
    best_bucket = m["pop_by_duration_bucket"].idxmax() if len(m["pop_by_duration_bucket"]) else "N/A"
    recs.append(("Marketing Strategy",
                 f"Tracks in the <b>{best_bucket}</b> duration bucket achieve the highest average popularity "
                 f"({m['pop_by_duration_bucket'].max():.1f}). Align promotional edits and playlist pitches to this length."))

    # Release Strategy
    if m["release_strategy_gap"] > 1:
        recs.append(("Release Strategy",
                     f"Albums outperform singles by {m['release_strategy_gap']:.1f} popularity points. "
                     f"Prioritize album-length releases for lead artists over the next cycle."))
    elif m["release_strategy_gap"] < -1:
        recs.append(("Release Strategy",
                     f"Singles outperform albums by {abs(m['release_strategy_gap']):.1f} popularity points. "
                     f"Favor a singles-led rollout with a compilation release later."))
    else:
        recs.append(("Release Strategy",
                     "Albums and singles perform comparably — release format can be chosen on artist-specific grounds."))

    # Content Strategy
    if m["explicit_success_rate"] > m["clean_success_rate"]:
        recs.append(("Content Strategy",
                     f"Explicit content shows a higher hit-rate ({m['explicit_success_rate']:.1f}% vs "
                     f"{m['clean_success_rate']:.1f}%). Retaining explicit versions in the primary release is advisable, "
                     f"with a clean edit offered for radio/family playlists."))
    else:
        recs.append(("Content Strategy",
                     f"Clean content shows a higher hit-rate ({m['clean_success_rate']:.1f}% vs "
                     f"{m['explicit_success_rate']:.1f}%). Clean edits should lead playlist pitching."))

    # Collaboration Strategy
    if m["collab_success_rate"] > m["solo_success_rate"]:
        recs.append(("Collaboration Strategy",
                     f"Collaborations convert to hits at {m['collab_success_rate']:.1f}% vs. {m['solo_success_rate']:.1f}% "
                     f"for solo work. Actively broker featured collaborations for developing artists."))
    else:
        recs.append(("Collaboration Strategy",
                     f"Solo releases convert to hits at {m['solo_success_rate']:.1f}% vs. {m['collab_success_rate']:.1f}% "
                     f"for collaborations. Protect solo brand identity for headline artists."))

    # Risk Analysis
    recs.append(("Risk Analysis",
                 f"Market Saturation Index is {m['market_saturation_index']:.1f}%. "
                 + ("A high share of repeat artists signals limited new-entrant risk but exposes revenue to a small roster — "
                    "hedge with A&R investment in emerging talent."
                    if m['market_saturation_index'] > 60 else
                    "Artist turnover is healthy, spreading commercial risk across a broad roster.")))

    # Growth Opportunities
    recs.append(("Growth Opportunities",
                 f"The Market Diversity Index is {m['diversity_index']:.1f}/100. "
                 + ("There is room to widen playlist variety without sacrificing popularity."
                    if m['diversity_index'] < 70 else
                    "The current roster mix already reflects strong diversity; maintain the current curation approach.")))

    # Emerging Artist Opportunities
    if m["opportunity_artists"]:
        sample = ", ".join(m["opportunity_artists"][:5])
        recs.append(("Emerging Artist Opportunities",
                     f"{len(m['opportunity_artists'])} artists ({m['artist_opportunity_score']:.1f}% of the roster) show "
                     f"high popularity despite low chart frequency — notably: {sample}. These are strong candidates for "
                     f"increased promotional investment."))
    else:
        recs.append(("Emerging Artist Opportunities",
                     "No clear low-frequency/high-popularity outliers were detected in the current filtered view."))

    # Investment Priority
    recs.append(("Investment Priority",
                 f"Top-5 artist concentration is {m['top5_concentration']:.1f}%. "
                 + ("Investment should prioritize retention deals for these anchor artists, who materially drive chart share."
                    if m['top5_concentration'] > 25 else
                    "No single artist bloc dominates chart share; investment can be spread more evenly across the roster.")))

    # Market Expansion Strategy
    recs.append(("Market Expansion Strategy",
                 f"Market Competition Score is {m['market_competition_score']:.1f}/100. "
                 + ("The UK chart remains highly contestable — an aggressive push with new releases can capture share quickly."
                    if m['market_competition_score'] > 60 else
                    "Competition for chart slots is intense; expansion should lean on already-proven artists and formats.")))

    return recs


# ==========================================================================================
# 7. CHART BUILDERS
# ==========================================================================================
def chart_artist_leaderboard(m: dict, top_n: int = 15):
    top = m["artist_counts"].head(top_n).sort_values()
    fig = go.Figure(go.Bar(
        x=top.values, y=top.index, orientation="h",
        marker=dict(color=top.values, colorscale=[[0, "#2c2f45"], [1, BRAND_PRIMARY]]),
        text=top.values, textposition="outside",
        hovertemplate="<b>%{y}</b><br>Appearances: %{x}<extra></extra>",
    ))
    fig.update_layout(
        title="Interactive Artist Leaderboard", template="plotly_dark",
        height=460, margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Chart Appearances", yaxis_title="",
    )
    return fig


def chart_artist_treemap(m: dict, top_n: int = 25):
    top = m["artist_counts"].head(top_n).reset_index()
    top.columns = ["Artist", "Appearances"]
    fig = px.treemap(
        top, path=["Artist"], values="Appearances", color="Appearances",
        color_continuous_scale=[[0, "#2c2f45"], [1, BRAND_PRIMARY]],
        title="Artist Market Share — Treemap",
    )
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_sunburst(df: pd.DataFrame):
    fig = px.sunburst(
        df, path=["album_type", "Collaboration", "Explicit_Label"],
        color="album_type", color_discrete_sequence=PALETTE,
        title="Content Structure — Sunburst (Album Type → Collaboration → Explicit)",
    )
    fig.update_layout(template="plotly_dark", height=480, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_sankey(df: pd.DataFrame):
    labels, idx = [], {}

    def get_idx(label):
        if label not in idx:
            idx[label] = len(labels)
            labels.append(label)
        return idx[label]

    flows = Counter()
    for _, row in df.iterrows():
        a, b, c = f"{row['album_type']}", f"{row['Collaboration']}", f"{row['Rank_Group']}"
        flows[(a, b)] += 1
        flows[(b, c)] += 1

    source, target, value = [], [], []
    for (a, b), v in flows.items():
        source.append(get_idx(a))
        target.append(get_idx(b))
        value.append(v)

    fig = go.Figure(go.Sankey(
        node=dict(pad=18, thickness=18, label=labels,
                   color=[PALETTE[i % len(PALETTE)] for i in range(len(labels))]),
        link=dict(source=source, target=target, value=value, color="rgba(108,92,231,0.35)"),
    ))
    fig.update_layout(title="Release Flow: Album Type → Collaboration → Rank Group",
                       template="plotly_dark", height=460, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_bubble(df: pd.DataFrame):
    agg = df.groupby(["primary_artist"]).agg(
        appearances=("song", "count"), avg_popularity=("popularity", "mean"),
        avg_duration=("duration_min", "mean"),
    ).reset_index().sort_values("appearances", ascending=False).head(30)
    fig = px.scatter(
        agg, x="avg_duration", y="avg_popularity", size="appearances", color="appearances",
        hover_name="primary_artist", color_continuous_scale=[[0, "#2c2f45"], [1, BRAND_SECONDARY]],
        title="Artist Bubble Map — Duration vs. Popularity vs. Chart Frequency",
        labels={"avg_duration": "Avg Duration (min)", "avg_popularity": "Avg Popularity"},
    )
    fig.update_layout(template="plotly_dark", height=460, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_heatmap(df: pd.DataFrame):
    pivot = df.pivot_table(index="weekday", columns="album_type", values="popularity", aggfunc="mean")
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([d for d in weekday_order if d in pivot.index])
    fig = px.imshow(
        pivot, text_auto=".1f", color_continuous_scale=[[0, "#1b1e2b"], [1, BRAND_PRIMARY]],
        title="Average Popularity Heatmap — Weekday × Album Type", aspect="auto",
    )
    fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_calendar_heatmap(df: pd.DataFrame):
    daily = df.groupby(df["date"].dt.date).size().reset_index(name="songs")
    daily["date"] = pd.to_datetime(daily["date"])
    daily["week"] = daily["date"].dt.isocalendar().week
    daily["weekday"] = daily["date"].dt.day_name()
    daily["year"] = daily["date"].dt.year
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = daily.pivot_table(index="weekday", columns=["year", "week"], values="songs", aggfunc="sum")
    pivot = pivot.reindex(weekday_order)
    fig = px.imshow(
        pivot, color_continuous_scale=[[0, "#1b1e2b"], [1, BRAND_SECONDARY]],
        aspect="auto", title="Calendar Heatmap — Chart Entries by Week",
    )
    fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=50, b=10),
                       xaxis_title="Week of Year", yaxis_title="")
    return fig


def chart_violin(df: pd.DataFrame):
    fig = px.violin(
        df, x="album_type", y="popularity", color="album_type", box=True, points=False,
        color_discrete_sequence=PALETTE, title="Popularity Distribution by Album Type — Violin Plot",
    )
    fig.update_layout(template="plotly_dark", height=440, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
    return fig


def chart_box(df: pd.DataFrame):
    fig = px.box(
        df, x="Rank_Group", y="duration_min", color="Rank_Group", color_discrete_sequence=PALETTE,
        title="Track Duration Spread by Rank Group — Box Plot",
    )
    fig.update_layout(template="plotly_dark", height=440, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
    return fig


def chart_radar(m: dict, df: pd.DataFrame):
    types = df["album_type"].unique().tolist()
    categories = ["Avg Popularity", "Avg Duration (scaled)", "Explicit % ", "Collaboration %", "Volume (scaled)"]
    fig = go.Figure()
    max_vol = df["album_type"].value_counts().max()
    for i, t in enumerate(types):
        sub = df[df["album_type"] == t]
        vals = [
            sub["popularity"].mean(),
            min(sub["duration_min"].mean() * 15, 100),
            sub["is_explicit"].mean() * 100,
            (sub["Collaboration"] == "Collaboration").mean() * 100,
            len(sub) / max_vol * 100 if max_vol else 0,
        ]
        fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=categories + [categories[0]],
                                        fill="toself", name=t, line=dict(color=PALETTE[i % len(PALETTE)])))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#9aa0b4"),
                    bgcolor="rgba(0,0,0,0)"),
        template="plotly_dark", title="Album Type Performance — Radar Comparison",
        height=460, margin=dict(l=40, r=40, t=60, b=20),
    )
    return fig


def chart_scatter_matrix(df: pd.DataFrame):
    sample = df.sample(min(1500, len(df)), random_state=42)
    fig = px.scatter_matrix(
        sample, dimensions=["popularity", "duration_min", "total_tracks", "position"],
        color="album_type", color_discrete_sequence=PALETTE,
        title="Multi-Dimensional Relationship Matrix",
    )
    fig.update_layout(template="plotly_dark", height=560, margin=dict(l=10, r=10, t=50, b=10))
    fig.update_traces(diagonal_visible=False, showupperhalf=False, marker=dict(size=4, opacity=0.6))
    return fig


def chart_timeline(df: pd.DataFrame):
    daily = df.groupby(df["date"].dt.date).agg(
        avg_popularity=("popularity", "mean"), songs=("song", "count")
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["avg_popularity"], mode="lines",
                               name="Avg Popularity", line=dict(color=BRAND_PRIMARY, width=2)))
    fig.add_trace(go.Bar(x=daily["date"], y=daily["songs"], name="Chart Entries",
                          marker=dict(color=BRAND_SECONDARY, opacity=0.25), yaxis="y2"))
    fig.update_layout(
        title="Timeline Analysis — Average Popularity & Volume Over Time", template="plotly_dark",
        height=440, margin=dict(l=10, r=10, t=50, b=10),
        yaxis=dict(title="Avg Popularity"),
        yaxis2=dict(title="Entries", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.1),
    )
    return fig


def chart_histogram(df: pd.DataFrame):
    fig = px.histogram(
        df, x="popularity", nbins=25, color_discrete_sequence=[BRAND_PRIMARY],
        title="Popularity Distribution — Histogram", marginal="box",
    )
    fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def chart_network_graph(df: pd.DataFrame, min_edge_weight: int = 1, max_nodes: int = 60):
    """Collaboration network — serves as a chord-diagram-like visualization of artist ties."""
    edge_counter = Counter()
    for artists in df.loc[df["artist_count"] > 1, "artist_list"]:
        for a, b in combinations(sorted(set(artists)), 2):
            edge_counter[(a, b)] += 1

    if not edge_counter:
        return None

    g = nx.Graph()
    for (a, b), w in edge_counter.items():
        if w >= min_edge_weight:
            g.add_edge(a, b, weight=w)

    if g.number_of_nodes() == 0:
        return None

    # keep the graph readable
    if g.number_of_nodes() > max_nodes:
        top_nodes = sorted(g.degree, key=lambda x: x[1], reverse=True)[:max_nodes]
        g = g.subgraph([n for n, _ in top_nodes]).copy()

    pos = nx.spring_layout(g, seed=42, k=0.6)

    edge_x, edge_y = [], []
    for u, v in g.edges():
        edge_x += [pos[u][0], pos[v][0], None]
        edge_y += [pos[u][1], pos[v][1], None]

    node_x = [pos[n][0] for n in g.nodes()]
    node_y = [pos[n][1] for n in g.nodes()]
    node_deg = [g.degree(n) for n in g.nodes()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines",
                               line=dict(width=1, color="rgba(108,92,231,0.35)"), hoverinfo="none"))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=list(g.nodes()), textposition="top center",
        textfont=dict(size=9, color="#cfd2e2"),
        marker=dict(size=[8 + d * 3 for d in node_deg], color=node_deg,
                     colorscale=[[0, "#2c2f45"], [1, BRAND_ACCENT]], line=dict(width=1, color="white")),
        hovertemplate="<b>%{text}</b><br>Connections: %{marker.color}<extra></extra>",
    ))
    fig.update_layout(
        title="Artist Collaboration Network", template="plotly_dark", showlegend=False,
        height=520, margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig


def chart_pareto(m: dict, top_n: int = 20):
    top = m["artist_counts"].head(top_n)
    cum_pct = (top.cumsum() / m["artist_counts"].sum() * 100).round(1)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=top.index, y=top.values, name="Appearances", marker=dict(color=BRAND_PRIMARY)))
    fig.add_trace(go.Scatter(x=top.index, y=cum_pct, name="Cumulative %", yaxis="y2",
                               line=dict(color=BRAND_ACCENT, width=3), mode="lines+markers"))
    fig.update_layout(
        title="Pareto Analysis — Artist Contribution to Total Chart Volume", template="plotly_dark",
        height=460, margin=dict(l=10, r=10, t=50, b=10),
        yaxis=dict(title="Appearances"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105], showgrid=False),
        legend=dict(orientation="h", y=1.12),
    )
    return fig


def chart_cumulative_market_share(m: dict):
    counts = m["artist_counts"]
    cum = (counts.cumsum() / counts.sum() * 100)
    x = np.arange(1, len(cum) + 1)
    fig = go.Figure(go.Scatter(x=x, y=cum.values, mode="lines", fill="tozeroy",
                                 line=dict(color=BRAND_SECONDARY, width=2)))
    fig.add_hline(y=80, line_dash="dash", line_color=BRAND_ACCENT,
                   annotation_text="80% market share", annotation_position="bottom right")
    fig.update_layout(
        title="Cumulative Market Share — Artist Rank vs. Chart Share", template="plotly_dark",
        height=420, margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Artist Rank (by appearances)", yaxis_title="Cumulative Share (%)",
    )
    return fig


def chart_gauge(value: float, title: str) -> go.Figure:
    """Generic 0-100 Plotly gauge used for the Market Health / Competition / Opportunity /
    Playlist Balance scorecards in the Executive Decision Center."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": " /100", "font": {"color": "white", "size": 28}},
        title={"text": title, "font": {"color": "#cfd2e2", "size": 13}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#9aa0b4", "tickfont": {"color": "#9aa0b4", "size": 9}},
            "bar": {"color": BRAND_PRIMARY, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(255,107,107,0.25)"},
                {"range": [40, 65], "color": "rgba(255,192,72,0.25)"},
                {"range": [65, 100], "color": "rgba(0,210,160,0.25)"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "thickness": 0.85, "value": value},
        },
    ))
    fig.update_layout(template="plotly_dark", height=260, margin=dict(l=20, r=20, t=45, b=10),
                       paper_bgcolor="rgba(0,0,0,0)")
    return fig


# ==========================================================================================
# 8. MAIN APPLICATION
# ==========================================================================================
def main():
    inject_css()

    # ---- Load & prepare data ----
    try:
        raw_df = load_raw_data(DATA_PATH)
    except FileNotFoundError:
        st.warning(f"Could not find `{DATA_PATH}` next to app.py.")
        uploaded = st.file_uploader("Upload the Atlantic_United_Kingdom.csv dataset", type="csv")
        if uploaded is None:
            st.stop()
        raw_df = pd.read_csv(uploaded)

    with st.spinner("Engineering features and building market intelligence..."):
        df_full = engineer_features(raw_df)

    # ---- Hero header ----
    st.markdown(
        f"""
        <div class="hero-header">
            <p class="hero-title">🎧 United Kingdom Top 50 Playlist — Market Intelligence</p>
            <p class="hero-subtitle">Market Structure · Artist Diversity · Content Localization Analysis</p>
            <span class="hero-tag">ATLANTIC RECORDING CORPORATION · EXECUTIVE BI DASHBOARD</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Sidebar filters ----
    filters = build_sidebar(df_full)
    filtered_df = apply_filters(df_full, filters)

    if filtered_df.empty:
        st.error("No records match the current filter combination. Please widen your filters.")
        st.stop()

    progress = st.progress(0, text="Computing business intelligence metrics...")
    metrics = compute_bi_metrics(filtered_df)
    progress.progress(50, text="Computing baseline comparison...")
    full_metrics = compute_bi_metrics(df_full)
    deltas = compute_deltas(metrics, full_metrics)
    progress.progress(80, text="Translating metrics into executive decisions...")
    decisions = compute_executive_decisions(filtered_df, metrics)
    progress.progress(100, text="Done")
    progress.empty()

    # ======================================================================================
    # EXECUTIVE KPI SECTION
    # ======================================================================================
    section("📊 Executive KPI Summary", "Live metrics for the current filter selection, benchmarked against the full dataset")

    r1 = st.columns(4, gap="medium")
    kpi_card(r1[0], "🎵", "Total Songs", f"{len(filtered_df):,}")
    kpi_card(r1[1], "🎤", "Unique Artists", f"{metrics['unique_artists']:,}", deltas.get("unique_artists"), " artists")
    kpi_card(r1[2], "📈", "Top-10 Concentration", f"{metrics['top10_concentration']:.1f}%", deltas.get("top10_concentration"))
    kpi_card(r1[3], "🤝", "Collaboration Ratio", f"{metrics['collaboration_ratio']:.1f}%", deltas.get("collaboration_ratio"))

    r2 = st.columns(4, gap="medium")
    kpi_card(r2[0], "🔞", "Explicit Content Share", f"{metrics['explicit_share']:.1f}%", deltas.get("explicit_share"))
    kpi_card(r2[1], "🌈", "Diversity Score", f"{metrics['diversity_index']:.1f}/100", deltas.get("diversity_index"))
    kpi_card(r2[2], "⭐", "Average Popularity", f"{metrics['avg_popularity']:.1f}", deltas.get("avg_popularity"), " pts")
    kpi_card(r2[3], "⏱️", "Average Duration", f"{metrics['avg_duration']:.2f} min", deltas.get("avg_duration"), " min")

    st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)

    # ======================================================================================
    # TABS
    # ======================================================================================
    tabs = st.tabs([
        "🎯 Executive Decision Center", "🏠 Overview", "🎤 Artist Intelligence", "💿 Content & Structure",
        "🌐 Market Dynamics", "📐 BI Metrics", "🧭 Executive Recommendations", "📤 Export",
    ])

    # ---------------------------------------------------------------------------------
    # TAB 0 — EXECUTIVE DECISION CENTER
    # ---------------------------------------------------------------------------------
    with tabs[0]:
        strategic_recs = render_executive_decision_center(metrics, decisions)

    # ---------------------------------------------------------------------------------
    # TAB 1 — OVERVIEW
    # ---------------------------------------------------------------------------------
    with tabs[1]:
        section("💡 Smart Insights", "Automatically generated from the current filtered data")
        insights = generate_insights(filtered_df, metrics)
        cols = st.columns(2)
        for i, insight in enumerate(insights):
            cols[i % 2].markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_artist_leaderboard(metrics), use_container_width=True)
        with c2:
            st.plotly_chart(chart_pareto(metrics), use_container_width=True)

        st.plotly_chart(chart_timeline(filtered_df), use_container_width=True)

    # ---------------------------------------------------------------------------------
    # TAB 2 — ARTIST INTELLIGENCE
    # ---------------------------------------------------------------------------------
    with tabs[2]:
        section("🎤 Artist Market Structure", "Concentration, collaboration ties, and emerging opportunities")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_artist_treemap(metrics), use_container_width=True)
        with c2:
            st.plotly_chart(chart_cumulative_market_share(metrics), use_container_width=True)

        net_fig = chart_network_graph(filtered_df)
        if net_fig:
            st.plotly_chart(net_fig, use_container_width=True)
        else:
            st.info("No multi-artist collaborations found in the current filter selection to build a network graph.")

        with st.expander("🌱 Emerging Artist Opportunities (low frequency, high popularity)"):
            if metrics["opportunity_artists"]:
                st.write(", ".join(metrics["opportunity_artists"]))
                st.caption(f"Opportunity Score: {metrics['artist_opportunity_score']:.1f}% of the current roster")
            else:
                st.write("No standout opportunity artists detected under the current filters.")

    # ---------------------------------------------------------------------------------
    # TAB 3 — CONTENT & STRUCTURE
    # ---------------------------------------------------------------------------------
    with tabs[3]:
        section("💿 Content & Release Structure", "Album types, explicit/clean mix, duration profile")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_sunburst(filtered_df), use_container_width=True)
        with c2:
            st.plotly_chart(chart_sankey(filtered_df), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(chart_violin(filtered_df), use_container_width=True)
        with c4:
            st.plotly_chart(chart_box(filtered_df), use_container_width=True)

        c5, c6 = st.columns(2)
        with c5:
            st.plotly_chart(chart_radar(metrics, filtered_df), use_container_width=True)
        with c6:
            st.plotly_chart(chart_histogram(filtered_df), use_container_width=True)

    # ---------------------------------------------------------------------------------
    # TAB 4 — MARKET DYNAMICS
    # ---------------------------------------------------------------------------------
    with tabs[4]:
        section("🌐 Market Dynamics & Competitive Landscape")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_bubble(filtered_df), use_container_width=True)
        with c2:
            st.plotly_chart(chart_heatmap(filtered_df), use_container_width=True)

        st.plotly_chart(chart_calendar_heatmap(filtered_df), use_container_width=True)
        st.plotly_chart(chart_scatter_matrix(filtered_df), use_container_width=True)

    # ---------------------------------------------------------------------------------
    # TAB 5 — BI METRICS GRID (all 20 metrics)
    # ---------------------------------------------------------------------------------
    with tabs[5]:
        section("📐 Decision-Making Metrics", "All 20 business intelligence metrics computed live from filtered data")

        metric_rows = [
            ("1. Artist Market Share (leader)", f"{metrics['artist_counts'].index[0]} — {metrics['artist_market_share'].iloc[0]:.1f}%"),
            ("2. Top 5 Artist Concentration", f"{metrics['top5_concentration']:.1f}%"),
            ("3. Top 10 Artist Concentration", f"{metrics['top10_concentration']:.1f}%"),
            ("4. Market Diversity Index", f"{metrics['diversity_index']:.1f} / 100"),
            ("5. Collaboration Success Rate", f"{metrics['collab_success_rate']:.1f}%  (hit ≥ {metrics['hit_threshold']:.0f} popularity)"),
            ("6. Explicit Song Success Rate", f"{metrics['explicit_success_rate']:.1f}%"),
            ("7. Clean Song Success Rate", f"{metrics['clean_success_rate']:.1f}%"),
            ("8. Album Success Score", f"{metrics['album_success_score']:.1f} avg. popularity"),
            ("9. Single Success Score", f"{metrics['single_success_score']:.1f} avg. popularity"),
            ("14. Artist Repeat Frequency", f"{metrics['artist_repeat_frequency']:.2f} appearances / artist"),
            ("15. Market Saturation Index", f"{metrics['market_saturation_index']:.1f}%"),
            ("16. Playlist Balance Index", f"{metrics['playlist_balance_index']:.1f} / 100"),
            ("17. Release Strategy Score", f"{metrics['release_strategy_gap']:+.1f} (album − single popularity gap)"),
            ("18. Artist Opportunity Score", f"{metrics['artist_opportunity_score']:.1f}% of roster"),
            ("19. UK Listener Preference Score", f"{metrics['top_combo'][0]} / {metrics['top_combo'][1]} / {metrics['top_combo'][2]} → {metrics['top_combo_score']:.1f}"),
            ("20. Market Competition Score", f"{metrics['market_competition_score']:.1f} / 100"),
        ]

        grid = st.columns(2)
        for i, (label, value) in enumerate(metric_rows):
            grid[i % 2].markdown(
                f'<div class="rec-card"><div class="rec-title">{label}</div>'
                f'<div class="rec-body">{value}</div></div>', unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**10. Average Popularity by Album Type**")
            st.dataframe(metrics["pop_by_album_type"].rename("Avg Popularity"), use_container_width=True)
            st.markdown("**13. Rank Distribution (%)**")
            st.dataframe(metrics["rank_distribution"].rename("% of Songs"), use_container_width=True)
        with c2:
            st.markdown("**11. Average Popularity by Duration Bucket**")
            st.dataframe(metrics["pop_by_duration_bucket"].rename("Avg Popularity"), use_container_width=True)
            st.markdown("**12. Hit Probability by Duration Bucket**")
            st.dataframe(metrics["hit_prob_by_duration"].rename("Hit Probability %"), use_container_width=True)

    # ---------------------------------------------------------------------------------
    # TAB 6 — EXECUTIVE RECOMMENDATIONS
    # ---------------------------------------------------------------------------------
    with tabs[6]:
        section("🧭 Executive Recommendations", "Data-driven guidance generated from the computed BI metrics")
        recommendations = generate_recommendations(filtered_df, metrics)
        for title, body in recommendations:
            st.markdown(
                f'<div class="rec-card"><div class="rec-title">🔹 {title}</div>'
                f'<div class="rec-body">{body}</div></div>', unsafe_allow_html=True,
            )

    # ---------------------------------------------------------------------------------
    # TAB 7 — EXPORT
    # ---------------------------------------------------------------------------------
    with tabs[7]:
        section("📤 Export Center", "Download the filtered dataset or a full executive summary report")

        csv_bytes = filtered_df.drop(columns=["artist_list"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Filtered Dataset (CSV)", data=csv_bytes,
            file_name="atlantic_uk_filtered.csv", mime="text/csv", use_container_width=True,
        )

        report_lines = [
            "ATLANTIC RECORDING CORPORATION",
            "UK Top 50 Playlist — Executive BI Report",
            "=" * 60,
            f"Filtered records: {len(filtered_df):,} | Full dataset: {len(df_full):,}",
            "",
            "EXECUTIVE AI SUMMARY",
            "-" * 60,
            decisions["executive_summary"],
            "",
            f"UK Market Health Score: {decisions['market_health']['score']:.1f}/100 ({decisions['market_health']['band']})",
            f"Market Competition Score: {decisions['market_competition']['score']:.1f}/100",
            f"Artist Opportunity Score: {decisions['artist_opportunity']['score']:.1f}/100 ({decisions['artist_opportunity']['band']})",
            f"Playlist Balance Score: {decisions['playlist_balance']['score']:.1f}/100",
            f"Predictive Engine Overall Confidence: {decisions['predictive_engine']['overall_confidence']:.1f}%",
            "",
            "KEY METRICS",
            "-" * 60,
        ]
        for label, value in metric_rows:
            report_lines.append(f"{label}: {value}")
        report_lines += ["", "SMART INSIGHTS", "-" * 60]
        for ins in insights:
            report_lines.append("- " + ins.replace("<b>", "").replace("</b>", ""))
        report_lines += ["", "EXECUTIVE RECOMMENDATIONS", "-" * 60]
        for title, body in recommendations:
            report_lines.append(f"[{title}] {body}")
        report_lines += ["", "STRATEGIC RECOMMENDATIONS (Executive Decision Center)", "-" * 60]
        for title, body in strategic_recs:
            report_lines.append(f"[{title}] {body}")
        report_lines += ["", "DECISION ALERTS", "-" * 60]
        for level, icon, title, body in decisions["alerts"]:
            report_lines.append(f"{icon} [{title}] {body}")

        report_text = "\n".join(report_lines)
        st.download_button(
            "📄 Download Executive Report (TXT)", data=report_text.encode("utf-8"),
            file_name="atlantic_uk_executive_report.txt", mime="text/plain", use_container_width=True,
        )

        with st.expander("Preview report"):
            st.text(report_text)

    # ---------------------------------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------------------------------
    st.markdown(
        f"""
        <div class="footer-box">
            United Kingdom Top 50 Playlist Market Structure Analysis &nbsp;|&nbsp;
            Atlantic Recording Corporation &nbsp;|&nbsp; Executive BI Dashboard &nbsp;|&nbsp;
            Built with Streamlit &amp; Plotly
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
