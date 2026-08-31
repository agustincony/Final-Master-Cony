import streamlit as st
import base64, os
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="CASI - Análisis de rendimiento",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from simular_contactos import simular_contactos

@st.cache_data
def cargar_excel():
    df = pd.read_parquet("totales_gps.parquet")
    df, _ = simular_contactos(df)
    return df

if "df_excel" not in st.session_state:
    st.session_state["df_excel"] = cargar_excel()

def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64  = img_base64("LOGO_CASI_SIN_FONDO.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:62px; width:auto;">' if logo_b64 else "⚡"

st.markdown(f"""
<style>
.topbar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 99999;
    background: #0f1a28;
    border-bottom: 3px solid #00A8CC;
    height: 72px;
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 16px;
}}
.topbar-logo    {{ display: flex; align-items: center; }}
.topbar-divider {{ width: 1px; height: 42px; background: #2a4060; margin: 0 16px; }}
.topbar-club    {{ font-size: 18px; font-weight: 900; color: white; letter-spacing: 1px; text-transform: uppercase; }}
.topbar-sub     {{ font-size: 13px; font-weight: 600; color: #00A8CC; letter-spacing: 2px; text-transform: uppercase; }}
.topbar-page    {{ font-size: 13px; font-weight: 700; color: #7a9ab5; letter-spacing: 2px; text-transform: uppercase; }}
header[data-testid="stHeader"] {{ display: none !important; }}
.stApp {{ background-color: #1a2535; color: white; min-width: 1200px !important; }}
.block-container {{ padding-top: 30px !important; padding-left: 2rem !important; padding-right: 2rem !important; }}
section[data-testid="stSidebar"] {{ background-color: #0f1a28 !important; margin-top: 72px !important; }}
section[data-testid="stSidebar"] span {{ color: white !important; }}
section[data-testid="stSidebar"] p    {{ color: white !important; }}
div[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
section[data-testid="collapsedControl"] {{ display: none !important; }}
section[data-testid="collapsedControl"] svg {{ stroke: white !important; }}
.seccion-header {{ font-size: 11px; font-weight: 800; letter-spacing: 2px; color: #ffffff;
    background: #0f1a28; border-left: 4px solid #00A8CC; padding: 8px 14px;
    margin: 0 0 10px 0; text-transform: uppercase; border-radius: 0 4px 4px 0; }}
.stat-label {{ font-size: 10px; font-weight: 700; color: #7a9ab5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }}
.stat-value {{ font-size: 22px; font-weight: 900; color: white; }}
.stat-unit  {{ font-size: 12px; font-weight: 600; color: #4a6a80; margin-left: 3px; }}
.fifa-grid {{ display: flex; flex-wrap: wrap; gap: 24px; padding: 10px 0; }}
.fifa-card {{
    width: 220px; position: relative; padding: 14px 14px 80px 14px;
    font-family: 'Arial Black', 'Impact', sans-serif;
    box-shadow: 0 8px 32px rgba(0,0,0,0.7), 0 2px 4px rgba(255,220,80,0.3);
    background:
        repeating-conic-gradient(from 0deg at 50% 110%, rgba(255,255,255,0.07) 0deg, transparent 2deg, transparent 5deg, rgba(255,255,255,0.04) 6deg, transparent 8deg),
        linear-gradient(160deg, #f7e87a 0%, #d4a017 15%, #f0cc50 30%, #c8900a 45%, #f5d848 55%, #b8780a 70%, #e8c040 82%, #a06010 92%, #c8a030 100%);
    clip-path: path('M 20 0 Q 0 0 0 20 L 0 420 Q 0 440 18 440 Q 85 440 110 460 Q 135 440 202 440 Q 220 440 220 420 L 220 20 Q 220 0 200 0 Z');
}}
.fifa-card-wide {{
    width: 220px; padding: 16px 16px 80px 16px;
    clip-path: path('M 20 0 Q 0 0 0 20 L 0 420 Q 0 440 18 440 Q 85 440 110 460 Q 135 440 202 440 Q 220 440 220 420 L 220 20 Q 220 0 200 0 Z');
    overflow: visible;
}}
.fifa-shine {{ position: absolute; top: 0; left: 0; right: 0; height: 55%; border-radius: 12px 12px 60% 60% / 12px 12px 40% 40%; background: radial-gradient(ellipse at 50% 0%, rgba(255,255,255,0.28) 0%, transparent 70%); pointer-events: none; z-index: 1; }}
.fifa-rays {{ position: absolute; bottom: -10%; left: 50%; transform: translateX(-50%); width: 300%; height: 160%; background: repeating-conic-gradient(from 0deg at 50% 100%, rgba(255,255,255,0.06) 0deg 2deg, transparent 2deg 8deg); pointer-events: none; z-index: 0; }}
.fifa-card-inner {{ position: relative; z-index: 2; }}
.fifa-top {{ display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 2px; }}
.fifa-rating {{ font-size: 16px; font-weight: 900; color: #000000; line-height: 1; letter-spacing: -1px; text-shadow: 0 1px 0 rgba(255,255,255,0.35); }}
.fifa-rating-wide {{ font-size: 20px; }}
.fifa-pos {{ font-size: 11px; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 1px; margin-top: -6px; margin-bottom: 4px; }}
.fifa-pos-wide {{ font-size: 14px; }}
.fifa-avatar {{ width: 100%; height: 20px; background: linear-gradient(170deg, rgba(255,220,80,0.3) 0%, rgba(160,90,0,0.4) 100%); border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-bottom: 6px; border: 1px solid rgba(0,0,0,0.15); }}
.fifa-avatar-wide {{ height: 180px; }}
.fifa-initials {{ font-size: 32px; font-weight: 900; color: rgba(60,30,0,0.45); letter-spacing: -1px; }}
.fifa-initials-wide {{ font-size: 46px; }}
.fifa-name {{ font-size: 11px; font-weight: 900; color: #000000; text-transform: uppercase; letter-spacing: 0.8px; text-align: center; width: 100%; border-top: 1px solid rgba(0,0,0,0.18); border-bottom: 1px solid rgba(0,0,0,0.18); padding: 4px 0; margin-bottom: 6px; text-shadow: 0 1px 0 rgba(255,255,255,0.2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.fifa-name-wide {{ font-size: 14px; }}
.fifa-stats-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3px 8px; }}
.fifa-stat-item {{ display: flex; flex-direction: column; align-items: center; }}
.fifa-stat-val {{ font-size: 13px; font-weight: 900; line-height: 1; }}
.fifa-stat-val-wide {{ font-size: 16px; }}
.fifa-stat-label {{ font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
.fifa-stat-label-wide {{ font-size: 10px; }}
</style>

<div class="topbar">
    <div class="topbar-logo">{logo_html}</div>
    <div class="topbar-divider"></div>
    <span class="topbar-club">Club Atlético de San Isidro</span>
    <div class="topbar-divider"></div>
    <span class="topbar-sub">Análisis de rendimiento</span>
    <div class="topbar-divider"></div>
    <span class="topbar-page">Resuman General</span>
</div>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components
components.html("""
<script>
window.parent.document.querySelectorAll('[data-testid="collapsedControl"]').forEach(el => {
    if (el.getAttribute('aria-expanded') === 'false') {
        el.click();
    }
});
</script>
""", height=0)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════
COLS_DIST_80 = [
    "80% Velocity Band 5 Total Distance (Set 2)",
    "90% Velocity Band 6 Total Distance (Set 2)",
    "95% Velocity Band 7 Total Distance (Set 2)",
    "100% Velocity Band 8 Total Distance (Set 2)",
]
COL_DIST_80 = "Dist >80% Vel Max"
COLS_EFF_80 = [
    "80% Velocity Band 5 Total Effort Count (Set 2)",
    "90% Velocity Band 6 Total Effort Count (Set 2)",
    "95% Velocity Band 7 Total Effort Count (Set 2)",
    "100% Velocity Band 8 Total Effort Count (Set 2)",
]
COL_EFF_80 = "# >80% Vel Max"

EJES = {
    "Volumen":       ["Distancia Total"],
    "Intensidad":    ["AI 18 Km/h"],
    "Neuromuscular": ["Acel 2,5 m/ss #", "Desacel -2,5 m/ss #"],
    "Impactos":      ["Contact Involvement Total Count Avg"],
}
COLS_EJES = list(EJES.keys())

SCORING_METRICAS = {
    "Total Player Load":                   ("Player Load", 0.20, None),
    "# ACDC":                              ("ACDC",        0.25, None),
    "Contact Involvement Total Count Avg": ("Contactos",   0.30, None),
    "Distancia Explosiva":                 ("Dist Expl",   0.25, None),
}

DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
NUMEROS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

@st.cache_data
def cargar_imagenes():
    df_img = pd.read_excel("Imagenes perfiles.xlsx")
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
        "Segundo Roy":                "Segundo Roy",
    }
    resultado = {}
    for _, row in df_img.iterrows():
        nombre_excel = row["Jugador"]
        url = row["URL"]
        if pd.isna(url): continue
        nombre_gps = MAPEO_NOMBRES.get(nombre_excel, nombre_excel)
        resultado[nombre_gps] = url
    return resultado

IMAGENES_JUGADORES = cargar_imagenes()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def score_ratio(r):
    if r is None or (isinstance(r, float) and np.isnan(r)): return 1
    if r >= 1.50: return 3
    if r >= 1.30: return 2
    return 1

UMBRAL_VERDE = 6
UMBRAL_AM    = 8

def calcular_score_ejes(row):
    total = sum(row[f"score_{eje}"] for eje in COLS_EJES)
    if total <= UMBRAL_VERDE: return total, "#00CC44", "Óptimo"
    if total <= UMBRAL_AM:    return total, "#FFD000", "Precaución"
    return total, "#FF0000", "Alerta"

def calc_score_row(row, max_dia):
    score = 0
    for col, (_, peso, _) in SCORING_METRICAS.items():
        val = row.get(col, np.nan)
        if pd.isna(val): continue
        ref = max_dia.get(col, 1)
        norm = min(val / ref, 1.0) if ref > 0 else 0
        score += norm * peso
    return round(score * 100)

# ══════════════════════════════════════════════════════════════════════════════
# PREPARAR DATOS — usa session_state ya cargado por cargar_excel()
# ══════════════════════════════════════════════════════════════════════════════
df_raw = st.session_state["df_excel"].copy()
df_raw = df_raw[
    (df_raw["Period Name"] == "Session") &
    (df_raw["Period Tags"] != "Diferenciado")
].copy()
df_raw["Fecha"] = pd.to_datetime(df_raw["Fecha"])
df_raw["Position Name"] = df_raw["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
df_raw[COL_DIST_80] = df_raw[COLS_DIST_80].fillna(0).sum(axis=1)
df_raw[COL_EFF_80]  = df_raw[COLS_EFF_80].fillna(0).sum(axis=1)

# ── EWMA ejes (para alarmas) ──────────────────────────────────────────────────
@st.cache_data
def calcular_ewma_ejes(df):
    cols_base = sorted({c for cols in EJES.values() for c in cols})
    agg = df.groupby(["Player Name", "Position Name", "Fecha"])[cols_base].sum().reset_index()
    for eje, cols in EJES.items():
        agg[eje] = agg[cols].sum(axis=1)
    resultados = []
    for jugador, g in agg.groupby("Player Name"):
        g = g.sort_values("Fecha").copy()
        idx = pd.date_range(g["Fecha"].min(), g["Fecha"].max(), freq="D")
        g_diario = g.set_index("Fecha").reindex(idx)
        for eje in COLS_EJES:
            g_diario[eje] = g_diario[eje].fillna(0)
        pos = g["Position Name"].iloc[-1]
        for eje in COLS_EJES:
            serie        = g_diario[eje].astype(float)
            ewma_aguda   = serie.ewm(span=7,  adjust=False).mean()
            ewma_cronica = serie.ewm(span=28, adjust=False).mean()
            for fecha in g["Fecha"]:
                if fecha not in ewma_aguda.index: continue
                ag = ewma_aguda[fecha]; cr = ewma_cronica[fecha]
                resultados.append({
                    "Player Name":   jugador,
                    "Position Name": pos,
                    "Fecha":         fecha,
                    "Eje":           eje,
                    "Ratio":         ag / cr if cr > 0 else np.nan,
                })
    return pd.DataFrame(resultados)

df_ewma_ejes = calcular_ewma_ejes(df_raw)

# ── Última sesión de entrenamiento ────────────────────────────────────────────
df_entreno       = df_raw.copy()
ultima_fecha_ent = df_entreno["Fecha"].max() if not df_entreno.empty else None

# ── Último partido ────────────────────────────────────────────────────────────
df_partidos     = df_raw[df_raw["MD"] == "MD"].copy()
ultima_fecha_md = df_partidos["Fecha"].max() if not df_partidos.empty else None

# ── Última fecha EWMA ─────────────────────────────────────────────────────────
ultima_fecha_ewma = df_ewma_ejes["Fecha"].max() if not df_ewma_ejes.empty else None

# ── Calcular alarmas ──────────────────────────────────────────────────────────
alarmas_html = ""
n_alerta = n_precaucion = n_optimo = 0

if ultima_fecha_ewma is not None:
    jugs_28 = df_raw[
        (df_raw["MD"] != "MD") &
        (df_raw["Fecha"] >= ultima_fecha_ewma - pd.Timedelta(days=28)) &
        (df_raw["Fecha"] <= ultima_fecha_ewma)
    ]["Player Name"].unique()

    df_fecha_ewma = df_ewma_ejes[
        (df_ewma_ejes["Fecha"] == ultima_fecha_ewma) &
        (df_ewma_ejes["Player Name"].isin(jugs_28))
    ].copy()

    if not df_fecha_ewma.empty:
        pivot = df_fecha_ewma.pivot_table(
            index=["Player Name", "Position Name"], columns="Eje", values="Ratio"
        ).reset_index()
        for eje in COLS_EJES:
            if eje not in pivot.columns:
                pivot[eje] = np.nan
            pivot[f"score_{eje}"] = pivot[eje].apply(score_ratio)
        pivot[["Score_Total", "Color_Score", "Label_Score"]] = pivot.apply(
            lambda row: pd.Series(calcular_score_ejes(row)), axis=1
        )
        # Contar sesiones (entrenamiento + partido) de cada jugador en los últimos 28 días
        sesiones_28 = df_raw[
            (df_raw["Fecha"] >= ultima_fecha_ewma - pd.Timedelta(days=28)) &
            (df_raw["Fecha"] <= ultima_fecha_ewma)
        ].groupby("Player Name")["Fecha"].nunique()

        jugadores_activos = sesiones_28[sesiones_28 >= 8].index

        n_alerta     = len(pivot[(pivot["Color_Score"] == "#FF0000") & (pivot["Player Name"].isin(jugadores_activos))])
        n_precaucion = len(pivot[(pivot["Color_Score"] == "#FFD000") & (pivot["Player Name"].isin(jugadores_activos))])
        n_optimo     = len(pivot[(pivot["Color_Score"] == "#00CC44") & (pivot["Player Name"].isin(jugadores_activos))])

        en_rojo = pivot[
            (pivot["Color_Score"] == "#FF0000") &
            (pivot["Player Name"].isin(jugadores_activos))
        ].sort_values("Score_Total", ascending=False)
        alarmas_html = '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:4px;">'
        for _, row in en_rojo.iterrows():
            alarmas_html += (
                f'<div style="background:#1a0a0a;border:1px solid #FF0000;border-radius:4px;'
                f'padding:4px 6px;text-align:center;">'
                f'<span style="font-size:10px;font-weight:700;color:#FF0000;">{row["Player Name"]}</span>'
                f'</div>'
            )
        alarmas_html += '</div>'

# ── Datos última sesión ───────────────────────────────────────────────────────
info_sesion = {}
top3_vel    = []

if ultima_fecha_ent is not None:
    df_ult = df_entreno[df_entreno["Fecha"] == ultima_fecha_ent].copy()
    df_ult_agg = df_ult.groupby("Player Name").agg(
        minutos=("Minutos", "sum"),
        dist=("Distancia Total", "sum"),
        hsr=("AI 18 Km/h", "sum"),
    ).reset_index()
    df_ult_agg = df_ult_agg[df_ult_agg["minutos"] > 30]

    tipo_md        = df_ult["MD"].iloc[0] if not df_ult.empty else "—"
    equipos_sesion = df_ult["Equipo"].dropna().unique().tolist() if "Equipo" in df_ult.columns else []
    dia_str        = DIAS_ES[ultima_fecha_ent.weekday()]

    info_sesion = {
        "fecha":     f'{dia_str} {ultima_fecha_ent.strftime("%d/%m/%Y")}',
        "tipo":      tipo_md,
        "equipos":   " · ".join(equipos_sesion) if equipos_sesion else "—",
        "n_jug":     len(df_ult_agg),
        "dist_prom": round(df_ult_agg["dist"].mean()) if not df_ult_agg.empty else 0,
        "hsr_prom":  round(df_ult_agg["hsr"].mean())  if not df_ult_agg.empty else 0,
        "min_prom":  round(df_ult_agg["minutos"].mean()) if not df_ult_agg.empty else 0,
    }

    top3 = df_ult.groupby("Player Name")["Maximum Velocity"].max().reset_index()
    top3 = top3.sort_values("Maximum Velocity", ascending=False).head(3).reset_index(drop=True)
    top3_vel = top3.to_dict("records")

    # ── Score demanda última sesión ───────────────────────────────────────────────
score_sesion_prom = None

if ultima_fecha_ent is not None:
    cols_sc_ent = [c for c in SCORING_METRICAS if c in df_entreno.columns]
    if cols_sc_ent:
        agg_ent = {c: "sum" for c in cols_sc_ent}
        agg_ent["Minutos"] = "sum"
        df_ent_ult = df_entreno[df_entreno["Fecha"] == ultima_fecha_ent].groupby("Player Name").agg(agg_ent).reset_index()
        df_ent_ult = df_ent_ult[df_ent_ult["Minutos"] > 30]
        if not df_ent_ult.empty:
            max_dia_ent = {col: df_ent_ult[col].max() for col in cols_sc_ent}
            df_ent_ult["Score"] = df_ent_ult.apply(lambda row: calc_score_row(row.to_dict(), max_dia_ent), axis=1)
            score_sesion_prom = round(df_ent_ult["Score"].mean())

# ── Top 5 ranking último partido ─────────────────────────────────────────────
top5_ranking   = []
rival_ultimo   = "—"
fecha_md_label = "—"

if ultima_fecha_md is not None:
    df_md_ult        = df_partidos[df_partidos["Fecha"] == ultima_fecha_md].copy()
    cols_disponibles = [c for c in SCORING_METRICAS if c in df_md_ult.columns]

    if cols_disponibles:
        agg_cols = {c: "sum" for c in cols_disponibles}
        agg_cols["Minutos"] = "sum"
        df_md_agg = df_md_ult.groupby("Player Name").agg(agg_cols).reset_index()
        df_md_agg = df_md_agg[df_md_agg["Minutos"] > 30]
        max_dia   = {col: df_md_agg[col].max() for col in cols_disponibles}
        df_md_agg["Score"] = df_md_agg.apply(lambda row: calc_score_row(row.to_dict(), max_dia), axis=1)
        top5 = df_md_agg.sort_values("Score", ascending=False).head(5).reset_index(drop=True)
        top5_ranking = top5[["Player Name", "Score"]].to_dict("records")

    if "Rival" in df_md_ult.columns and not df_md_ult.empty:
        rival_ultimo = df_md_ult["Rival"].iloc[0] or "—"
    dia_md         = DIAS_ES[ultima_fecha_md.weekday()]
    fecha_md_label = f'{dia_md} {ultima_fecha_md.strftime("%d/%m/%Y")}'

    # Datos del partido del jugador #1 para la card FIFA
COLS_PERFIL_CARD = [
    "Minutos", "Maximum Velocity", "Distancia Total",
    "AI 18 Km/h", "DT + 25 Km/h", "+25 Km/h #",
    "Acel 2,5 m/ss #", "Desacel -2,5 m/ss #",
    "Contact Involvement Total Count Avg",
    "Contact Involvement Average BiG Time",
]
METRICAS_CARD = [
    ("Distancia Total",                     "Dist",  "mts"),
    ("AI 18 Km/h",                          "HSR",   "mts"),
    ("DT + 25 Km/h",                        "Sprint","mts"),
    ("+25 Km/h #",                          "N°Spr", ""),
    ("Acel 2,5 m/ss #",                     "Acel",  ""),
    ("Desacel -2,5 m/ss #",                 "Decel", ""),
    ("Contact Involvement Total Count Avg", "Cont",  ""),
    ("Maximum Velocity",                    "VMax",  "km/h"),
    ("Minutos",                             "Min",   "′"),
    ("Contact Involvement Average BiG Time", "BiG",   "")
]

card_html = ""
if top5_ranking and ultima_fecha_md is not None:
    jugador_1 = top5_ranking[0]["Player Name"]
    score_1   = top5_ranking[0]["Score"]
    df_card   = df_partidos[
        (df_partidos["Fecha"] == ultima_fecha_md) &
        (df_partidos["Player Name"] == jugador_1)
    ].copy()
    cols_disp = [c for c in COLS_PERFIL_CARD if c in df_card.columns]
    if not df_card.empty:
        agg = {c: "max" if c in ("Maximum Velocity",) else "sum" for c in cols_disp}
        row_card = df_card.groupby("Player Name").agg(agg).reset_index().iloc[0]
        pos_card = df_card["Position Name"].iloc[0] if "Position Name" in df_card.columns else ""
        ini      = "".join([p[0].upper() for p in jugador_1.split()[:2]])
        short    = jugador_1.split()[0][0] + ". " + jugador_1.split()[-1] if len(jugador_1.split()) > 1 else jugador_1

        def fmt_card(val, es_kmh=False):
            if pd.isna(val): return "—"
            if es_kmh: return f"{val:.1f}".replace(".", ",")
            return f"{int(round(val)):,}".replace(",", ".")

        stats_html = (
            '<div style="display:flex;justify-content:space-around;margin-bottom:4px;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;min-width:44px;"><span style="font-size:13px;font-weight:900;color:#fff;line-height:1;">{fmt_card(row_card.get("Minutos",np.nan))}</span><span style="font-size:6px;font-weight:700;color:#000000;text-transform:uppercase;letter-spacing:0.5px;">Min</span></div>'
            f'<div style="display:flex;flex-direction:column;align-items:center;min-width:44px;"><span style="font-size:13px;font-weight:900;color:#fff;line-height:1;">{fmt_card(row_card.get("Maximum Velocity",np.nan),es_kmh=True)}</span><span style="font-size:6px;font-weight:700;color:#000000;text-transform:uppercase;letter-spacing:0.5px;">Vel Max</span></div>'
            '</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:3px 8px;margin-bottom:4px;">'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("Distancia Total",np.nan))}</span><span class="fifa-stat-label" style="color:#000000;">Dist</span></div>'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("AI 18 Km/h",np.nan))}</span><span class="fifa-stat-label" style="color:#000000;">HSR</span></div>'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("DT + 25 Km/h",np.nan))}</span><span class="fifa-stat-label" style="color:#000000;">Sprint</span></div>'
            '</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px 8px;margin-bottom:4px;">'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("Acel 2,5 m/ss #",np.nan))}</span><span class="fifa-stat-label" style="color:#000000;">Acel</span></div>'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("Desacel -2,5 m/ss #",np.nan))}</span><span class="fifa-stat-label" style="color:#000000;">Decel</span></div>'
            '</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px 8px;">'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("Contact Involvement Total Count Avg",np.nan))}</span><span class="fifa-stat-label" style="color:#000000;">Cont</span></div>'
            f'<div class="fifa-stat-item"><span class="fifa-stat-val" style="color:white;">{fmt_card(row_card.get("Contact Involvement Average BiG Time",np.nan),es_kmh=True)}</span><span class="fifa-stat-label" style="color:#000000;">BiG</span></div>'
            '</div>'
        )

        avatar_html = (
            f'<div class="fifa-avatar fifa-avatar-wide" style="padding:2px;">'
            f'<img src="{IMAGENES_JUGADORES[jugador_1]}" style="width:100%;height:170px;object-fit:cover;border-radius:4px;object-position:center 5%;">'
            f'</div>'
            if jugador_1 in IMAGENES_JUGADORES else
            f'<div class="fifa-avatar fifa-avatar-wide">'
            f'<span class="fifa-initials fifa-initials-wide">{ini}</span>'
            f'</div>'
        )

        card_html = (
            '<div class="fifa-card fifa-card-wide" style="width:200px;margin-left:60px;">'
            '<div class="fifa-rays"></div>'
            '<div class="fifa-shine"></div>'
            '<div class="fifa-card-inner">'
            '<div class="fifa-top" style="display:flex;flex-direction:row;justify-content:space-between;align-items:flex-start;width:100%;">'
            f'<div><div class="fifa-rating fifa-rating-wide">{score_1}</div>'
            f'<div class="fifa-pos fifa-pos-wide">{pos_card}</div></div>'
            f'<img src="data:image/png;base64,{logo_b64}" style="height:52px;opacity:0.7;">'
            '</div>'
            + avatar_html
            + f'<div class="fifa-name fifa-name-wide">{short}</div>'
            + stats_html
            + '</div></div>'
        )

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════

# ── FILA 1: Alarmas + Última sesión ──────────────────────────────────────────
col_izq, col_der = st.columns(2, gap="medium")

col_izq, col_der = st.columns(2, gap="medium")

# ── FILA 1: Alarmas + Última sesión ──────────────────────────────────────────
col_izq, col_der = st.columns(2, gap="medium")

with col_izq:
    if info_sesion:
        st.markdown(
            f'<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:8px;padding:14px 16px;">'
            f'<div style="border-left:4px solid #00A8CC;padding-left:12px;margin-bottom:12px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div style="font-size:18px;font-weight:900;color:#FFFFFF;text-transform:uppercase;letter-spacing:2px;">📋 Última sesión</div>'
            f'<div style="display:flex;align-items:center;gap:10px;">'
            f'<span style="font-size:20px;font-weight:900;color:white;">{info_sesion.get("fecha","—")}</span>'
            f'<span style="font-size:20px;font-weight:900;color:white;">{info_sesion.get("tipo","—")}</span>'
            f'</div></div></div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;text-align:center;">'
            f'<div><div style="font-size:11px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">Min. prom.</div>'
            f'<div style="font-size:22px;font-weight:900;color:white;">{info_sesion.get("min_prom","—")}<span style="font-size:11px;color:#4a6a80;">′</span></div></div>'
            f'<div><div style="font-size:11px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">Dist. prom.</div>'
            f'<div style="font-size:22px;font-weight:900;color:white;">{info_sesion.get("dist_prom","—"):,}<span style="font-size:11px;color:#4a6a80;">m</span></div></div>'
            f'<div><div style="font-size:11px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">HSR prom.</div>'
            f'<div style="font-size:22px;font-weight:900;color:white;">{info_sesion.get("hsr_prom","—")}<span style="font-size:11px;color:#4a6a80;">m</span></div></div>'
            f'<div><div style="font-size:11px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">Alertas</div>'
            f'<div style="font-size:22px;font-weight:900;color:#FF0000;">{n_alerta}</div></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        if alarmas_html:
            st.markdown(alarmas_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:6px;'
                'padding:24px;text-align:center;color:#00CC44;font-weight:700;font-size:10px;">'
                '✅ Sin jugadores en zona de alerta</div>',
                unsafe_allow_html=True
            )   
        if score_sesion_prom is not None:
            barras_html = ""
            if ultima_fecha_ent is not None and not df_ent_ult.empty:
                for col, (lbl, peso, _) in SCORING_METRICAS.items():
                    if col not in df_ent_ult.columns: continue
                    val_prom = df_ent_ult[col].mean()
                    mejor = df_ent_ult[col].max()
                    pct = min(val_prom / mejor * 100, 100) if mejor > 0 else 0
                    color_barra = "#00CC44" if pct >= 70 else ("#FFD000" if pct >= 40 else "#FF4444")
                    barras_html += (
                        f'<div style="margin-bottom:8px;">'
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                        f'<span style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:0.5px;">{lbl}</span>'
                        f'<span style="font-size:10px;font-weight:700;color:#ffffff;">{val_prom:.0f}</span>'
                        f'</div>'
                        f'<div style="background:#1e3048;border-radius:3px;height:5px;">'
                        f'<div style="background:{color_barra};width:{pct:.0f}%;height:5px;border-radius:3px;"></div>'
                        f'</div></div>'
                    )
            st.markdown(
                f'<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:10px;padding:12px;margin-top:10px;max-width:230px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
                f'<div>'
                f'<div style="font-size:13px;font-weight:800;letter-spacing:2px;color:#ffffff;text-transform:uppercase;">💪 Demanda física</div>'
                f'<div style="font-size:15px;font-weight:900;color:#ffffff;margin-top:3px;">'
                f'{"vs " + str(df_ult["Rival"].iloc[0]) if info_sesion.get("tipo") == "MD" and "Rival" in df_ult.columns and not df_ult["Rival"].isna().all() else info_sesion.get("tipo","—")}'
                f'</div>'
                f'<div style="font-size:9px;color:#4a6a80;margin-top:2px;">Promedio plantel</div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:48px;font-weight:900;color:#FFD000;line-height:1;">{score_sesion_prom}</div>'
                f'<div style="font-size:9px;color:#4a6a80;text-transform:uppercase;">score</div>'
                f'</div></div>'
                f'{barras_html}'
                f'</div>',
                unsafe_allow_html=True
            )     
    else:
        st.info("Sin datos de sesión disponibles.")

with col_der:
    st.markdown(
        f'<div class="seccion-header">🏆 Mayor desgaste físico · último partido · '
        f'<span style="color:#00A8CC;">vs {rival_ultimo}</span> · {fecha_md_label}</div>',
        unsafe_allow_html=True
    )
    if top5_ranking:
        c_card, c_rank = st.columns([1.3, 1], gap="small")
        with c_card:
            if card_html:
                st.markdown(card_html, unsafe_allow_html=True)
                with c_rank:
                    medallas_md = ["🥇", "🥈", "🥉"]
                    for i, row in enumerate(top5_ranking[:5]):
                        medalla = NUMEROS[i]
                        st.markdown(
                            f'<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:6px;'
                            f'padding:8px 12px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">'
                            f'<div style="display:flex;align-items:center;gap:8px;">'
                            f'<span style="font-size:16px;">{medalla}</span>'
                            f'<span style="font-size:12px;font-weight:700;color:white;">{row["Player Name"]}</span>'
                            f'</div>'
                            f'<span style="font-size:16px;font-weight:900;color:#00A8CC;">{int(row["Score"])}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    # Top 3 velocidades dentro del mismo espacio
                    if ultima_fecha_md is not None:
                        top3_md = df_partidos[df_partidos["Fecha"] == ultima_fecha_md].groupby("Player Name")["Maximum Velocity"].max().reset_index()
                        top3_md = top3_md.sort_values("Maximum Velocity", ascending=False).head(3).reset_index(drop=True)
                        medallas_vel = ["🥇", "🥈", "🥉"]
                        top3_md_html = '<div style="font-size:10px;font-weight:800;letter-spacing:2px;color:#7a9ab5;text-transform:uppercase;margin-bottom:6px;margin-top:12px;">⚡ Top 3 velocidades</div>'
                        top3_md_html += '<div style="display:flex;gap:6px;">'
                        for i, row in top3_md.iterrows():
                            apellido = row["Player Name"].split()[-1]
                            top3_md_html += (
                                f'<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:8px;'
                                f'padding:8px;flex:1;text-align:center;">'
                                f'<div style="font-size:14px;">{medallas_vel[i]}</div>'
                                f'<div style="font-size:10px;font-weight:700;color:white;margin-top:3px;">{apellido}</div>'
                                f'<div style="font-size:16px;font-weight:900;color:#00A8CC;">{str(round(row["Maximum Velocity"],1)).replace(".",",")}</div>'
                                f'<div style="font-size:8px;color:#4a6a80;">km/h</div>'
                                f'</div>'
                            )
                        top3_md_html += '</div>'
                        st.markdown(top3_md_html, unsafe_allow_html=True)



