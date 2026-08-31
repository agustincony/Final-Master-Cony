import streamlit as st
import pandas as pd
import numpy as np
import base64, os

st.set_page_config(page_title="Perfiles", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
header[data-testid="stHeader"]   { display: none !important; }
.stApp                           { background-color: #1a2535; color: white; min-width: 1200px !important; }
.block-container                 { padding-top: 90px !important; padding-left: 2rem !important; padding-right: 2rem !important; }
section[data-testid="stSidebar"] { background-color: #0f1a28 !important; margin-top: 72px !important; }
section[data-testid="stSidebar"] span { color: white !important; }
section[data-testid="stSidebar"] p    { color: white !important; }
section[data-testid="stSidebar"] a    { color: white !important; }
div[data-testid="stSidebarCollapseButton"] { display: none !important; }
section[data-testid="collapsedControl"] { display: none !important; }
div[data-testid="stSelectbox"] > label { color: #7a9ab5 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
div[data-testid="stRadio"] label {
    display: flex !important; align-items: center !important; justify-content: center !important;
    padding: 5px 14px !important; border-radius: 6px !important; font-size: 13px !important;
    font-weight: 700 !important; color: #ffffff !important; cursor: pointer !important;
    background: transparent !important; white-space: nowrap !important;
}
div[data-testid="stRadio"] input[type="radio"] { display: none !important; }
div[data-testid="stRadio"] label svg { display: none !important; }
div[data-testid="stRadio"] label > div:first-child { display: none !important; }
div[data-testid="stRadio"] span { display: none !important; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important; flex-direction: row !important; gap: 4px !important;
    background-color: transparent !important; border: none !important;
    padding: 0 !important;
}
div[data-testid="stRadio"] label {
    display: flex !important; align-items: center !important; justify-content: center !important;
    padding: 5px 14px !important; border-radius: 6px !important; font-size: 13px !important;
    font-weight: 700 !important; color: #ffffff !important; cursor: pointer !important;
    background: transparent !important; white-space: nowrap !important;
}
div[data-testid="stRadio"] label:has(input:checked) { background-color: #00A8CC !important; }
div[data-testid="stRadio"] label p { color: #ffffff !important; }
div[data-testid="stRadio"] > label:first-child { display: none !important; }
.filtro-label { font-size: 11px; color: #7a9ab5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; display: block; }
.seccion-header { font-size: 11px; font-weight: 800; letter-spacing: 2px; color: #ffffff; background: #0f1a28; border-left: 4px solid #00A8CC; padding: 8px 14px; margin: 20px 0 10px 0; text-transform: uppercase; border-radius: 0 4px 4px 0; }

.fifa-grid { display: flex; flex-wrap: wrap; gap: 24px; padding: 10px 0; }
.fifa-card {
    width: 220px; position: relative; padding: 14px 14px 80px 14px;
    font-family: 'Arial Black', 'Impact', sans-serif;
    box-shadow: 0 8px 32px rgba(0,0,0,0.7), 0 2px 4px rgba(255,220,80,0.3);
    background:
        repeating-conic-gradient(from 0deg at 50% 110%, rgba(255,255,255,0.07) 0deg, transparent 2deg, transparent 5deg, rgba(255,255,255,0.04) 6deg, transparent 8deg),
        linear-gradient(160deg, #f7e87a 0%, #d4a017 15%, #f0cc50 30%, #c8900a 45%, #f5d848 55%, #b8780a 70%, #e8c040 82%, #a06010 92%, #c8a030 100%);
    clip-path: path('M 20 0 Q 0 0 0 20 L 0 420 Q 0 440 18 440 Q 85 440 110 460 Q 135 440 202 440 Q 220 440 220 420 L 220 20 Q 220 0 200 0 Z');
}
.fifa-card-wide {
    width: 220px; padding: 16px 16px 80px 16px;
    clip-path: path('M 20 0 Q 0 0 0 20 L 0 420 Q 0 440 18 440 Q 85 440 110 460 Q 135 440 202 440 Q 220 440 220 420 L 220 20 Q 220 0 200 0 Z');
    overflow: visible;
}
.fifa-shine { position: absolute; top: 0; left: 0; right: 0; height: 55%; border-radius: 12px 12px 60% 60% / 12px 12px 40% 40%; background: radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.28) 0%, transparent 70%); pointer-events: none; z-index: 1; }
.fifa-rays { position: absolute; bottom: -10%; left: 50%; transform: translateX(-50%); width: 300%; height: 160%; background: repeating-conic-gradient(from 0deg at 50% 100%, rgba(255,255,255,0.06) 0deg 2deg, transparent 2deg 8deg); pointer-events: none; z-index: 0; }
.fifa-card-inner { position: relative; z-index: 2; }
.fifa-top { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 2px; }
.fifa-rating { font-size: 16px; font-weight: 900; color: #000000; line-height: 1; letter-spacing: -1px; text-shadow: 0 1px 0 rgba(255,255,255,0.35); }
.fifa-rating-wide { font-size: 20px; }
.fifa-pos { font-size: 11px; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 1px; margin-top: -6px; margin-bottom: 4px; }
.fifa-pos-wide { font-size: 14px; }
.fifa-avatar { width: 100%; height: 20px; background: linear-gradient(170deg, rgba(255,220,80,0.3) 0%, rgba(160,90,0,0.4) 100%); border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-bottom: 6px; border: 1px solid rgba(0,0,0,0.15); }
.fifa-avatar-wide { height: 180px; }
.fifa-initials { font-size: 32px; font-weight: 900; color: rgba(60,30,0,0.45); letter-spacing: -1px; }
.fifa-initials-wide { font-size: 46px; }
.fifa-name { font-size: 11px; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 0.8px; text-align: center; width: 100%; border-top: 1px solid rgba(0,0,0,0.18); border-bottom: 1px solid rgba(0,0,0,0.18); padding: 4px 0; margin-bottom: 6px; text-shadow: 0 1px 0 rgba(255,255,255,0.2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fifa-name-wide { font-size: 14px; }
.fifa-stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3px 8px; }
.fifa-stat-item { display: flex; flex-direction: column; align-items: center; }
.fifa-stat-val { font-size: 13px; font-weight: 900; line-height: 1; }
.fifa-stat-val-wide { font-size: 16px; }
.fifa-stat-label { font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.fifa-stat-label-wide { font-size: 10px; }

.tabla-semaforo { width: 100%; border-collapse: collapse; font-size: 12px; }
.tabla-semaforo th { background: #0f1a28; color: #00A8CC; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; padding: 8px 6px; border-bottom: 2px solid #1e3048; text-align: center; }
.tabla-semaforo th.col-jugador { text-align: left; min-width: 140px; }
.tabla-semaforo td { padding: 6px 6px; border-bottom: 1px solid #1e3048; text-align: center; color: white; }
.tabla-semaforo td.col-jugador { text-align: left; color: #cce0f0; font-weight: 600; }
.tabla-semaforo tr:hover td { background: #1e3048 !important; }
.celda-valor { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; min-width: 52px; }
div[data-testid="stSlider"] label { color: #ffffff !important; }
div[data-testid="stSlider"] p { color: #ffffff !important; }
div[data-testid="stPopover"] > div > button {
    background-color: #0f1a28 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 6px !important;
    color: white !important;
    font-size: 13px !important;
    width: 100% !important;
    text-align: left !important;
}
div[data-testid="stPopoverBody"] {
    background-color: #0f1a28 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 8px !important;
}
div[data-testid="stPopoverBody"] label { color: #cce0f0 !important; font-size: 13px !important; }
div[data-testid="stPopoverBody"] p { color: #7a9ab5 !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ────────────────────────────────────────────────────────────────
METRICAS = {
    "Minutos":                                  ("Min",    "min",  "⏱️",  False),
    "Maximum Velocity":                         ("Vel Max","km/h", "💨",  False),
    "Max Vel (% Max)":                          ("% Max",  "%",    "📊",  False),
    "Distancia Total":                          ("Dist",   "mts",  "📍",  False),
    "AI 18 Km/h":                               ("HSR",    "mts",  "⚡",  False),
    "DT + 25 Km/h":                             ("Sprint", "mts",  "🚀",  False),
    "+25 Km/h #":                               ("N°Spr",  "cant", "🏃",  False),
    "Acel 2,5 m/ss #":                          ("Acel",   "cant", "▲",   False),
    "Desacel -2,5 m/ss #":                      ("Decel",  "cant", "▼",   False),
    "Contact Involvement Total Count Avg":      ("Cont",   "cant", "💥",  False),
    "Contact Involvement Average BiG Time":     ("BiG",    "seg",  "🔄",  True),
}
COLS = list(METRICAS.keys())
EQUIPOS_ORDEN = ["Primera", "Intermedia", "Pre A"]

GRUPOS_PUESTO = {
    "Primeras":         ["Pilar izquierdo", "Pilar derecho", "Hooker"],
    "Segundas":         ["Segunda Linea"],
    "Terceras":         ["Ala", "Octavo"],
    "Pareja de medios": ["Medio Scrum", "Apertura"],
    "Centros":          ["Centro"],
    "3 del fondo":      ["Wing", "Full Back"],
}

NUMEROS_CAMISETA = {
    "Jeronimo Solveyra":          1,
    "Facundo Andreotti":          2,
    "Hugo Garcia":                3,
    "Eugenio Sartori":            4,
    "Joaquin Britto":             5,
    "Felix Paolucci":             6,
    "Luis Briatore":              8,
    "Ignacio Sanchez":            9,
    "Felipe Hileman":            10,
    "Santiago David":            11,
    "Franco Pastorino":          13,
    "Ramón Castillo":            14,
    "Agustín Belleze":           15,
    "Juan Cruz Perri":           16,
    "Santiago Acuña":            17,
    "Ignacio Larrague":          18,
    "Leo Mazzini":               19,
    "Juan Bautista Torres Obeid":20,
    "Felipe Carman":             21,
    "Tomas Phelan":              22,
    "Benjamin Rocca Rivarola":   23,
    "Juan Ignacio Albareda":     24,
    "Juan Franco Akemeier":      25,
    "Bautista Belleze":          26,
    "Pampa Storey":              27,
    "Facundo Barone":            28,
    "Francisco Lescano":         29,
    "Agustin Posleman":          30,
    "Joaquin Saenz de Miera":    31,
    "Facundo Scaiano":           26,
    "Benjamin Belaga":           33,
    "Vicente Mammoliti":         34,
    "Isidro Pichot":             35,
    "Eliseo Roger":              36,
    "Pedro Repetto":             38,
    "Benito Paolucci":           40,
    "Mateo Castiglione":         42,
    "Ian Oppenheimer":           44,
    "Matias Phelan":             46,
    "Alejo Lavayen":             48,
    "Ignacio Torrado":           50,
    "Bautista Cejas":            53,
    "Joaquin Behar":             60,
    "Benjamín Llano":            61,
    "Thiago Federico":           64,
    "Nicanor Castillo":          65,
    "Joaquin Ibañez":            66,
    "Segundo Roy":               68,
    "Francisco Rocca Sackmann":  73,
    "Ignacio Milesi":            74,
    "Tomas Gongora":             76,
    "Alejo Montes de Oca":       77,
    "Tomas Belgrano":            94,
    "Ignacio Ymaz":              95,
    "Mateo Baldrich":            96,
    "Santiago Murray":           98,
    "Ricardo Pasman":            99,
    "Salvador Ochoa":           100,
    "Joaquin Dominguez Perdigón":84,
    "Martín Roger":              85,
    "Juan Cruz Meabe":           86,
    "Beltran Lagos":            101,
    "Facundo Soave":            102,
    "Cristobal Bernasconi":     104,
    "Martín Landajo":           106,
}

COLORES_RIVALES = {
    "Los Tilos":  "#228B22",
    "Tilos":      "#228B22",
    "Matreros":   "#D32F2F",
    "Rosario":    "#800020",
    "CUBA":       "#002FA7",
    "Cuba":       "#002FA7",
    "Regatas":    "#1E3F66",
    "Biei":      "#052B76",
    "La Plata":   "#FFCC00",
    "Belgrano":   "#5C4033",
    "Hindu":      "#FFCC00",
    "Hindú":      "#FFCC00",
    "SIC":        "#6CB4EE",
    "Sic":        "#6CB4EE",
    "Champagnat": "#003366",
    "Newman":     "#4A0E17",
    "Alumni":     "#E63946",
    "Plaza":      "#8B0000",
}

# ── Imágenes de jugadores ─────────────────────────────────────────────────────
@st.cache_data
def cargar_imagenes():
    df_img = pd.read_excel("Imagenes perfiles.xlsx")
    # Mapeo nombre Excel → nombre GPS
    MAPEO_NOMBRES = {
        "Juan Bautista Torres Obeid": "Juan Bautista Torres Obeid",
        "Tomás Gongora":              "Tomas Gongora",
        "Facundo Andreotti":          "Facundo Andreotti",
        "Juan Albareda":              "Juan Ignacio Albareda",
        "Ignacio Rizzutti":           "Juan Ignacio Rizzuti",
        "Juan Cruz Perri":            "Juan Cruz Perri",
        "Felix Paolucci":             "Felix Paolucci",
        "Hugo García":                "Hugo Garcia",
        "Ian Openheimer":             "Ian Oppenheimer",
        "Joaquin Britto":             "Joaquin Britto",
        "Facundo Scaiano":            "Facundo Scaiano",
        "Cristo Bernasconi":          "Cristobal Bernasconi",
        "Agustin Posleman":           "Agustin Posleman",
        "Thiago Federico":            "Thiago Federico",
        "Ignacio Larrague":           "Ignacio Larrague",
        "Mateo Castiglione":          "Mateo Castiglione",
        "Salvador Ochoa":             "Salvador Ochoa",
        "Mateo Stortoni":             "Mateo Stortoni",
        "Leo Mazzini":                "Leo Mazzini",
        "Joaquin Saenz de Miera":     "Joaquin Saenz de Miera",
        "Ignacio Torrado":            "Ignacio Torrado",
        "Benjamin Rocca Rivarola":    "Benjamin Rocca Rivarola",
        "Francisco Cossio":           "Francisco Cossio",
        "Eugenio Sartori":            "Eugenio Sartori",
        "Santiago Acuña":             "Santiago Acuña",
        "Pastorino Franco":           "Franco Pastorino",
        "Bautista Belleze":           "Bautista Belleze",
        "Pampa Storey":               "Pampa Storey",
        "Benito Paolucci":            "Benito Paolucci",
        "Facundo Soave":              "Facundo Soave",
        "Felipe Guerrero":            "Felipe Guerrero",
        "Eliseo Roger":               "Eliseo Roger",
        "Vicente Mammolitti":         "Vicente Mammoliti",
        "Joaquin Sanchez":            "Joaquin Sanchez",
        "Bautista Cejas":             "Bautista Cejas",
        "Felipe Carman":              "Felipe Carman",
        "Alejo Montes de Oca":        "Alejo Montes de Oca",
        "Felipe Hileman":             "Felipe Hileman",
        "Jeronimo Solveyra":          "Jeronimo Solveyra",
        "Benjamin Belaga":            "Benjamin Belaga",
        "Tomas Phelan":               "Tomas Phelan",
        "Matias Phelan":              "Matias Phelan",
        "Joaquin Behar":              "Joaquin Behar",
        "Santiago Murray":            "Santiago Murray",
        "Ricardo Pasman":             "Ricardo Pasman",
        "Nicanor Castillo":           "Nicanor Castillo",
        "Jeronimo Tumbarello":        "Jeronimo Tumbarello",
        "Pedro Repetto":              "Pedro Repetto",
        "Santiago David":             "Santiago David",
        "Francisco Lescano":          "Francisco Lescano",
        "Facundo Barone":             "Facundo Barone",
        "Juan Akemeier":              "Juan Franco Akemeier",
        "Isidro Pichot":              "Isidro Pichot",
        "Felipe Probaos":             "Felipe Probaos",
        "Ignacio Milesi":             "Ignacio Milesi",
        "Mateo Sartori":              "Mateo Sartori",
        "Segundo Roy":            "Segundo Roy",
    }
    resultado = {}
    for _, row in df_img.iterrows():
        nombre_excel = row["Jugador"]
        url = row["URL"]
        if pd.isna(url):
            continue
        nombre_gps = MAPEO_NOMBRES.get(nombre_excel, nombre_excel)
        resultado[nombre_gps] = url
    return resultado

IMAGENES_JUGADORES = cargar_imagenes()

# ── Helpers ───────────────────────────────────────────────────────────────────
def color_pct(pct, inverso=False):
    if pct is None or (isinstance(pct, float) and np.isnan(pct)): return "#4a6a80"
    if inverso:
        pct = 1 / pct if pct > 0 else 0
    if pct < 0.75:  return "#FF0000"
    if pct < 1:  return "#FFD000"
    if pct >= 1: return "#00CC44"
    return "#00CC44"

def fmt(val):
    if val is None or (isinstance(val, float) and np.isnan(val)): return "—"
    if val == 0: return "—"
    if val >= 10 or val == int(val): return f"{val:,.0f}".replace(",", ".")
    return f"{val:.1f}".replace(".", ",")

def fmt2(val):
    if val is None or (isinstance(val, float) and np.isnan(val)): return "—"
    return f"{val:.2f}".replace(".", ",")

def calc_perfil_competitivo(df):
    """Perfil = (max + media) / 2 de MD con 30-100 min. Siempre sesión completa."""
    df_md = df[df["MD"] == "MD"].copy()
    agg_dict = {col: (col, "sum") for col in COLS if col != "Minutos"}
    agg_dict["Maximum Velocity"] = ("Maximum Velocity", "max")
    agg_dict["Max Vel (% Max)"]  = ("Max Vel (% Max)", "max")
    por_dia = df_md.groupby(["Player Name", "Fecha"]).agg(
        minutos=("Minutos", "sum"), **agg_dict
    ).reset_index()
    por_dia = por_dia[(por_dia["minutos"] >= 30) & (por_dia["minutos"] <= 100)]
    jugadores_validos = por_dia.groupby("Player Name").size()
    jugadores_validos = jugadores_validos[jugadores_validos >= 6].index
    por_dia = por_dia[por_dia["Player Name"].isin(jugadores_validos)]
    if len(por_dia) == 0:
        return pd.Series({col: np.nan for col in COLS + ["Maximum Velocity", "Max Vel (% Max)"]})
    perfil = {}
    for col in COLS:
        data = por_dia["minutos"] if col == "Minutos" else por_dia[col]
        perfil[col] = (data.max() + data.mean()) / 2
        perfil["Maximum Velocity"] = por_dia["Maximum Velocity"].max() if "Maximum Velocity" in por_dia.columns else np.nan
    perfil["Max Vel (% Max)"]  = por_dia["Max Vel (% Max)"].max()  if "Max Vel (% Max)" in por_dia.columns else np.nan
    return pd.Series(perfil)
 
def calc_perfil_por_jugador(df):
    jugadores = df["Player Name"].dropna().unique()
    resultado = {}
    for j in jugadores:
        perf = calc_perfil_competitivo(df[df["Player Name"] == j])
        if not perf.isna().all():
            resultado[j] = perf
    return resultado

def initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return parts[0][0].upper() + parts[-1][0].upper()
    return name[:2].upper()

def rating_from_perfil(perf, perf_ref):
    scores = []
    for col, (_, _, _, inverso) in METRICAS.items():
        val   = perf.get(col, np.nan)
        bench = perf_ref.get(col, np.nan)
        if np.isnan(val) or np.isnan(bench) or bench == 0:
            continue
        pct = val / bench
        if inverso:
            pct = 1 / pct if pct > 0 else 0
        scores.append(min(pct, 1.5))
    if not scores:
        return 70
    avg = np.mean(scores)
    return int(np.clip(50 + avg * 40, 50, 99))

def cargar_datos():
    if "df_excel" not in st.session_state:
        st.session_state["df_excel"] = pd.read_parquet("totales_gps.parquet")
    df = st.session_state["df_excel"].copy()
    df = df[
        (df["Period Name"] == "Session") &
        (df["Period Tags"] != "Diferenciado")
    ].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    return df

def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def fifa_card_html(name, subtitle, perfil, rating, is_wide=False):
    ini        = initials(name)
    w          = "-wide" if is_wide else ""
    wide_cls   = "  fifa-card-wide" if is_wide else ""
    short_name = name.split()[-1].upper() if name else name

    def stat(val, label):
        return (
            '<div style="display:flex;flex-direction:column;align-items:center;min-width:44px;">'
            '<span style="font-size:13px;font-weight:900;color:#fff;line-height:1;">' + fmt(val) + '</span>'
            + '<span style="font-size:6px;font-weight:400;color:#000;text-transform:uppercase;letter-spacing:0.5px;">' + label + '</span>'
            + '</div>'
        )

    def row3(v1, l1, v2, l2, v3, l3):
        return '<div style="display:flex;justify-content:space-around;margin-bottom:4px;">' + stat(v1,l1) + stat(v2,l2) + stat(v3,l3) + '</div>'

    def row2(v1, l1, v2, l2):
        return '<div style="display:flex;justify-content:center;gap:24px;margin-bottom:4px;">' + stat(v1,l1) + stat(v2,l2) + '</div>'

    p = perfil
    stats_html = (
        '<div style="display:flex;justify-content:space-around;margin-bottom:4px;">'
        + stat(p.get("Minutos", np.nan), "Min")
        + '<div style="display:flex;flex-direction:column;align-items:center;min-width:44px;"><span style="font-size:13px;font-weight:900;color:#fff;line-height:1;">' + (fmt2(p.get("Maximum Velocity", np.nan)) if vista == "Jugador" else "—") + '</span><span style="font-size:6px;font-weight:400;color:#000;text-transform:uppercase;letter-spacing:0.5px;">Vel Max</span></div>'
        + '</div>'
        + row3(p.get("Distancia Total", np.nan),    "Dist",
               p.get("AI 18 Km/h", np.nan),          "HSR",
               p.get("DT + 25 Km/h", np.nan),        "Sprint")
        + row2(p.get("Acel 2,5 m/ss #", np.nan),   "Acel",
               p.get("Desacel -2,5 m/ss #", np.nan),"Decel")
        + row2(p.get("Contact Involvement Total Count Avg", np.nan), "Cont",
               p.get("Contact Involvement Average BiG Time", np.nan),"BiG")
    )

    return (
        '<div class="fifa-card' + wide_cls + '">'
        + '<div class="fifa-rays"></div>'
        + '<div class="fifa-shine"></div>'
        + '<div class="fifa-card-inner">'
        + '<div class="fifa-top" style="display:flex;flex-direction:row;justify-content:space-between;align-items:flex-start;width:100%;">'
        + '<div>'
        + '<div class="fifa-rating' + w + '">' + str(rating) + '</div>'
        + '<div class="fifa-pos' + w + '">' + subtitle + '</div>'
        + '</div>'
        + '<img src="data:image/png;base64,' + logo_b64 + '" style="height:52px;opacity:0.7;">'
        + '</div>'
        + (
            '<div class="fifa-avatar' + (' fifa-avatar-wide' if is_wide else '') + '" style="padding:2px;">'
            + '<img src="' + IMAGENES_JUGADORES[name] + '" style="width:100%;height:170px;object-fit:cover;border-radius:4px;object-position:center 5%;">'
            + '</div>'
            if name in IMAGENES_JUGADORES else
            '<div class="fifa-avatar' + (' fifa-avatar-wide' if is_wide else '') + '">'
            + '<span class="fifa-initials' + (' fifa-initials-wide' if is_wide else '') + '">' + ini + '</span>'
            + '</div>'
        )
        + '<div class="fifa-name' + (' fifa-name-wide' if is_wide else '') + '">' + short_name + '</div>'
        + stats_html
        + '</div>'
        + '</div>'
    )



# ── Topbar ────────────────────────────────────────────────────────────────────
logo_b64  = img_base64("LOGO_CASI_SIN_FONDO.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:62px; width:auto;">' if logo_b64 else "⚡"

st.markdown(
    f'<style>.topbar {{position:fixed;top:0;left:0;right:0;z-index:99999;background:#0f1a28;'
    f'border-bottom:3px solid #00A8CC;height:72px;display:flex;align-items:center;padding:0 24px;gap:16px;}}'
    f'.topbar-divider {{width:1px;height:36px;background:#2a4060;margin:0 16px;}}'
    f'.topbar-club {{font-size:18px;font-weight:900;color:white;letter-spacing:1px;text-transform:uppercase;}}'
    f'.topbar-sub {{font-size:13px;font-weight:600;color:#00A8CC;letter-spacing:2px;text-transform:uppercase;}}'
    f'.topbar-page {{font-size:13px;font-weight:700;color:#7a9ab5;letter-spacing:2px;text-transform:uppercase;}}</style>'
    f'<div class="topbar"><div>{logo_html}</div>'
    f'<div class="topbar-divider"></div><span class="topbar-club">Club Atlético de San Isidro</span>'
    f'<div class="topbar-divider"></div><span class="topbar-sub">Análisis de rendimiento</span>'
    f'<div class="topbar-divider"></div><span class="topbar-page">Perfil de Rendimiento · Partido</span></div>',
    unsafe_allow_html=True
)

df_raw = cargar_datos()

# ── Filtros ───────────────────────────────────────────────────────────────────
equipos_disp = [e for e in EQUIPOS_ORDEN if e in df_raw["Equipo"].dropna().unique()]
pf_equipo = None
pf_puesto = None
pf_jugador = None
pf_participacion = "Sesión completa"

pf_col1, pf_col2, pf_col3, pf_col4 = st.columns([4, 2, 2, 2])

with pf_col1:
    st.markdown('<span class="filtro-label"></span>', unsafe_allow_html=True)
    vista = st.radio("", ["Plantel", "Equipo", "Puesto", "Jugador"],
                     horizontal=True, label_visibility="collapsed", key="pf_vista")

with pf_col2:
    if vista == "Equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        pf_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="pf_eq")
    elif vista == "Puesto":
        st.markdown('<span class="filtro-label">Puesto</span>', unsafe_allow_html=True)
        pf_puesto = st.selectbox("", list(GRUPOS_PUESTO.keys()), label_visibility="collapsed", key="pf_pu")
    elif vista == "Jugador":
        jugadores_disp = sorted(df_raw["Player Name"].dropna().unique())
        st.markdown('<span class="filtro-label">Jugador</span>', unsafe_allow_html=True)
        pf_jugador = st.selectbox("", jugadores_disp, label_visibility="collapsed", key="pf_ju")

with pf_col3:
    if vista in ("Puesto", "Jugador"):
        st.markdown('<span class="filtro-label">Participación</span>', unsafe_allow_html=True)
        pf_participacion = st.radio("", ["Sesión completa", "Solo 1 equipo"],
                                    horizontal=False, label_visibility="collapsed", key="pf_part")

with pf_col4:
    if vista in ("Puesto", "Jugador") and pf_participacion == "Solo 1 equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        pf_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="pf_eq2")

equipo_sel = pf_equipo
puesto_sel = pf_puesto
jugador_sel = pf_jugador

# ── Base según vista ──────────────────────────────────────────────────────────
if vista == "Plantel":
    df_base = df_raw.copy()
    titulo  = "Plantel completo"
elif vista == "Equipo":
    df_base = df_raw[df_raw["Equipo"] == pf_equipo] if pf_equipo else df_raw.copy()
    titulo  = pf_equipo or "Equipo"
elif vista == "Puesto":
    puestos_grupo = GRUPOS_PUESTO.get(pf_puesto, [])
    if pf_participacion == "Solo 1 equipo" and pf_equipo:
        df_eq = df_raw[df_raw["Equipo"] == pf_equipo]
    else:
        df_eq = df_raw
    df_base = df_eq[df_eq["Position Name"].isin(puestos_grupo)] if puestos_grupo else df_eq
    titulo  = (pf_puesto + " — " + (pf_equipo or "Plantel")) if pf_puesto else "Puesto"
else:  # Jugador
    if pf_participacion == "Solo 1 equipo" and pf_equipo:
        df_base = df_raw[(df_raw["Player Name"] == pf_jugador) & (df_raw["Equipo"] == pf_equipo)] if pf_jugador else df_raw
    else:
        df_base = df_raw[df_raw["Player Name"] == pf_jugador] if pf_jugador else df_raw
    titulo  = pf_jugador or "Jugador"

# ── Sección 1: Perfil Competitivo ─────────────────────────────────────────────
st.markdown('<div class="seccion-header">🏆 Perfil Competitivo — ' + titulo + '</div>', unsafe_allow_html=True)

if vista == "Plantel":
    perfil_grupo = calc_perfil_competitivo(df_base)
    html_card = fifa_card_html(titulo, "Perfil competitivo", perfil_grupo, rating=85, is_wide=True)
    st.markdown("<div class='fifa-grid'>" + html_card + "</div>", unsafe_allow_html=True)

elif vista == "Equipo":
    perfiles_jug = calc_perfil_por_jugador(df_base)
    perfil_grupo = pd.Series({col: np.nanmean([p[col] for p in perfiles_jug.values()]) for col in COLS})
    html_card = fifa_card_html(titulo, "Perfil competitivo", perfil_grupo, rating=85, is_wide=True)
    col_card, col_tabla = st.columns([1, 3])
    with col_card:
        st.markdown("<div class='fifa-grid'>" + html_card + "</div>", unsafe_allow_html=True)
    with col_tabla:
        if perfiles_jug:
            cabecera = "<tr><th class='col-jugador'>Jugador</th>"
            for col, (label, unidad, icono, _) in METRICAS.items():
                cabecera += "<th>" + icono + "<br>" + label + "</th>"
            cabecera += "</tr>"
            filas = ""
            for jug, perf in sorted(perfiles_jug.items()):
                fila = "<tr><td class='col-jugador'>" + jug + "</td>"
                for col, (_, _, _, inverso) in METRICAS.items():
                    val   = perf[col]
                    bench = perfil_grupo[col]
                    pct   = val / bench if bench and not np.isnan(bench) and not np.isnan(val) else None
                    color = color_pct(pct, inverso)
                    bg    = color + "22"
                    fila += "<td><span class='celda-valor' style='background:" + bg + "; color:" + color + ";'>" + (fmt2(val) if col == "Maximum Velocity" else fmt(val)) + "</span></td>"
                fila += "</tr>"
                filas += fila
            st.markdown(
                "<div style='overflow-x:auto;'><table class='tabla-semaforo'>" + cabecera + filas + "</table></div>",
                unsafe_allow_html=True
            )

elif vista == "Puesto":
    perfiles_jug = calc_perfil_por_jugador(df_base)
    perfil_grupo = pd.Series({col: np.nanmean([p[col] for p in perfiles_jug.values()]) for col in COLS})
    html_card = fifa_card_html(titulo, "Perfil competitivo", perfil_grupo, rating=85, is_wide=True)
    col_card, col_tabla = st.columns([1, 3])
    with col_card:
        st.markdown("<div class='fifa-grid'>" + html_card + "</div>", unsafe_allow_html=True)
    with col_tabla:
        if perfiles_jug:
            cabecera = "<tr><th class='col-jugador'>Jugador</th>"
            for col, (label, unidad, icono, _) in METRICAS.items():
                cabecera += "<th>" + icono + "<br>" + label + "</th>"
            cabecera += "</tr>"
            filas = ""
            for jug, perf in sorted(perfiles_jug.items()):
                fila = "<tr><td class='col-jugador'>" + jug + "</td>"
                for col, (_, _, _, inverso) in METRICAS.items():
                    val   = perf[col]
                    bench = perfil_grupo[col]
                    pct   = val / bench if bench and not np.isnan(bench) and not np.isnan(val) else None
                    color = color_pct(pct, inverso)
                    bg    = color + "22"
                    fila += "<td><span class='celda-valor' style='background:" + bg + "; color:" + color + ";'>" + (fmt2(val) if col == "Maximum Velocity" else fmt(val)) + "</span></td>"
                fila += "</tr>"
                filas += fila
            st.markdown(
                "<div style='overflow-x:auto;'><table class='tabla-semaforo'>" + cabecera + filas + "</table></div>",
                unsafe_allow_html=True
            )

else:  # Jugador
    if pf_participacion == "Solo 1 equipo" and pf_equipo:
        df_jug_raw = df_raw[(df_raw["Player Name"] == jugador_sel) & (df_raw["Equipo"] == pf_equipo)] if jugador_sel else df_raw
    else:
        df_jug_raw = df_raw[df_raw["Player Name"] == jugador_sel] if jugador_sel else df_raw
    perf = calc_perfil_competitivo(df_jug_raw)
    df_ref     = df_raw[df_raw["Equipo"] == equipo_sel] if equipo_sel else df_raw
    perfil_ref = calc_perfil_competitivo(df_ref)
    rat        = rating_from_perfil(perf, perfil_ref)
    puesto_jug = df_jug_raw["Position Name"].dropna().iloc[0] if len(df_jug_raw) > 0 else "—"
    num_camiseta = NUMEROS_CAMISETA.get(jugador_sel, "—")
    html_card  = fifa_card_html(jugador_sel or "Jugador", puesto_jug, perf, num_camiseta, is_wide=True)

    BACKS    = ["Medio Scrum", "Apertura", "Centro", "Wing", "Full Back"]
    FORWARDS = ["Pilar izquierdo", "Pilar derecho", "Hooker", "Segunda Linea", "Ala", "Octavo"]
    grupo_jug = "Backs" if puesto_jug in BACKS else "Forwards"

    df_pos    = df_raw[df_raw["Position Name"] == puesto_jug]
    perf_pos  = calc_perfil_competitivo(df_pos)

    grupo_puestos = BACKS if grupo_jug == "Backs" else FORWARDS
    df_grupo      = df_raw[df_raw["Position Name"].isin(grupo_puestos)]
    perf_grupo    = calc_perfil_competitivo(df_grupo)

    METRICAS_RADAR = [c for c in COLS if c != "Contact Involvement Average BiG Time"]
    labels = [METRICAS[c][0] for c in METRICAS_RADAR]

    def normalizar(perf_val, ref):
        return [
            min(round((perf_val[c] / ref[c] * 100), 1), 150) if ref[c] and not np.isnan(ref[c]) and not np.isnan(perf_val[c]) else 0
            for c in METRICAS_RADAR
        ]

    vals_jug   = normalizar(perf, perf_pos)
    vals_pos   = [100] * len(METRICAS_RADAR)
    vals_grupo = normalizar(perf_grupo, perf_pos)

    import plotly.graph_objects as go
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=vals_pos   + [vals_pos[0]],   theta=labels + [labels[0]], name="Promedio posición", line=dict(color="#FF00FF", dash="dash"), fill="none"))
    fig_radar.add_trace(go.Scatterpolar(r=vals_grupo + [vals_grupo[0]], theta=labels + [labels[0]], name=grupo_jug,           line=dict(color="#00CC44"),              fill="toself", fillcolor="rgba(0,204,68,0.1)"))
    fig_radar.add_trace(go.Scatterpolar(r=vals_jug   + [vals_jug[0]],  theta=labels + [labels[0]], name=jugador_sel,          line=dict(color="#00A8CC"),              fill="toself", fillcolor="rgba(0,168,204,0.15)"))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0f1a28",
            radialaxis=dict(visible=True, range=[0, 150], tickfont=dict(color="#7a9ab5", size=8), gridcolor="#1e3048"),
            angularaxis=dict(tickfont=dict(color="white", size=10), gridcolor="#1e3048"),
        ),
        paper_bgcolor="#1a2535", plot_bgcolor="#1a2535",
        legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"),
        margin=dict(t=20, b=20, l=40, r=40),
        height=360,
    )

    col_card, col_radar = st.columns([1, 2])
    with col_card:
        st.markdown("<div class='fifa-grid'>" + html_card + "</div>", unsafe_allow_html=True)
    with col_radar:
        st.plotly_chart(fig_radar, use_container_width=True)



# ── Sección 2: Rendimiento en partido ────────────────────────────────────────
st.markdown('<div class="seccion-header">⚔️ Rendimiento en partido individual</div>', unsafe_allow_html=True)

s2_equipo = None
s2_puesto = None
s2_jugador = None
s2_participacion = "Sesión completa"

s2_col1, s2_col2, s2_col3, s2_col4 = st.columns([4, 2, 2, 2])

with s2_col1:
    st.markdown('<span class="filtro-label"></span>', unsafe_allow_html=True)
    s2_vista = st.radio("", ["Plantel", "Equipo", "Puesto", "Jugador"],
                        horizontal=True, label_visibility="collapsed", key="s2_vista")

with s2_col2:
    if s2_vista == "Jugador":
        jugadores_s2 = sorted(df_raw["Player Name"].dropna().unique())
        st.markdown('<span class="filtro-label">Jugador</span>', unsafe_allow_html=True)
        s2_jugador = st.selectbox("", jugadores_s2, label_visibility="collapsed", key="s2_ju")
    elif s2_vista == "Puesto":
        st.markdown('<span class="filtro-label">Puesto</span>', unsafe_allow_html=True)
        s2_puesto = st.selectbox("", list(GRUPOS_PUESTO.keys()), label_visibility="collapsed", key="s2_pu")
    elif s2_vista == "Equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        s2_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="s2_eq")

with s2_col3:
    if s2_vista in ("Jugador", "Puesto"):
        st.markdown('<span class="filtro-label">Participación</span>', unsafe_allow_html=True)
        s2_participacion = st.radio("", ["Sesión completa", "Solo 1 equipo"],
                                    horizontal=False, label_visibility="collapsed", key="s2_part")

with s2_col4:
    if s2_vista in ("Jugador", "Puesto") and s2_participacion == "Solo 1 equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        s2_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="s2_eq2")

df_md_all = df_raw[df_raw["MD"] == "MD"].copy()
if s2_equipo:
    df_md_eq = df_md_all[df_md_all["Equipo"] == s2_equipo].copy()
else:
    df_md_eq = df_md_all.copy()
if s2_vista == "Jugador" and s2_jugador:
    df_md_eq = df_md_eq[df_md_eq["Player Name"] == s2_jugador]
elif s2_vista == "Puesto" and s2_puesto:
    puestos_s2 = GRUPOS_PUESTO.get(s2_puesto, [])
    df_md_eq = df_md_eq[df_md_eq["Position Name"].isin(puestos_s2)]

fechas_unicas = sorted(df_md_eq["Fecha"].unique(), reverse=True)
opciones_partidos = {}
total_fechas = len(fechas_unicas)
# Número real de fecha basado en todas las fechas del equipo
todas_fechas_eq = sorted(df_raw[
    (df_raw["MD"] == "MD") & 
    (df_raw["Equipo"] == (s2_equipo or equipos_disp[0]))
]["Fecha"].unique())
num_fecha_map = {f: i+1 for i, f in enumerate(todas_fechas_eq)}

for fecha in fechas_unicas:
    rival = df_md_eq[df_md_eq["Fecha"] == fecha]["Rival"].iloc[0] if "Rival" in df_md_eq.columns else "—"
    num = num_fecha_map.get(fecha, "?")
    label = "Fecha " + str(num) + " — " + pd.Timestamp(fecha).strftime("%d/%m") + " vs " + str(rival)
    opciones_partidos[label] = fecha

if len(opciones_partidos) == 0:
    st.warning("No hay partidos MD disponibles para esta selección.")
else:
    fp1, _ = st.columns([3, 4])
    with fp1:
        st.markdown('<span class="filtro-label">Partido</span>', unsafe_allow_html=True)
        if s2_vista == "Jugador":
            partidos_sel = st.multiselect("", list(opciones_partidos.keys()),
                                        default=[list(opciones_partidos.keys())[0]],
                                        label_visibility="collapsed", key="partido_multi")
            if not partidos_sel:
                st.warning("Seleccioná al menos un partido.")
                st.stop()
            fechas_sel = sorted([opciones_partidos[p] for p in partidos_sel], reverse=True)
        else:
            partido_label = st.selectbox("", list(opciones_partidos.keys()),
                                        label_visibility="collapsed", key="partido_single")
            fechas_sel = [opciones_partidos[partido_label]]

    df_partido = df_md_eq[df_md_eq["Fecha"].isin(fechas_sel)].copy()
    

    if df_partido.empty:
        st.warning("Sin jugadores para esta selección en el partido.")
    else:
        df_hist = df_raw[~df_raw["Fecha"].isin(fechas_sel)]

        # Perfil por posición como fallback cuando el jugador tiene menos de 6 partidos
        perfiles_posicion = {}
        for pos in df_raw["Position Name"].dropna().unique():
            perfiles_posicion[pos] = calc_perfil_competitivo(df_hist[df_hist["Position Name"] == pos])

        todos_jugs = sorted(df_partido["Player Name"].dropna().unique())
        perfiles_hist = {}
        for j in todos_jugs:
            perf = calc_perfil_competitivo(df_hist[df_hist["Player Name"] == j])
            if perf.isna().all():
                pos_jug = df_hist[df_hist["Player Name"] == j]["Position Name"].dropna()
                pos_jug = pos_jug.iloc[0] if len(pos_jug) > 0 else None
                perf = perfiles_posicion.get(pos_jug, perf)
            perfiles_hist[j] = perf

        cabecera2 = "<tr><th class='col-jugador'>Jugador</th><th>Intensidad</th>"
        for col, (label, unidad, icono, _) in METRICAS.items():
            cabecera2 += "<th>" + icono + "<br>" + label + "</th>"
        cabecera2 += "</tr>"

        DIAS_TABLA = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        filas2 = ""

        df_partido["Fecha"] = pd.to_datetime(df_partido["Fecha"])
        fechas_sel = [pd.to_datetime(f) for f in fechas_sel]

        if s2_vista == "Jugador":
            iteracion = [(fecha_p, jug) 
                         for fecha_p in fechas_sel 
                         for jug in sorted(df_partido[df_partido["Fecha"] == pd.to_datetime(fecha_p)]["Player Name"].dropna().unique())]
        else:
            iteracion = [(fechas_sel[0], jug) for jug in todos_jugs]

        for fecha_p, jug in iteracion:
            fila_df    = df_partido[(df_partido["Player Name"] == jug) & (df_partido["Fecha"] == pd.to_datetime(fecha_p))]
            puesto_jug = fila_df["Position Name"].iloc[0] if "Position Name" in fila_df.columns and len(fila_df) > 0 else "—"
            perf_jug   = perfiles_hist.get(jug, pd.Series({col: np.nan for col in COLS}))

            # Calcular score de intensidad
            METRICAS_INTENSIDAD = ["Minutos", "Distancia Total", "AI 18 Km/h", "DT + 25 Km/h",
                                    "+25 Km/h #", "Acel 2,5 m/ss #", "Desacel -2,5 m/ss #",
                                    "Contact Involvement Total Count Avg"]
            puntos_intensidad = 0
            for m in METRICAS_INTENSIDAD:
                val_m = fila_df[m].sum() if m != "Minutos" else fila_df["Minutos"].sum()
                bench_m = perf_jug[m]
                if bench_m and not np.isnan(bench_m) and bench_m > 0:
                    pct_m = val_m / bench_m
                    if pct_m >= 0.90:   puntos_intensidad += 4
                    elif pct_m >= 0.80: puntos_intensidad += 3
                    elif pct_m >= 0.60: puntos_intensidad += 2
                    else:                puntos_intensidad += 1
            score_intensidad = round((puntos_intensidad / 28) * 100)

            fecha_fila = fila_df["Fecha"].iloc[0] if len(fila_df) > 0 else fechas_sel[0]
            # Buscar el label del partido correspondiente a fecha_p
            label_partido = next((k for k, v in opciones_partidos.items() if pd.to_datetime(v) == pd.to_datetime(fecha_fila)), "")
            fecha_str2 = label_partido if label_partido else ""
            fila2 = "<tr><td class='col-jugador'>" + jug + ("<br><span style='font-size:10px;color:#7a9ab5;'>" + fecha_str2 + "</span>" if fecha_str2 else "") + "</td><td style='color:#7a9ab5;font-size:11px;text-align:center;font-weight:700;'>" + str(score_intensidad) + "</td>"

            for col, (_, _, _, inverso) in METRICAS.items():
                if col == "Minutos":
                    val_partido = fila_df[col].sum()
                elif col in ("Maximum Velocity", "Max Vel (% Max)"):
                    val_partido = fila_df[col].max()
                else:
                    val_partido = fila_df[col].sum()
                bench_jug   = perf_jug[col]
                pct = val_partido / bench_jug if bench_jug and not np.isnan(bench_jug) and val_partido > 0 else None
                color   = color_pct(pct, inverso)
                bg      = color + "22"
                pct_str = (str(round(pct*100)) + "%") if pct is not None else "—"
                fila2 += (
                    "<td><span class='celda-valor' style='background:" + bg + "; color:" + color + ";'>"
                    + (fmt2(val_partido) if col == "Maximum Velocity" else fmt(val_partido)) + "<br>"
                    + "<span style='font-size:10px;opacity:0.8;'>" + pct_str + "</span>"
                    + "</span></td>"
                )
            fila2 += "</tr>"
            filas2 += fila2

        st.markdown(
            "<div style='overflow-x:auto;max-height:750px;overflow-y:auto;'><table class='tabla-semaforo'>" + cabecera2 + filas2 + "</table></div>",
            unsafe_allow_html=True
        )

        st.markdown('<div style="font-size:15px;color:#4a6a80;text-align:right;margin-top:4px;">↕ Desplazá para ver más filas</div>', unsafe_allow_html=True)
st.divider()
