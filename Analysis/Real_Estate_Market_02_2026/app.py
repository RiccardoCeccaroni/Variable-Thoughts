"""
Italian Real Estate Market Dashboard
Rent vs. Buy analysis across 104 Italian provinces
Data: ~190K sale listings + ~67K rental listings (Feb 2026)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# ─── Page Config ───
st.set_page_config(
    page_title="Italian Real Estate | Rent vs Buy Analysis",
    page_icon="https://em-content.zobj.net/source/twitter/408/house_1f3e0.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Professional CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #f8f9fb;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
        color: #1a1f36;
    }

    /* Header banner */
    .dash-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2.5rem 2.5rem 2.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #f1f5f9;
        border-bottom: 3px solid #3b82f6;
    }
    .dash-header h1 {
        font-size: 2rem;
        font-weight: 700 !important;
        margin: 0 0 0.25rem;
        color: #ffffff !important;
        letter-spacing: -0.03em;
    }
    .dash-header .subtitle {
        font-size: 1rem;
        color: #94a3b8;
        font-weight: 400;
        margin: 0;
    }

    /* KPI cards */
    .kpi-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .kpi-card {
        flex: 1;
        min-width: 150px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        transition: box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .kpi-card .kpi-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .kpi-card .kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-card .kpi-sub {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.15rem;
        font-weight: 400;
    }
    .kpi-value.positive { color: #059669; }
    .kpi-value.negative { color: #dc2626; }
    .kpi-value.neutral  { color: #0f172a; }

    /* Section headers */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 1.5rem 0 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #475569;
        font-weight: 600;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 0.6rem 1.2rem;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #1e293b !important;
        border-bottom: 2px solid #3b82f6;
    }

    /* Dataframes */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Plotly template ───
CHART_LAYOUT = dict(
    font=dict(family="Inter, sans-serif", size=12, color="#334155"),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    title_font=dict(size=14, color="#1e293b", family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=45, b=40),
    coloraxis_showscale=False,
    xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
    yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
)

BUY_COLOR = "#059669"
RENT_COLOR = "#dc2626"
COLOR_MAP = {"BUY": BUY_COLOR, "RENT": RENT_COLOR}
ACCENT = "#3b82f6"


# ═══════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════

SCENARIO_PCT_MAP = {
    "3.5% · E20/D80 (Best)": "pct_buy_35_e20d80",
    "3.5% · E30/D70": "pct_buy_35_e30d70",
    "4.0% · E20/D80": "pct_buy_40_e20d80",
    "4.0% · E30/D70": "pct_buy_40_e30d70",
    "4.5% · E20/D80": "pct_buy_45_e20d80",
    "4.5% · E30/D70": "pct_buy_45_e30d70",
    "5.0% · E20/D80": "pct_buy_50_e20d80",
    "5.0% · E30/D70 (Worst)": "pct_buy_50_e30d70",
}
SCENARIO_RE_MAP = {
    "3.5% · E20/D80 (Best)": "Avg RE/sqm 3.5% E20/D80",
    "3.5% · E30/D70": "Avg RE/sqm 3.5% E30/D70",
    "4.0% · E20/D80": "Avg RE/sqm 4.0% E20/D80",
    "4.0% · E30/D70": "Avg RE/sqm 4.0% E30/D70",
    "4.5% · E20/D80": "Avg RE/sqm 4.5% E20/D80",
    "4.5% · E30/D70": "Avg RE/sqm 4.5% E30/D70",
    "5.0% · E20/D80": "Avg RE/sqm 5.0% E20/D80",
    "5.0% · E30/D70 (Worst)": "Avg RE/sqm 5.0% E30/D70",
}

COORDS = {
    "AG":[37.31,13.58],"AL":[44.91,8.62],"AN":[43.62,13.52],"AO":[45.74,7.32],
    "AP":[42.85,13.57],"AR":[43.46,11.88],"AT":[44.90,8.21],"AV":[40.91,14.79],
    "BA":[41.12,16.87],"BG":[45.70,9.68],"BI":[45.56,8.05],"BL":[46.14,12.22],
    "BN":[41.13,14.78],"BO":[44.49,11.34],"BR":[40.63,17.94],"BS":[45.54,10.21],
    "BT":[41.23,16.30],"CA":[39.22,9.12],"CB":[41.56,14.66],"CE":[41.07,14.33],
    "CH":[42.35,14.17],"CL":[37.49,14.06],"CN":[44.39,7.55],"CO":[45.81,9.09],
    "CR":[45.14,10.02],"CS":[39.30,16.25],"CT":[37.51,15.08],"CZ":[38.90,16.59],
    "EN":[37.57,14.28],"FC":[44.22,12.04],"FE":[44.84,11.62],"FG":[41.46,15.54],
    "FI":[43.77,11.26],"FM":[43.16,13.72],"FR":[41.64,13.35],"GE":[44.41,8.95],
    "GO":[45.94,13.62],"GR":[42.76,11.11],"IM":[43.89,8.03],"IS":[41.59,14.24],
    "KR":[39.08,17.13],"LE":[40.35,18.18],"LI":[43.55,10.31],"LO":[45.31,9.50],
    "LT":[41.47,12.90],"LU":[43.84,10.50],"MB":[45.58,9.27],"MC":[43.30,13.45],
    "ME":[38.19,15.55],"MI":[45.46,9.19],"MN":[45.16,10.79],"MO":[44.65,10.93],
    "MS":[44.03,10.14],"MT":[40.67,16.60],"NA":[40.85,14.27],"NO":[45.45,8.62],"NU":[40.32,9.33],
    "OR":[39.91,8.59],"PA":[38.12,13.36],"PC":[45.05,9.69],"PD":[45.41,11.88],
    "PE":[42.46,14.21],"PG":[43.11,12.39],"PI":[43.72,10.40],"PN":[45.96,12.66],
    "PO":[43.88,11.10],"PR":[44.80,10.33],"PT":[43.93,10.92],"PU":[43.91,12.91],
    "PV":[45.18,9.16],"PZ":[40.64,15.80],"RA":[44.42,12.20],"RC":[38.11,15.65],
    "RE":[44.70,10.63],"RG":[36.93,14.73],"RI":[42.40,12.86],"RM":[41.90,12.50],
    "RN":[44.06,12.57],"RO":[45.07,11.79],"SA":[40.68,14.77],"SI":[43.32,11.33],
    "SO":[46.17,9.88],"SP":[44.10,9.82],"SR":[37.08,15.29],"SS":[40.73,8.56],
    "SU":[39.50,8.86],"SV":[44.31,8.48],"TA":[40.48,17.23],"TE":[42.66,13.70],
    "TN":[46.07,11.12],"TO":[45.07,7.69],"TP":[38.02,12.51],"TR":[42.56,12.64],
    "TS":[45.65,13.78],"TV":[45.67,12.24],"UD":[46.07,13.23],"VA":[45.82,8.83],
    "VB":[46.14,8.27],"VC":[45.33,8.42],"VE":[45.44,12.32],"VI":[45.55,11.54],
    "VR":[45.44,10.99],"VT":[42.42,12.11],"VV":[38.68,16.10],
}

PROVINCE_NAMES = {
    "AG":"Agrigento","AL":"Alessandria","AN":"Ancona","AO":"Aosta",
    "AP":"Ascoli Piceno","AR":"Arezzo","AT":"Asti","AV":"Avellino",
    "BA":"Bari","BG":"Bergamo","BI":"Biella","BL":"Belluno",
    "BN":"Benevento","BO":"Bologna","BR":"Brindisi","BS":"Brescia",
    "BT":"Barletta-Andria-Trani","CA":"Cagliari","CB":"Campobasso",
    "CE":"Caserta","CH":"Chieti","CL":"Caltanissetta","CN":"Cuneo",
    "CO":"Como","CR":"Cremona","CS":"Cosenza","CT":"Catania",
    "CZ":"Catanzaro","EN":"Enna","FC":"Forli-Cesena","FE":"Ferrara",
    "FG":"Foggia","FI":"Firenze","FM":"Fermo","FR":"Frosinone",
    "GE":"Genova","GO":"Gorizia","GR":"Grosseto","IM":"Imperia",
    "IS":"Isernia","KR":"Crotone","LE":"Lecce","LI":"Livorno",
    "LO":"Lodi","LT":"Latina","LU":"Lucca","MB":"Monza e Brianza",
    "MC":"Macerata","ME":"Messina","MI":"Milano","MN":"Mantova",
    "MO":"Modena","MS":"Massa-Carrara","MT":"Matera","NA":"Napoli","NO":"Novara",
    "NU":"Nuoro","OR":"Oristano","PA":"Palermo","PC":"Piacenza",
    "PD":"Padova","PE":"Pescara","PG":"Perugia","PI":"Pisa",
    "PN":"Pordenone","PO":"Prato","PR":"Parma","PT":"Pistoia",
    "PU":"Pesaro e Urbino","PV":"Pavia","PZ":"Potenza","RA":"Ravenna",
    "RC":"Reggio Calabria","RE":"Reggio Emilia","RG":"Ragusa",
    "RI":"Rieti","RM":"Roma","RN":"Rimini","RO":"Rovigo",
    "SA":"Salerno","SI":"Siena","SO":"Sondrio","SP":"La Spezia",
    "SR":"Siracusa","SS":"Sassari","SU":"Sud Sardegna","SV":"Savona",
    "TA":"Taranto","TE":"Teramo","TN":"Trento","TO":"Torino",
    "TP":"Trapani","TR":"Terni","TS":"Trieste","TV":"Treviso",
    "UD":"Udine","VA":"Varese","VB":"Verbano-Cusio-Ossola",
    "VC":"Vercelli","VE":"Venezia","VI":"Vicenza","VR":"Verona",
    "VT":"Viterbo","VV":"Vibo Valentia",
}


# ═══════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════

@st.cache_data
def load_all_data(file_path):
    engine = "pyxlsb" if file_path.endswith(".xlsb") else "openpyxl"
    xls = pd.ExcelFile(file_path, engine=engine)

    # Province rent vs buy per sqm
    prov_sqm = pd.read_excel(xls, sheet_name="Prov Rent vs Buy (per sqm)", keep_default_na=False)
    prov_sqm.rename(columns={"Provincia": "Sigla"}, inplace=True)
    for c in prov_sqm.columns:
        if c != "Sigla":
            prov_sqm[c] = pd.to_numeric(prov_sqm[c], errors="coerce")

    # Province % distribution
    raw_pct = pd.read_excel(xls, sheet_name="Prov % Distribution", keep_default_na=False)
    prov_pct = raw_pct.iloc[1:].reset_index(drop=True)
    prov_pct.columns = range(len(raw_pct.columns))
    prov_pct_clean = pd.DataFrame({
        "Sigla": prov_pct[0],
        "pct_buy_35_e20d80": pd.to_numeric(prov_pct[2], errors="coerce"),
        "pct_buy_35_e30d70": pd.to_numeric(prov_pct[4], errors="coerce"),
        "pct_buy_40_e20d80": pd.to_numeric(prov_pct[6], errors="coerce"),
        "pct_buy_40_e30d70": pd.to_numeric(prov_pct[8], errors="coerce"),
        "pct_buy_45_e20d80": pd.to_numeric(prov_pct[10], errors="coerce"),
        "pct_buy_45_e30d70": pd.to_numeric(prov_pct[12], errors="coerce"),
        "pct_buy_50_e20d80": pd.to_numeric(prov_pct[14], errors="coerce"),
        "pct_buy_50_e30d70": pd.to_numeric(prov_pct[16], errors="coerce"),
        "internet_rent_sqm": pd.to_numeric(prov_pct[17], errors="coerce"),
    })

    # Province rent vs sale summary
    prov_summary = pd.read_excel(xls, sheet_name="Prov Rent vs Sale Summary", keep_default_na=False)
    prov_summary["Sigla"] = prov_summary["Provincia"].str.extract(r'\((\w+)\)')
    for c in prov_summary.columns:
        if c not in ("Provincia", "Sigla"):
            prov_summary[c] = pd.to_numeric(prov_summary[c], errors="coerce")

    # Province+Size: rent vs sale
    size_summary = pd.read_excel(xls, sheet_name="Rent vs Sale Summary", keep_default_na=False)
    size_summary["Sigla"] = size_summary["Provincia"].str.extract(r'\((\w+)\)')
    size_summary = size_summary.dropna(subset=["Size Category"])
    for c in size_summary.columns:
        if c not in ("Provincia", "Sigla", "Size Category", "Sqm Range (Percentile Cutoffs)"):
            size_summary[c] = pd.to_numeric(size_summary[c], errors="coerce")

    # Province+Size: rent vs buy per sqm
    size_sqm = pd.read_excel(xls, sheet_name="Rent vs Buy (per sqm)", keep_default_na=False)
    for c in size_sqm.columns:
        if c != "Category":
            size_sqm[c] = pd.to_numeric(size_sqm[c], errors="coerce")
    size_sqm["Sigla"] = size_sqm["Category"].str.split("_").str[0]
    size_sqm["Size"] = size_sqm["Category"].str.split("_").str[1]

    # Province+Size: % distribution
    raw_sz_pct = pd.read_excel(xls, sheet_name="Rent vs Buy % Distribution", keep_default_na=False)
    sz_pct = raw_sz_pct.iloc[1:].reset_index(drop=True)
    sz_pct.columns = range(len(raw_sz_pct.columns))
    size_pct_clean = pd.DataFrame({
        "Category": sz_pct[0],
        "pct_buy_35_e20d80": pd.to_numeric(sz_pct[2], errors="coerce"),
        "pct_buy_35_e30d70": pd.to_numeric(sz_pct[4], errors="coerce"),
        "pct_buy_40_e20d80": pd.to_numeric(sz_pct[6], errors="coerce"),
        "pct_buy_40_e30d70": pd.to_numeric(sz_pct[8], errors="coerce"),
        "pct_buy_45_e20d80": pd.to_numeric(sz_pct[10], errors="coerce"),
        "pct_buy_45_e30d70": pd.to_numeric(sz_pct[12], errors="coerce"),
        "pct_buy_50_e20d80": pd.to_numeric(sz_pct[14], errors="coerce"),
        "pct_buy_50_e30d70": pd.to_numeric(sz_pct[16], errors="coerce"),
        "internet_rent_sqm": pd.to_numeric(sz_pct[17], errors="coerce"),
    })
    size_pct_clean["Sigla"] = size_pct_clean["Category"].str.split("_").str[0]
    size_pct_clean["Size"] = size_pct_clean["Category"].str.split("_").str[1]

    # Province -> Region mapping
    sell_map = pd.read_excel(xls, sheet_name="Selling Listings", usecols=["Provincia", "Regione"], keep_default_na=False)
    prov_region = sell_map.drop_duplicates().rename(columns={"Provincia": "Sigla"})

    # Region-level
    region_summary = pd.read_excel(xls, sheet_name="Region vs Sale Summary", keep_default_na=False)
    for c in region_summary.columns:
        if c != "Regione":
            region_summary[c] = pd.to_numeric(region_summary[c], errors="coerce")

    return {
        "prov_sqm": prov_sqm, "prov_pct": prov_pct_clean,
        "prov_summary": prov_summary, "size_summary": size_summary,
        "size_sqm": size_sqm, "size_pct": size_pct_clean,
        "prov_region": prov_region, "region_summary": region_summary,
    }


# ═══════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(DATA_DIR, "ComparisonSaleRent.xlsx")

if os.path.exists(DEFAULT_FILE):
    data_path = DEFAULT_FILE
else:
    st.error("No data file found. Place ComparisonSaleRent.xlsx in the app directory.")
    st.stop()

try:
    data = load_all_data(data_path)
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

prov_sqm = data["prov_sqm"]
prov_pct = data["prov_pct"]
prov_summary = data["prov_summary"]
size_pct = data["size_pct"]
size_sqm = data["size_sqm"]
size_summary = data["size_summary"]
prov_region = data["prov_region"]

# Enrich with region + name
for df in [prov_sqm, prov_pct, prov_summary]:
    if "Regione" not in df.columns:
        merged = df.merge(prov_region, on="Sigla", how="left")
        df["Regione"] = merged["Regione"]
    df["Province"] = df["Sigla"].map(PROVINCE_NAMES)


# ═══════════════════════════════════════════════════
# SIDEBAR FILTERS
# ═══════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<div style='padding:0.5rem 0 0.8rem;'>"
        "<span style='font-weight:700; font-size:1.7rem; color:#0f172a;'>Real Estate Analysis</span>"
        "<br><span style='font-size:1.2rem; color:#94a3b8;'>Italian Market Dashboard</span>"
        "<br><span style='font-size:1rem; color:#64748b;'>Riccardo Ceccaroni</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### Scenario")
    scenario_labels = list(SCENARIO_PCT_MAP.keys())
    selected_scenario = st.select_slider(
        "Mortgage scenario", options=scenario_labels, value=scenario_labels[2],
        label_visibility="collapsed",
    )
    st.caption(f"Selected: **{selected_scenario}**")
    st.markdown("---")
    st.markdown("### Filters")
    all_regions = sorted(prov_sqm["Regione"].dropna().unique())
    selected_regions = st.multiselect("Regions", all_regions, default=[], placeholder="All regions")
    selected_size = st.radio("Property size", ["All", "Small", "Medium", "Large"], horizontal=True)
    st.markdown("---")
    st.caption("~190K sale + ~67K rent listings | Feb 2026")
    st.caption("Source: immobiliare.it + idealista")


# ═══════════════════════════════════════════════════
# BUILD MAIN VIEW
# ═══════════════════════════════════════════════════

pct_col = SCENARIO_PCT_MAP[selected_scenario]
re_col = SCENARIO_RE_MAP[selected_scenario]

prov_view = prov_pct.copy()
prov_view["pct_buy"] = prov_view[pct_col]
prov_view["Verdict"] = np.where(prov_view["pct_buy"] >= 0.5, "BUY", "RENT")

prov_view = prov_view.merge(
    prov_sqm[["Sigla", "Avg Rent \u20ac/sqm/month", re_col, "Internet Rent \u20ac/sqm Feb 2026"]],
    on="Sigla", how="left")
prov_view = prov_view.merge(
    prov_summary[["Sigla", "Avg Rent \u20ac/month", "Avg Sale \u20ac", "Avg Sale \u20ac/sqm",
                   "N Rent", "N Sale", "Price-to-Rent Ratio"]],
    on="Sigla", how="left")
prov_view["Monthly_RE_sqm"] = prov_view[re_col]
prov_view["Savings_sqm"] = prov_view["Avg Rent \u20ac/sqm/month"] - prov_view["Monthly_RE_sqm"]
prov_view["lat"] = prov_view["Sigla"].map(lambda s: COORDS.get(s, [None, None])[0])
prov_view["lon"] = prov_view["Sigla"].map(lambda s: COORDS.get(s, [None, None])[1])

if selected_regions:
    prov_view = prov_view[prov_view["Regione"].isin(selected_regions)]


# ═══════════════════════════════════════════════════
# HEADER + KPIs
# ═══════════════════════════════════════════════════

n_buy = (prov_view["Verdict"] == "BUY").sum()
n_rent = (prov_view["Verdict"] == "RENT").sum()
n_total = len(prov_view)
avg_buy_pct = prov_view["pct_buy"].mean() * 100
avg_sale_sqm = prov_view["Avg Sale \u20ac/sqm"].mean()
avg_rent_sqm = prov_view["Avg Rent \u20ac/sqm/month"].mean()

st.markdown(f"""
<div class="dash-header">
    <h1>Italian Real Estate Market</h1>
    <p class="subtitle">Rent vs. Buy Analysis &nbsp;|&nbsp; {n_total} provinces &nbsp;|&nbsp; {selected_scenario}</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">Provinces favoring Buy</div>
        <div class="kpi-value positive">{n_buy}</div>
        <div class="kpi-sub">{n_buy/max(n_total,1)*100:.0f}% of total</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Provinces favoring Rent</div>
        <div class="kpi-value negative">{n_rent}</div>
        <div class="kpi-sub">{n_rent/max(n_total,1)*100:.0f}% of total</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Avg Buy-Win Rate</div>
        <div class="kpi-value neutral">{avg_buy_pct:.1f}%</div>
        <div class="kpi-sub">across all listings</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Avg Sale Price</div>
        <div class="kpi-value neutral">\u20ac{avg_sale_sqm:,.0f}/m\u00b2</div>
        <div class="kpi-sub">asking price</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Avg Monthly Rent</div>
        <div class="kpi-value neutral">\u20ac{avg_rent_sqm:,.1f}/m\u00b2</div>
        <div class="kpi-sub">scraped listings</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# MAP
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-title">Geographic Overview</div>', unsafe_allow_html=True)
st.caption("Dot color indicates verdict. Dot size reflects buy-win percentage.")

df_map = prov_view.dropna(subset=["lat", "lon"]).copy()

fig_map = px.scatter_mapbox(
    df_map, lat="lat", lon="lon", color="Verdict",
    color_discrete_map=COLOR_MAP,
    size=df_map["pct_buy"].clip(0.05, 1) * 100, size_max=22,
    hover_name="Province",
    hover_data={"Sigla": True, "Regione": True, "pct_buy": ":.1%",
                "Avg Rent \u20ac/sqm/month": ":.2f", "Monthly_RE_sqm": ":.2f",
                "Internet Rent \u20ac/sqm Feb 2026": ":.1f",
                "Price-to-Rent Ratio": ":.1f", "lat": False, "lon": False},
    labels={"pct_buy": "Buy Win %", "Monthly_RE_sqm": "Mortgage \u20ac/sqm/mo"},
    mapbox_style="carto-positron", zoom=4.8, center={"lat": 42.0, "lon": 12.5},
    height=560,
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(
        orientation="h", yanchor="top", y=0.98, xanchor="left", x=0.01,
        bgcolor="rgba(255,255,255,0.92)", bordercolor="#e2e8f0", borderwidth=1,
        font=dict(family="Inter, sans-serif", size=12),
    ),
)
st.plotly_chart(fig_map, use_container_width=True)


# ═══════════════════════════════════════════════════
# SCENARIO COMPARISON
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-title">Scenario Comparison</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    scenario_data = []
    for label, col in SCENARIO_PCT_MAP.items():
        src = prov_pct[prov_pct["Regione"].isin(selected_regions)] if selected_regions else prov_pct
        scenario_data.append({"Scenario": label, "Avg % Buy Wins": src[col].mean() * 100})
    df_sc = pd.DataFrame(scenario_data)

    fig_sc = px.bar(
        df_sc, x="Scenario", y="Avg % Buy Wins",
        color="Avg % Buy Wins",
        color_continuous_scale=["#ef4444", "#f59e0b", "#059669"],
        range_color=[50, 100], height=420,
    )
    fig_sc.add_hline(y=50, line_dash="dash", line_color="#94a3b8",
                     annotation_text="50% threshold",
                     annotation_font=dict(size=11, color="#64748b"))
    fig_sc.update_layout(
        **CHART_LAYOUT,
        title="Avg % of Listings Where Buying Wins",
    )
    fig_sc.update_xaxes(tickangle=-30, gridcolor="#f1f5f9", linecolor="#e2e8f0")
    fig_sc.update_yaxes(range=[0, 100], gridcolor="#f1f5f9", linecolor="#e2e8f0")
    st.plotly_chart(fig_sc, use_container_width=True)

with col_b:
    scatter_df = prov_pct.copy()
    if selected_regions:
        scatter_df = scatter_df[scatter_df["Regione"].isin(selected_regions)]
    scatter_df["Best"] = scatter_df["pct_buy_35_e20d80"] * 100
    scatter_df["Worst"] = scatter_df["pct_buy_50_e30d70"] * 100
    scatter_df["Swing"] = scatter_df["Best"] - scatter_df["Worst"]

    fig_scat = px.scatter(
        scatter_df, x="Best", y="Worst", hover_name="Province",
        color="Swing", color_continuous_scale=["#3b82f6", "#f59e0b", "#ef4444"],
        labels={"Best": "Buy Win % (Best: 3.5% E20/D80)",
                "Worst": "Buy Win % (Worst: 5.0% E30/D70)"},
        height=420,
    )
    fig_scat.add_shape(type="line", x0=0, y0=0, x1=100, y1=100,
                       line=dict(color="#cbd5e1", dash="dash"))
    fig_scat.add_shape(type="line", x0=50, y0=0, x1=50, y1=100,
                       line=dict(color="#ef4444", dash="dot", width=1))
    fig_scat.add_shape(type="line", x0=0, y0=50, x1=100, y1=50,
                       line=dict(color="#ef4444", dash="dot", width=1))
    fig_scat.update_layout(
        **CHART_LAYOUT,
        title="Buy Win % — Best vs. Worst Scenario",
    )
    st.plotly_chart(fig_scat, use_container_width=True)


# ═══════════════════════════════════════════════════
# FLIPPER PROVINCES
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-title">Scenario-Sensitive Provinces</div>', unsafe_allow_html=True)
st.caption("Provinces whose verdict flips between best and worst mortgage scenario.")

flip_df = prov_pct.copy()
if selected_regions:
    flip_df = flip_df[flip_df["Regione"].isin(selected_regions)]
flip_df["buy_best"] = flip_df["pct_buy_35_e20d80"] >= 0.5
flip_df["buy_worst"] = flip_df["pct_buy_50_e30d70"] >= 0.5
flip_df["flips"] = flip_df["buy_best"] != flip_df["buy_worst"]
n_flip = flip_df["flips"].sum()

st.markdown(f"**{n_flip}** province(s) change verdict between best and worst scenario.")

if n_flip > 0:
    flippers = flip_df[flip_df["flips"]].copy()
    disp = {"Province": flippers["Province"], "Sigla": flippers["Sigla"], "Region": flippers["Regione"]}
    for label, col in SCENARIO_PCT_MAP.items():
        short = label.split(" (")[0]
        disp[short] = (flippers[col] * 100).round(1).astype(str) + "%"
    df_flip_disp = pd.DataFrame(disp)

    def color_pct(val):
        try:
            n = float(val.replace("%", ""))
            return "background-color: #dcfce7; color: #166534; font-weight: 600" if n >= 50 \
                else "background-color: #fef2f2; color: #991b1b; font-weight: 600"
        except:
            return ""

    pct_cols = [c for c in df_flip_disp.columns if c not in ["Province", "Sigla", "Region"]]
    st.dataframe(df_flip_disp.style.map(color_pct, subset=pct_cols),
                 use_container_width=True, height=min(400, 50 + 35 * n_flip))


# ═══════════════════════════════════════════════════
# SIZE BREAKDOWN
# ═══════════════════════════════════════════════════

if selected_size != "All":
    st.markdown(f'<div class="section-title">{selected_size} Properties Breakdown</div>',
                unsafe_allow_html=True)

    sv = size_pct[size_pct["Size"] == selected_size].copy()
    sv = sv.merge(prov_region, on="Sigla", how="left")
    if selected_regions:
        sv = sv[sv["Regione"].isin(selected_regions)]
    sv["Province"] = sv["Sigla"].map(PROVINCE_NAMES)
    sv["pct_buy"] = sv[pct_col]
    sv["Verdict"] = np.where(sv["pct_buy"] >= 0.5, "BUY", "RENT")
    sv["lat"] = sv["Sigla"].map(lambda s: COORDS.get(s, [None, None])[0])
    sv["lon"] = sv["Sigla"].map(lambda s: COORDS.get(s, [None, None])[1])

    nb = (sv["Verdict"] == "BUY").sum()
    nr = (sv["Verdict"] == "RENT").sum()
    st.markdown(f"**{nb}** provinces favor BUY, **{nr}** favor RENT for {selected_size} properties.")

    sm = sv.dropna(subset=["lat", "lon"])
    fig_sm = px.scatter_mapbox(
        sm, lat="lat", lon="lon", color="Verdict", color_discrete_map=COLOR_MAP,
        size=sm["pct_buy"].clip(0.05, 1) * 100, size_max=20,
        hover_name="Province", hover_data={"pct_buy": ":.1%", "Regione": True, "lat": False, "lon": False},
        mapbox_style="carto-positron", zoom=4.8, center={"lat": 42.0, "lon": 12.5}, height=450,
    )
    fig_sm.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_sm, use_container_width=True)


# ═══════════════════════════════════════════════════
# REGIONAL OVERVIEW
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-title">Regional Overview</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    rp = prov_view.groupby("Regione").agg(avg_sale=("Avg Sale \u20ac/sqm", "mean")).reset_index()
    rp = rp.sort_values("avg_sale", ascending=True)
    fig_rp = px.bar(rp, y="Regione", x="avg_sale", orientation="h",
                    color="avg_sale", color_continuous_scale=["#bfdbfe", "#1e40af"], height=550)
    fig_rp.update_layout(
        **CHART_LAYOUT,
        title="Avg Sale Price by Region (\u20ac/m\u00b2)",
        yaxis_title="", xaxis_title="\u20ac/m\u00b2",
    )
    st.plotly_chart(fig_rp, use_container_width=True)

with col2:
    rptr = prov_view.groupby("Regione")["Price-to-Rent Ratio"].mean().reset_index()
    rptr = rptr.sort_values("Price-to-Rent Ratio", ascending=True)
    fig_ptr = px.bar(rptr, y="Regione", x="Price-to-Rent Ratio", orientation="h",
                     color="Price-to-Rent Ratio",
                     color_continuous_scale=["#059669", "#f59e0b", "#dc2626"], height=550)
    fig_ptr.add_vline(x=20, line_dash="dash", line_color="#94a3b8",
                      annotation_text="20x threshold",
                      annotation_font=dict(size=11, color="#64748b"))
    fig_ptr.update_layout(
        **CHART_LAYOUT,
        title="Price-to-Rent Ratio by Region",
        yaxis_title="",
    )
    st.plotly_chart(fig_ptr, use_container_width=True)


# ═══════════════════════════════════════════════════
# RENT COMPARISON: SCRAPED vs INTERNET
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-title">Scraped Rent vs. Published Internet Rent</div>',
            unsafe_allow_html=True)

rc = prov_view[["Province", "Sigla", "Regione",
                 "Avg Rent \u20ac/sqm/month", "Internet Rent \u20ac/sqm Feb 2026"]].dropna().copy()
rc["Diff"] = rc["Avg Rent \u20ac/sqm/month"] - rc["Internet Rent \u20ac/sqm Feb 2026"]
rc["Diff %"] = (rc["Diff"] / rc["Internet Rent \u20ac/sqm Feb 2026"]) * 100

fig_rc = px.scatter(
    rc, x="Internet Rent \u20ac/sqm Feb 2026", y="Avg Rent \u20ac/sqm/month",
    hover_name="Province", color="Diff %",
    color_continuous_scale="RdBu_r", color_continuous_midpoint=0,
    size=abs(rc["Diff"]).clip(0.5), size_max=15,
    height=450,
)
mx = max(rc["Internet Rent \u20ac/sqm Feb 2026"].max(), rc["Avg Rent \u20ac/sqm/month"].max())
fig_rc.add_shape(type="line", x0=0, y0=0, x1=mx, y1=mx,
                 line=dict(color="#cbd5e1", dash="dash"))
fig_rc.update_layout(
    **CHART_LAYOUT,
    title="Scraped vs Internet Rent (\u20ac/sqm/month)",
)
st.plotly_chart(fig_rc, use_container_width=True)


# ═══════════════════════════════════════════════════
# PROVINCE RANKINGS
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-title">Province Rankings</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Strongest BUY", "Strongest RENT", "Full Table"])

ranking = prov_view[["Province", "Sigla", "Regione", "pct_buy", "Avg Sale \u20ac/sqm",
                      "Avg Rent \u20ac/sqm/month", "Monthly_RE_sqm",
                      "Internet Rent \u20ac/sqm Feb 2026", "Price-to-Rent Ratio",
                      "N Sale", "N Rent", "Verdict"]].copy()
ranking["% Buy"] = (ranking["pct_buy"] * 100).round(1)
fmt = {"% Buy": "{:.1f}%", "Avg Sale \u20ac/sqm": "\u20ac{:,.0f}", "Avg Rent \u20ac/sqm/month": "\u20ac{:.2f}",
       "Monthly_RE_sqm": "\u20ac{:.2f}", "Internet Rent \u20ac/sqm Feb 2026": "\u20ac{:.1f}",
       "Price-to-Rent Ratio": "{:.1f}x", "N Sale": "{:,}", "N Rent": "{:,}"}
show_cols = ["Province", "Regione", "% Buy", "Avg Sale \u20ac/sqm",
             "Avg Rent \u20ac/sqm/month", "Monthly_RE_sqm", "Price-to-Rent Ratio"]

with tab1:
    bb = ranking[ranking["Verdict"] == "BUY"].sort_values("pct_buy", ascending=False).head(15)
    st.dataframe(bb[show_cols].style.format(fmt, na_rep="\u2014"), use_container_width=True)

with tab2:
    br = ranking[ranking["Verdict"] == "RENT"].sort_values("pct_buy").head(15)
    if len(br) == 0:
        st.info("No provinces favor renting under this scenario.")
    else:
        st.dataframe(br[show_cols].style.format(fmt, na_rep="\u2014"), use_container_width=True)

with tab3:
    def hl(val):
        if val == "BUY": return "background-color: #dcfce7; color: #166534"
        elif val == "RENT": return "background-color: #fef2f2; color: #991b1b"
        return ""
    full = ranking.sort_values("Province")
    all_cols = ["Province", "Sigla", "Regione", "Verdict", "% Buy", "Avg Sale \u20ac/sqm",
                "Avg Rent \u20ac/sqm/month", "Monthly_RE_sqm", "Internet Rent \u20ac/sqm Feb 2026",
                "Price-to-Rent Ratio", "N Sale", "N Rent"]
    st.dataframe(full[all_cols].style.map(hl, subset=["Verdict"]).format(fmt, na_rep="\u2014"),
                 use_container_width=True, height=600)


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.78rem; padding:0.8rem 0 1.5rem;'>"
    "Italian Real Estate Dashboard &nbsp;|&nbsp; immobiliare.it + idealista &nbsp;|&nbsp; Feb 2026"
    "<br>Unrecoverable-cost method &nbsp;|&nbsp; 8 scenarios"
    "</div>", unsafe_allow_html=True)
