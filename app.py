from pathlib import Path
import re
import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
DRIVER_DIR = ROOT / "drivers"
LOGO_DIR = ROOT / "logos"

# Local assets are preferred so the dashboard does not depend on a portrait API.
DRIVER_FILES = {
    "alex albon": "alex.jpg", "fernando alonso": "alonso.jpg",
    "arvid lindblad": "arvid.webp", "valtteri bottas": "bottas.png",
    "carlos sainz": "carlos.webp", "charles leclerc": "charles.jpeg",
    "franco colapinto": "franco.jpeg", "gabriel bortoleto": "gabi.webp",
    "pierre gasly": "gasly.webp", "george russell": "george.jpg",
    "isack hadjar": "isack.webp", "kimi antonelli": "kimi.jpeg",
    "andrea kimi antonelli": "kimi.jpeg", "lance stroll": "lance.jpg",
    "lando norris": "lando.webp", "lewis hamilton": "lewis.webp",
    "liam lawson": "liam.webp", "max verstappen": "max.jpeg",
    "nico hulkenberg": "nico.jpg", "esteban ocon": "ocon.webp",
    "oliver bearman": "ollie.jpeg", "oscar piastri": "oscar.jpeg",
    "sergio perez": "sergio.webp",
}
TEAM_LOGOS = {
    "red bull": "redbull.png", "red bull racing": "redbull.png",
    "ferrari": "ferrari.jpeg", "mercedes": "mercedes.webp",
    "mclaren": "mclaren.jpg", "aston martin": "aston martin.png",
    "williams": "williams.png", "alpine": "alpine.jpg",
    "haas": "haas.jpg", "racing bulls": "racing bulls.png",
    "rb": "racing bulls.png", "audi": "audi.png",
    "cadillac": "Cadillac-Logo.png",
}

st.set_page_config(
    page_title="F1 Predictor | Austin GP 2026",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
:root { --red:#e10600; --bg:#080b0e; --panel:#0e1318; --line:#202932; --muted:#98a6b4; }
.stApp { background:var(--bg); color:#f3f5f7; font-family:'Inter',sans-serif; }
header[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:1700px; padding:1.25rem 1.5rem 2rem; }
section[data-testid="stSidebar"] {
    background:
        radial-gradient(ellipse at top left, rgba(225,6,0,.09), transparent 45%),
        linear-gradient(180deg, #080b0e 0%, #0c1117 55%, #10151b 100%);
    border-right: 1px solid #252d36;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.8rem;
}
section[data-testid="stSidebar"] .brand {
    font-size: 1.8rem;
    letter-spacing: -.035em;
    line-height: 1.05;
}
section[data-testid="stSidebar"] .sidebar-tagline {
    color: #82909e;
    font-size: .68rem;
    letter-spacing: .13em;
    line-height: 1.8;
    text-transform: uppercase;
    margin-top: .45rem;
}
section[data-testid="stSidebar"] .sidebar-section-label {
    color: #778492;
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin: .3rem 0 .6rem;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] > div[role="radiogroup"] {
    gap: .35rem;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: .58rem .65rem;
    transition: background .18s ease, border-color .18s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    background: #151d25;
    border-color: #29343f;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
    border-color: #65717e;
}
section[data-testid="stSidebar"] .sidebar-race-label {
    color: #ff3933;
    font-size: .67rem;
    font-weight: 800;
    letter-spacing: .2em;
    text-transform: uppercase;
    margin-bottom: .55rem;
}
section[data-testid="stSidebar"] .sidebar-race-title {
    color: #f4f6f8;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: .4rem;
}
section[data-testid="stSidebar"] .sidebar-race-meta {
    color: #9aa7b4;
    font-size: .78rem;
    line-height: 1.75;
}
section[data-testid="stSidebar"] .sidebar-project-note {
    color: #8794a1;
    font-size: .75rem;
    line-height: 1.65;
    padding: .8rem .85rem;
    border-left: 2px solid #e10600;
    background: linear-gradient(90deg, rgba(225,6,0,.07), transparent);
    border-radius: 0 6px 6px 0;
}
h1,h2,h3 { font-family:'Barlow Condensed',sans-serif !important; letter-spacing:.025em; }
h1 { font-size:3.2rem !important; font-weight:800 !important; line-height:.98 !important; }
h2 { font-size:1.9rem !important; }
.brand { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.75rem; line-height:1; }
.brand .red { color:var(--red); }
.kicker { color:#ff302b; font-size:.72rem; font-weight:800; letter-spacing:.2em; text-transform:uppercase; }
.muted { color:var(--muted); font-size:.86rem; line-height:1.55; }
.hero {
  min-height:235px; padding:1.8rem 2rem; border:1px solid #252c34; border-radius:14px;
  background:linear-gradient(90deg,rgba(8,11,14,.98) 0%,rgba(8,11,14,.90) 37%,rgba(8,11,14,.18) 100%),
  none;
  background-color:#10151b; margin-bottom:1rem; position:relative; overflow:hidden;
}
.hero h1 { margin:.45rem 0 .65rem; max-width:680px; }
.hero-meta { display:flex; gap:2rem; flex-wrap:wrap; color:#e5e9ed; font-size:.82rem; margin-top:1.1rem; }
.hero-meta span { color:var(--muted); }
.metric-card { background:linear-gradient(135deg,#121a21,#0b1015); border:1px solid #242e38; border-radius:12px; padding:1rem 1.15rem; min-height:105px; }
.metric-label { color:#aab4bf; font-size:.69rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; margin-bottom:.45rem; }
.metric-value { font-family:'Barlow Condensed',sans-serif; font-size:1.65rem; font-weight:700; line-height:1.1; }
.section-title { font-family:'Barlow Condensed',sans-serif; font-size:1.65rem; font-weight:800; text-transform:uppercase; margin:.2rem 0 .8rem; }
.section-title span { color:var(--red); }
.panel { background:linear-gradient(145deg,#0e141a,#090d11); border:1px solid #202a33; border-radius:12px; padding:1rem; }
.team-pill { display:inline-block; padding:3px 7px; border:1px solid #34404b; background:#182129; color:#e5eaf0; border-radius:4px; font-size:.68rem; white-space:nowrap; }
.driver-name { font-weight:700; font-size:.84rem; line-height:1.2; }
.driver-team { color:var(--muted); font-size:.7rem; margin-top:4px; }
.score-track { height:9px; width:100%; background:#1b252e; border-radius:2px; overflow:hidden; }
.score-fill { height:100%; background:linear-gradient(90deg,#ff5b5b,#e10600); border-radius:2px; }
.rank-chip { font-family:'Barlow Condensed',sans-serif; color:#ff4540; font-size:1.1rem; font-weight:800; background:#301214; padding:3px 8px; border-radius:5px; text-align:center; }
div[data-testid="stDataFrame"] { border:1px solid #202a33; border-radius:8px; }
.stTextInput input { background:#111820; border-color:#2b3540; }
.stButton>button,.stDownloadButton>button { border-radius:6px; border:1px solid #35414c; background:#121a21; }
hr { border-color:#202a33; }
footer { visibility:hidden; }

/* -------------------- Responsive / mobile styling -------------------- */
@media (max-width: 900px) {
    .block-container {
        padding: 1rem 1rem 1.5rem !important;
    }

    h1 {
        font-size: clamp(2.1rem, 7vw, 3rem) !important;
        line-height: 1 !important;
    }

    h2 {
        font-size: 1.55rem !important;
    }

    .hero {
        min-height: auto;
        padding: 1.25rem 1.15rem;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(8,11,14,.98), rgba(16,21,27,.96));
    }

    .hero-meta {
        gap: .8rem 1.1rem;
        font-size: .76rem;
        margin-top: .9rem;
    }

    .metric-card {
        padding: .85rem .9rem;
        min-height: 88px;
    }

    .metric-value {
        font-size: 1.35rem;
        overflow-wrap: anywhere;
    }

    .section-title {
        font-size: 1.45rem;
        margin-bottom: .65rem;
    }

    .team-pill {
        white-space: normal;
        overflow-wrap: anywhere;
        font-size: .64rem;
    }

    .stButton > button,
    .stDownloadButton > button {
        min-height: 42px;
        width: 100%;
    }

    div[data-testid="stDataFrame"] {
        overflow-x: auto;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding: .7rem .65rem 1.1rem !important;
    }

    .hero {
        padding: 1rem .9rem;
        margin-bottom: .65rem;
    }

    .hero .kicker {
        font-size: .62rem;
        letter-spacing: .14em;
    }

    .hero h1 {
        font-size: clamp(1.9rem, 9vw, 2.5rem) !important;
        line-height: .98 !important;
    }

    .hero-meta {
        display: grid;
        grid-template-columns: 1fr;
        gap: .55rem;
        font-size: .75rem;
        margin-top: .85rem;
    }

    .metric-card {
        padding: .75rem .8rem;
        min-height: 0;
        margin-bottom: .2rem;
    }

    .metric-label {
        font-size: .62rem;
        letter-spacing: .06em;
    }

    .metric-value {
        font-size: 1.3rem;
    }

    .section-title {
        font-size: 1.35rem;
        line-height: 1.1;
    }

    .driver-name {
        font-size: .78rem;
        overflow-wrap: anywhere;
    }

    /* Compact the six-column leaderboard rows for narrow phone screens.
       Driver photo, rank and name remain visible; team and score details
       are available in the contender cards and score-distribution chart. */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) {
        gap: .3rem !important;
        align-items: center;
    }

    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) > div[data-testid="column"]:nth-child(1) {
        flex: 0 0 38px !important;
        min-width: 38px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) > div[data-testid="column"]:nth-child(2) {
        flex: 0 0 18px !important;
        min-width: 18px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) > div[data-testid="column"]:nth-child(3) {
        flex: 1 1 125px !important;
        min-width: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) > div[data-testid="column"]:nth-child(4),
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) > div[data-testid="column"]:nth-child(5),
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(6)) > div[data-testid="column"]:nth-child(6) {
        display: none !important;
    }

    /* Keep top contender cards readable without forcing oversized images. */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2)) {
        gap: .6rem;
    }

    section[data-testid="stSidebar"] .brand {
        font-size: 1.55rem;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    .stTextInput input {
        font-size: 16px !important;
    }

    footer {
        visibility: hidden;
    }
}

</style>
""", unsafe_allow_html=True)



def display_local_image(path: Path | None, width):
    """Display local images safely; return False instead of crashing on unsupported codecs."""
    if path is None or not path.is_file():
        return False
    try:
        with Image.open(path) as source:
            source.load()
            # Normalize to common formats Streamlit can reliably serialize.
            image = source.convert("RGBA" if "A" in source.getbands() else "RGB")
            st.image(image, width=width)
        return True
    except (OSError, ValueError, UnidentifiedImageError, RuntimeError) as exc:
        st.caption(f"Image unavailable: {path.name}")
        return False


def load_csv(filename):
    path = OUT / filename
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        st.warning(f"Could not read {filename}: {exc}")
        return None


def find_asset(folder: Path, filename: str | None) -> Path | None:
    """Find a local asset without relying on case-sensitive filesystem matching."""
    if not filename or not folder.is_dir():
        return None
    direct = folder / filename
    if direct.is_file():
        return direct
    wanted = filename.casefold()
    for candidate in folder.iterdir():
        if candidate.is_file() and candidate.name.casefold() == wanted:
            return candidate
    return None


def driver_photo(name: str) -> Path | None:
    normalized = re.sub(r"\s+", " ", str(name).strip().lower())
    filename = DRIVER_FILES.get(normalized)
    if filename is None:
        # Controlled aliases for names that can vary in prediction data.
        aliases = {
            "alexander albon": "alex.jpg", "nico hülkenberg": "nico.jpg",
            "sergio perez": "sergio.webp", "oliver bearman": "ollie.jpeg",
            "gabriel bortoleto": "gabi.webp",
        }
        filename = aliases.get(normalized)
    return find_asset(DRIVER_DIR, filename)


def team_logo(team_name: str) -> Path | None:
    normalized = str(team_name).strip().lower()
    aliases = {
        "red bull racing": "redbull.png", "red bull": "redbull.png",
        "scuderia ferrari": "ferrari.jpeg", "mercedes-amg": "mercedes.webp",
        "visa cash app rb": "racing bulls.png", "rb f1 team": "racing bulls.png",
        "aston martin aramco": "aston martin.png",
    }
    filename = aliases.get(normalized, TEAM_LOGOS.get(normalized))
    if filename is None:
        for key, candidate in TEAM_LOGOS.items():
            if key in normalized:
                filename = candidate
                break
    return find_asset(LOGO_DIR, filename)


TEAM_META = {
    "Red Bull": "#3671C6", "Ferrari": "#E8002D", "Mercedes": "#27F4D2",
    "McLaren": "#FF8000", "Aston Martin": "#229971", "Williams": "#64C4FF",
    "Alpine": "#FF87BC", "Haas": "#B6BABD", "Racing Bulls": "#6692FF",
    "RB": "#6692FF", "Audi": "#E0002B", "Cadillac": "#D6D6D6",
}


def team_style(name):
    normalized = str(name).lower()
    for key, colour in TEAM_META.items():
        if key.lower() in normalized:
            return colour
    return "#e10600"


def initials(name):
    return "".join(part[0] for part in str(name).split()[:2]).upper()


def metrics_by_race(df, score_col, baseline_col=None, lower=False):
    required = {"season", "round", "driver_id", "WonRace", score_col}
    if df is None or not required.issubset(df.columns):
        return None, None
    rows = []
    for (season, rnd), race in df.groupby(["season", "round"]):
        race = race.dropna(subset=[score_col]).copy()
        wins = pd.to_numeric(race["WonRace"], errors="coerce")
        if race.empty or wins.sum() != 1:
            continue
        race["rank"] = pd.to_numeric(race[score_col], errors="coerce").rank(ascending=False, method="min")
        winner_rank = float(race.loc[wins == 1, "rank"].iloc[0])
        row = {"Season": int(season), "Round": int(rnd), "Top 1": int(winner_rank == 1), "Top 3": int(winner_rank <= 3)}
        if baseline_col and baseline_col in race:
            vals = pd.to_numeric(race[baseline_col], errors="coerce")
            if vals.notna().any():
                race["baseline_rank"] = vals.rank(ascending=lower, method="min")
                br = float(race.loc[wins == 1, "baseline_rank"].iloc[0])
                row["Baseline top 1"] = int(br == 1)
                row["Baseline top 3"] = int(br <= 3)
        rows.append(row)
    if not rows:
        return None, None
    results = pd.DataFrame(rows)
    return {
        "races": len(results),
        "top1": results["Top 1"].mean(),
        "top3": results["Top 3"].mean(),
        "base1": results["Baseline top 1"].mean() if "Baseline top 1" in results else None,
        "base3": results["Baseline top 3"].mean() if "Baseline top 3" in results else None,
    }, results


pred = load_csv("austin_gp_2026_prequal_prediction.csv")
pre_oof = load_csv("prequal_random_forest_comparison_oof.csv")
post_oof = load_csv("postqual_random_forest_comparison_oof.csv")
pre_imp = load_csv("prequal_feature_importance.csv")
post_imp = load_csv("postqual_feature_importance.csv")

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown(
        '<div class="brand">🏎️ F1 <span class="red">PREDICTOR</span></div>'
        '<div class="sidebar-tagline">Race data · Machine learning</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        '<div class="sidebar-section-label">Workspace</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        ["Race Predictions", "Model Performance", "Feature Insights"],
        label_visibility="collapsed",
        key="workspace_navigation",
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-race-label">● &nbsp; Round 19 / 2026</div>'
        '<div class="sidebar-race-title">United States Grand Prix</div>'
        '<div class="sidebar-race-meta">'
        'Circuit of The Americas<br>'
        'Austin, Texas<br>'
        'Race weekend · October 25'
        '</div>',
        unsafe_allow_html=True,
    )

    circuit_poster = ROOT / "1.webp"
    if circuit_poster.exists():
        display_local_image(circuit_poster, width="stretch")

    st.markdown(
        '<div class="sidebar-project-note">'
        'A data-driven driver ranking built from historical race data, '
        'recent form and machine learning.'
        '</div>',
        unsafe_allow_html=True,
    )


# -------------------- Race prediction page --------------------
if page == "Race Predictions":
    hero_text, hero_image = st.columns([1.15, 1], gap="small", vertical_alignment="center")
    with hero_text:
        st.markdown("""
        <div class="hero">
          <div class="kicker">2026 SEASON / AUSTIN</div>
          <h1>UNITED STATES<br><span style="color:#e10600">GRAND PRIX</span></h1>
          <div class="muted">A data-driven driver ranking built from recent form, constructor performance,
          championship standings and circuit history.</div>
          <div class="hero-meta"><div>▦ &nbsp; Round 19<br><span>Oct 25, 2026</span></div>
          <div>◉ &nbsp; Circuit of The Americas<br><span>Austin, Texas</span></div>
          <div>⚑ &nbsp; Prediction stage<br><span>Pre-qualifying</span></div></div>
        </div>
        """, unsafe_allow_html=True)
    with hero_image:
        car_image = ROOT / "3.jpg"
        if car_image.exists():
            display_local_image(car_image, width="stretch")
        else:
            st.caption("Add 3.jpg to the project folder to show the local F1 car banner.")

    if pred is None or pred.empty:
        st.error("Prediction file not found: outputs/austin_gp_2026_prequal_prediction.csv")
    elif not {"predicted_rank", "driver_name", "constructor", "normalized_model_score"}.issubset(pred.columns):
        st.error("Prediction CSV is missing required columns.")
    else:
        pred = pred.copy()
        pred["predicted_rank"] = pd.to_numeric(pred["predicted_rank"], errors="coerce")
        pred["normalized_model_score"] = pd.to_numeric(pred["normalized_model_score"], errors="coerce")
        pred = pred.sort_values("predicted_rank").reset_index(drop=True)
        first = pred.iloc[0]

        a, b, c = st.columns(3)
        with a:
            st.markdown(f'<div class="metric-card"><div class="metric-label">🏆 &nbsp; MODEL TOP PICK</div><div class="metric-value">{first["driver_name"]}</div><div class="muted">{first["constructor"]}</div></div>', unsafe_allow_html=True)
        with b:
            st.markdown(f'<div class="metric-card"><div class="metric-label">👥 &nbsp; DRIVERS RANKED</div><div class="metric-value">{len(pred)}</div><div class="muted">Full prediction field</div></div>', unsafe_allow_html=True)
        with c:
            st.markdown('<div class="metric-card"><div class="metric-label">▰ &nbsp; PREDICTION STAGE</div><div class="metric-value">PRE-QUALIFYING</div><div class="muted">Qualifying data excluded</div></div>', unsafe_allow_html=True)

        left, right = st.columns([1.7, 1])
        with left:
            st.markdown('<div class="section-title">DRIVER <span>LEADERBOARD</span></div>', unsafe_allow_html=True)
            search = st.text_input("Search", placeholder="⌕  Search driver or team...", label_visibility="collapsed")
            view = pred.copy()
            if search:
                mask = view["driver_name"].astype(str).str.contains(search, case=False, na=False) | view["constructor"].astype(str).str.contains(search, case=False, na=False)
                view = view[mask]

            # Local driver portraits and constructor logos are displayed in each row.
            for _, row in view.iterrows():
                driver_name = str(row["driver_name"])
                team_name = str(row["constructor"])
                photo = driver_photo(driver_name)
                logo = team_logo(team_name)
                accent = team_style(team_name)
                score = float(row["normalized_model_score"]) if pd.notna(row["normalized_model_score"]) else 0.0
                photo_col, rank_col, name_col, team_col, bar_col, pct_col = st.columns([0.42, 0.22, 1.2, 1.15, 1.25, 0.42], vertical_alignment="center")
                with photo_col:
                    if photo:
                        display_local_image(photo, width=42)
                    else:
                        st.markdown(f'<div style="width:38px;height:38px;border-radius:7px;background:#1b242c;border:1px solid #2d3944;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.75rem">{initials(driver_name)}</div>', unsafe_allow_html=True)
                with rank_col:
                    st.markdown(f'<span style="color:#aeb9c4;font-size:.85rem">{int(row["predicted_rank"])}</span>', unsafe_allow_html=True)
                with name_col:
                    st.markdown(f'<div class="driver-name">{driver_name}</div>', unsafe_allow_html=True)
                with team_col:
                    logo_col, label_col = st.columns([0.42, 1.6], vertical_alignment="center")
                    with logo_col:
                        if logo:
                            display_local_image(logo, width=28)
                    with label_col:
                        st.markdown(f'<span class="team-pill" style="border-left:3px solid {accent}">{team_name}</span>', unsafe_allow_html=True)
                with bar_col:
                    st.markdown(f'<div class="score-track"><div class="score-fill" style="width:{max(0,min(100,score*100)):.2f}%"></div></div>', unsafe_allow_html=True)
                with pct_col:
                    st.markdown(f'<div style="font-size:.78rem;text-align:right">{score:.1%}</div>', unsafe_allow_html=True)
                st.markdown('<div style="height:1px;background:#172029;margin:3px 0 5px"></div>', unsafe_allow_html=True)

            st.download_button("↓  Download full ranking (CSV)", pred.to_csv(index=False).encode(), "f1_predictor_austin_2026.csv", "text/csv")

        with right:
            st.markdown('<div class="section-title">TOP <span>CONTENDERS</span></div>', unsafe_allow_html=True)
            for _, row in pred.head(3).iterrows():
                driver_name = str(row["driver_name"])
                team_name = str(row["constructor"])
                photo = driver_photo(driver_name)
                logo = team_logo(team_name)
                accent = team_style(team_name)
                score = float(row["normalized_model_score"])
                pic_col, info_col = st.columns([0.9, 1.65], vertical_alignment="center")
                with pic_col:
                    if photo:
                        display_local_image(photo, width=105)
                    else:
                        st.markdown(f'<div style="height:95px;border-radius:8px;background:#1b242c;border:1px solid #2d3944;display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:800">{initials(driver_name)}</div>', unsafe_allow_html=True)
                with info_col:
                    st.markdown(f'<div style="border-left:3px solid {accent};padding-left:10px"><div class="metric-label">RANK {int(row["predicted_rank"])}</div><div style="font-weight:800;font-size:.95rem">{driver_name}</div><div style="margin:6px 0"><span class="team-pill">{team_name}</span></div><div class="muted">{score:.2%} normalized score</div></div>', unsafe_allow_html=True)
                    if logo:
                        display_local_image(logo, width=42)
                st.markdown('<div style="height:1px;background:#202a33;margin:8px 0"></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">SCORE <span>DISTRIBUTION</span></div>', unsafe_allow_html=True)
            chart = pred[["driver_name", "normalized_model_score"]].copy()
            chart["normalized_model_score"] *= 100
            st.bar_chart(chart.set_index("driver_name"), height=240)
            st.markdown('<div class="section-title">CIRCUIT <span>PROFILE</span></div>', unsafe_allow_html=True)
            circuit_map = ROOT / "2.webp"
            if circuit_map.exists():
                display_local_image(circuit_map, width="stretch")
                st.caption("Circuit of The Americas · Austin, Texas")
            st.caption("Scores are normalized ranking scores, not calibrated win probabilities.")

elif page == "Model Performance":
    st.markdown('<div class="kicker">BACKTESTING</div>', unsafe_allow_html=True)
    st.title("MODEL PERFORMANCE")
    st.markdown('<div class="muted">Historical out-of-fold evaluation against a simple ranking baseline.</div>', unsafe_allow_html=True)
    stage = st.segmented_control("Prediction stage", ["Pre-qualifying", "Post-qualifying"], default="Pre-qualifying")
    if stage == "Post-qualifying":
        data, baselines = post_oof, {"Qualifying position": "qualifying_position"}
    else:
        data, baselines = pre_oof, {"Championship points": "driver_championship_points_pre", "Recent points": "driver_points_last5", "Recent average finish": "driver_avg_finish_last5"}
    baseline_name = st.selectbox("Baseline", list(baselines))
    baseline_col = baselines[baseline_name]
    summary, races = metrics_by_race(data, "model_score", baseline_col, baseline_col in {"qualifying_position", "driver_avg_finish_last5"})
    if summary is None:
        st.warning("Validation data unavailable. Check the OOF CSV files in outputs/.")
    else:
        x, y, z = st.columns(3)
        x.metric("Races evaluated", summary["races"])
        y.metric("Top-1 accuracy", f'{summary["top1"]:.1%}')
        z.metric("Top-3 accuracy", f'{summary["top3"]:.1%}')
        if summary["base1"] is not None:
            compare = pd.DataFrame({"Top-1 accuracy": [summary["top1"], summary["base1"]], "Top-3 accuracy": [summary["top3"], summary["base3"]]}, index=["Random Forest", baseline_name])
            st.markdown('<div class="section-title">MODEL <span>VS BASELINE</span></div>', unsafe_allow_html=True)
            st.bar_chart(compare, y=["Top-1 accuracy", "Top-3 accuracy"])
        with st.expander("View race-by-race results"):
            st.dataframe(races, hide_index=True, width="stretch")
        st.caption("Historical validation is not a guarantee of future race outcomes.")

else:
    st.markdown('<div class="kicker">MODEL INTERPRETATION</div>', unsafe_allow_html=True)
    st.title("FEATURE INSIGHTS")
    st.markdown('<div class="muted">Explore which inputs contributed most to the Random Forest model.</div>', unsafe_allow_html=True)
    stage = st.segmented_control("Model stage", ["Pre-qualifying", "Post-qualifying"], default="Pre-qualifying")
    importance = post_imp if stage == "Post-qualifying" else pre_imp
    if importance is None or importance.empty:
        st.warning("Feature-importance CSV not found in outputs/.")
    else:
        feature_col = "encoded_feature" if "encoded_feature" in importance.columns else importance.columns[0]
        value_col = "importance" if "importance" in importance.columns else importance.columns[1]
        n = st.slider("Features to display", 5, min(20, len(importance)), min(10, len(importance)))
        chart = importance[[feature_col, value_col]].head(n).copy()
        chart[feature_col] = chart[feature_col].astype(str).str.replace(r"^(numeric__|categorical__)", "", regex=True)
        st.bar_chart(chart.sort_values(value_col).set_index(feature_col), horizontal=True)
        with st.expander("View importance values"):
            st.dataframe(chart.sort_values(value_col, ascending=False), hide_index=True, width="stretch")
        st.caption("Feature importance describes model behavior; it does not establish causation.")

st.divider()
st.caption("F1 PREDICTOR · FORMULA 1 ANALYTICS · PYTHON + SCIKIT-LEARN + STREAMLIT")
