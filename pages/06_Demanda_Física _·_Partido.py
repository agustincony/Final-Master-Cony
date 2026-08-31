import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64, os

st.set_page_config(page_title="Scoring Físico", layout="wide", initial_sidebar_state="expanded")

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
div[data-testid="stRadio"] label:has(input:checked) { background-color: #00A8CC !important; }
div[data-testid="stRadio"] label p { color: #ffffff !important; }
div[data-testid="stRadio"] > label:first-child { display: none !important; }
.filtro-label { font-size: 11px; color: #7a9ab5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; display: block; }
.seccion-header { font-size: 11px; font-weight: 800; letter-spacing: 2px; color: #ffffff; background: #0f1a28; border-left: 4px solid #00A8CC; padding: 8px 14px; margin: 20px 0 10px 0; text-transform: uppercase; border-radius: 0 4px 4px 0; }
.tabla-semaforo { width: 100%; border-collapse: collapse; font-size: 12px; }
.tabla-semaforo th { background: #0f1a28; color: #00A8CC; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; padding: 8px 6px; border-bottom: 2px solid #1e3048; text-align: center; }
.tabla-semaforo th.col-jugador { text-align: left; min-width: 140px; }
.tabla-semaforo td { padding: 6px 6px; border-bottom: 1px solid #1e3048; text-align: center; color: white; }
.tabla-semaforo td.col-jugador { text-align: left; color: #cce0f0; font-weight: 600; }
.tabla-semaforo tr:hover td { background: #1e3048 !important; }
.celda-valor { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; min-width: 52px; }
div[data-testid="stPopover"] > div > button {
    background-color: #0f1a28 !important; border: 1px solid #1e3048 !important;
    border-radius: 6px !important; color: white !important; font-size: 13px !important;
    width: 100% !important; text-align: left !important;
}
div[data-testid="stPopoverBody"] { background-color: #0f1a28 !important; border: 1px solid #1e3048 !important; border-radius: 8px !important; }
div[data-testid="stPopoverBody"] label { color: #cce0f0 !important; font-size: 13px !important; }
div[data-testid="stPopoverBody"] p { color: #7a9ab5 !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ────────────────────────────────────────────────────────────────
GRUPOS_PUESTO = {
    "Primeras":         ["Pilar izquierdo", "Pilar derecho", "Hooker"],
    "Segundas":         ["Segunda Linea"],
    "Terceras":         ["Ala", "Octavo"],
    "Pareja de medios": ["Medio Scrum", "Apertura"],
    "Centros":          ["Centro"],
    "3 del fondo":      ["Wing", "Full Back"],
}

EQUIPOS_ORDEN = ["Primera", "Intermedia", "Pre A"]

SCORING_METRICAS = {
    "Total Player Load":                     ("Player Load", 0.20, None),
    "# ACDC":                                ("ACDC",        0.25, None),
    "Contact Involvement Total Count Avg":   ("Contactos",   0.30, None),
    "Distancia Explosiva":                   ("Dist Expl",   0.25, None),
}

METRICAS_INTENSIDAD = ["Minutos", "Distancia Total", "AI 18 Km/h", "DT + 25 Km/h",
                        "+25 Km/h #", "Acel 2,5 m/ss #", "Desacel -2,5 m/ss #",
                        "Contact Involvement Total Count Avg"]

COLS_PERFIL = ["Minutos", "Maximum Velocity", "Max Vel (% Max)", "Distancia Total",
               "AI 18 Km/h", "DT + 25 Km/h", "+25 Km/h #", "Acel 2,5 m/ss #",
               "Desacel -2,5 m/ss #", "Contact Involvement Total Count Avg",
               "Contact Involvement Average BiG Time"]

COLORES_RIVALES = {
    "Los Tilos":  "#228B22", "Tilos": "#228B22", "Matreros": "#D32F2F",
    "Rosario": "#800020", "CUBA": "#002FA7", "Cuba": "#002FA7",
    "Regatas": "#1E3F66", "Biei": "#052B76", "La Plata": "#FFCC00",
    "Belgrano": "#5C4033", "Hindu": "#FFCC00", "Hindú": "#FFCC00",
    "SIC": "#6CB4EE", "Sic": "#6CB4EE", "Champagnat": "#003366",
    "Newman": "#4A0E17", "Alumni": "#E63946", "Plaza": "#8B0000",
}

def colores_rival(rival):
    for key, color in COLORES_RIVALES.items():
        if key.lower() in rival.lower():
            return color
    return "#00A8CC"

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

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

df_raw = cargar_datos()
_df_max = df_raw[df_raw["MD"] == "MD"].groupby(["Player Name", "Fecha"]).agg(
    {col: "sum" for col in SCORING_METRICAS.keys()}
).reset_index()
MAX_HIST = {col: _df_max[col].max() for col in SCORING_METRICAS.keys()}

def calc_perfil_competitivo(df):
    df_md = df[df["MD"] == "MD"].copy()
    agg_dict = {col: (col, "sum") for col in COLS_PERFIL if col not in ("Minutos", "Maximum Velocity", "Max Vel (% Max)")}
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
        return pd.Series({col: np.nan for col in COLS_PERFIL})
    perfil = {}
    for col in COLS_PERFIL:
        if col == "Minutos":
            perfil[col] = (por_dia["minutos"].max() + por_dia["minutos"].mean()) / 2
        elif col in ("Maximum Velocity", "Max Vel (% Max)"):
            perfil[col] = por_dia[col].max() if col in por_dia.columns else np.nan
        else:
            perfil[col] = (por_dia[col].max() + por_dia[col].mean()) / 2
    return pd.Series(perfil)

@st.cache_data
def calcular_todos_perfiles(_df):
    jugadores = _df["Player Name"].dropna().unique()
    cache = {}
    for jug in jugadores:
        df_jug = _df[_df["Player Name"] == jug]
        cache[jug] = calc_perfil_competitivo(df_jug)
    return cache

PERFILES_TODOS = calcular_todos_perfiles(df_raw)

def calc_score_row(row, max_dia=None):
    score = 0
    for col, (label, peso, max_hist) in SCORING_METRICAS.items():
        val = row[col]
        if pd.isna(val):
            continue
        ref = max_dia[col] if max_dia and col in max_dia and max_dia[col] > 0 else MAX_HIST.get(col, 1)
        norm = min(val / ref, 1.0) if ref > 0 else 0
        score += norm * peso
    return round(score * 100) if not np.isnan(score) else 0

def calc_intensidad(row, perf_jug):
    puntos = 0
    for m in METRICAS_INTENSIDAD:
        val_m = row.get(m, 0)
        bench_m = perf_jug.get(m, np.nan)
        if pd.isna(bench_m) or bench_m == 0:
            continue
        pct_m = val_m / bench_m
        if pct_m >= 0.90:   puntos += 4
        elif pct_m >= 0.80: puntos += 3
        elif pct_m >= 0.60: puntos += 2
        else:               puntos += 1
    return round((puntos / 28) * 100)

# ── Carga de datos ────────────────────────────────────────────────────────────
df_raw = cargar_datos()
equipos_disp = [e for e in EQUIPOS_ORDEN if e in df_raw["Equipo"].dropna().unique()] if "Equipo" in df_raw.columns else []

# ── Topbar ────────────────────────────────────────────────────────────────────
logo_b64  = img_base64("LOGO_CASI_SIN_FONDO.png")
logo_html = (f'<img src="data:image/png;base64,{logo_b64}" style="height:62px; width:auto;">' if logo_b64 else "⚡")

st.markdown(f"""
<style>
.topbar {{ position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
    background: #0f1a28; border-bottom: 3px solid #00A8CC; height: 72px;
    display: flex; align-items: center; padding: 0 24px; gap: 16px; }}
.topbar-divider {{ width: 1px; height: 36px; background: #2a4060; margin: 0 16px; }}
.topbar-club    {{ font-size: 18px; font-weight: 900; color: white; letter-spacing: 1px; text-transform: uppercase; }}
.topbar-sub     {{ font-size: 13px; font-weight: 600; color: #00A8CC; letter-spacing: 2px; text-transform: uppercase; }}
.topbar-page    {{ font-size: 13px; font-weight: 700; color: #7a9ab5; letter-spacing: 2px; text-transform: uppercase; }}
</style>
<div class="topbar">
    <div>{logo_html}</div>
    <div class="topbar-divider"></div>
    <span class="topbar-club">Club Atlético de San Isidro</span>
    <div class="topbar-divider"></div>
    <span class="topbar-sub">Análisis de rendimiento</span>
    <div class="topbar-divider"></div>
    <span class="topbar-page">Demanda Física · Partido</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: SCORING FÍSICO POR PARTIDO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">💪 Scoring Físico</div>', unsafe_allow_html=True)

sc_equipo = None
sc_puesto = None
sc_jugador = None
sc_participacion = "Sesión completa"

sc_col1, sc_col2, sc_col3, sc_col4 = st.columns([4, 2, 2, 2])

with sc_col1:
    st.markdown('<span class="filtro-label"></span>', unsafe_allow_html=True)
    sc_vista = st.radio("", ["Plantel", "Equipo", "Puesto", "Jugador"],
                        horizontal=True, label_visibility="collapsed", key="sc_vista")

with sc_col2:
    if sc_vista == "Jugador":
        jugadores_sc = sorted(df_raw["Player Name"].dropna().unique())
        st.markdown('<span class="filtro-label">Jugador</span>', unsafe_allow_html=True)
        sc_jugador = st.selectbox("", jugadores_sc, label_visibility="collapsed", key="sc_ju")
    elif sc_vista == "Puesto":
        st.markdown('<span class="filtro-label">Puesto</span>', unsafe_allow_html=True)
        sc_puesto = st.selectbox("", list(GRUPOS_PUESTO.keys()), label_visibility="collapsed", key="sc_pu")
    elif sc_vista == "Equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        sc_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="sc_eq2")

with sc_col3:
    if sc_vista in ("Jugador", "Puesto"):
        st.markdown('<span class="filtro-label">Participación</span>', unsafe_allow_html=True)
        sc_participacion = st.radio("", ["Sesión completa", "Solo 1 equipo"],
                                    horizontal=False, label_visibility="collapsed", key="sc_part")

with sc_col4:
    if sc_vista in ("Jugador", "Puesto") and sc_participacion == "Solo 1 equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        sc_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="sc_eq3")

df_md_sc = df_raw[(df_raw["MD"] == "MD")].copy()
if sc_equipo:
    df_md_sc = df_md_sc[df_md_sc["Equipo"] == sc_equipo]
if sc_vista == "Jugador" and sc_jugador:
    df_md_sc = df_md_sc[df_md_sc["Player Name"] == sc_jugador]
elif sc_vista == "Puesto" and sc_puesto:
    puestos_sc = GRUPOS_PUESTO.get(sc_puesto, [])
    df_md_sc = df_md_sc[df_md_sc["Position Name"].isin(puestos_sc)]

fechas_sc = sorted(df_md_sc["Fecha"].unique())
opciones_sc = {}
todas_fechas_eq = sorted(df_raw[(df_raw["MD"] == "MD") & (df_raw["Equipo"] == (sc_equipo or equipos_disp[0]))]["Fecha"].unique())
num_fecha_map = {f: i+1 for i, f in enumerate(todas_fechas_eq)}

for fecha in fechas_sc:
    rival = df_md_sc[df_md_sc["Fecha"] == fecha]["Rival"].iloc[0] if "Rival" in df_md_sc.columns else "—"
    num = num_fecha_map.get(fecha, "?")
    label = "F" + str(num) + " · " + pd.Timestamp(fecha).strftime("%d/%m") + " vs " + str(rival)
    opciones_sc[label] = fecha

partidos_sel = []
if len(opciones_sc) == 0:
    st.warning("No hay partidos disponibles.")
else:
    sc_key = f"{sc_vista}_{sc_equipo}_{sc_jugador if sc_vista == 'Jugador' else sc_puesto}"
    if st.session_state.get("sc_last_key") != sc_key:
        prev_sel = st.session_state.get("sc_partidos", [])
        prev_key = st.session_state.get("sc_last_key", "")
        if not prev_key or prev_sel == list(opciones_sc.keys()):
            st.session_state["sc_partidos"] = list(opciones_sc.keys())
        else:
            st.session_state["sc_partidos"] = [p for p in prev_sel if p in opciones_sc]
        st.session_state["sc_last_key"] = sc_key

    st.markdown('<span class="filtro-label">Partidos</span>', unsafe_allow_html=True)
    default_sel = [p for p in opciones_sc.keys() if p in st.session_state.get("sc_partidos", list(opciones_sc.keys()))]
    partidos_sel = st.multiselect("", list(opciones_sc.keys()),
                                  default=default_sel,
                                  label_visibility="collapsed", key="sc_partidos")

if partidos_sel:
    mejores_promedios = {}
    for col in SCORING_METRICAS.keys():
        promedios_por_partido = []
        for fec in fechas_sc:
            dp = df_md_sc[df_md_sc["Fecha"] == fec].copy()
            dp = dp.groupby("Player Name").agg({col: "sum"}).reset_index()
            promedios_por_partido.append(dp[col].mean())
        mejores_promedios[col] = max(promedios_por_partido)

    datos_grafico = []
    for partido_label in [l for l in opciones_sc.keys() if l in partidos_sel]:
        fecha_sc = opciones_sc[partido_label]
        df_p = df_md_sc[df_md_sc["Fecha"] == fecha_sc].copy()
        df_p = df_p.groupby("Player Name").agg(
            {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
        ).reset_index()
        df_p = df_p[df_p["Minutos"] > 30]
        media_cont = df_p["Contact Involvement Total Count Avg"].replace(0, np.nan).mean()
        df_p["Contact Involvement Total Count Avg"] = df_p["Contact Involvement Total Count Avg"].apply(
            lambda x: media_cont if pd.isna(x) or x < 5 else x
        )
        df_todos_partido = df_raw[
            (df_raw["MD"] == "MD") & (df_raw["Fecha"] == fecha_sc)
        ].groupby("Player Name").agg(
            {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
        ).reset_index()
        df_todos_partido = df_todos_partido[df_todos_partido["Minutos"] > 30]
        max_dia = {col: df_todos_partido[col].max() for col in SCORING_METRICAS.keys()}
        df_p["Score"] = df_p.apply(lambda row: calc_score_row(row, max_dia), axis=1)
        score_eq = df_p["Score"].mean()
        rival = partido_label.split(" vs ")[-1]
        fecha_str = partido_label.split(" · ")[1].split(" vs ")[0]
        metricas_prom = {col: df_p[col].mean() for col in SCORING_METRICAS.keys()}
        datos_grafico.append({
            "label": partido_label, "rival": rival, "fecha": fecha_str,
            "score": round(score_eq) if not np.isnan(score_eq) else 0, **metricas_prom
        })

    df_graf = pd.DataFrame(datos_grafico)
    df_graf["fecha_dt"] = pd.to_datetime(df_graf["fecha"], format="%d/%m")
    df_graf = df_graf.sort_values("fecha_dt").reset_index(drop=True)

    df_todos = pd.DataFrame()
    for lbl, fec in opciones_sc.items():
        dp = df_md_sc[df_md_sc["Fecha"] == fec].copy()
        dp = dp.groupby("Player Name").agg(
            {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
        ).reset_index()
        dp = dp[dp["Minutos"] > 30]
        media_c = dp["Contact Involvement Total Count Avg"].replace(0, np.nan).mean()
        dp["Contact Involvement Total Count Avg"] = dp["Contact Involvement Total Count Avg"].apply(lambda x: media_c if pd.isna(x) or x < 5 else x)
        df_todos_prom = df_raw[
            (df_raw["MD"] == "MD") & (df_raw["Fecha"] == fec)
        ].groupby("Player Name").agg(
            {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
        ).reset_index()
        df_todos_prom = df_todos_prom[df_todos_prom["Minutos"] > 30]
        max_dia_prom = {col: df_todos_prom[col].max() for col in SCORING_METRICAS.keys()}
        dp["Score"] = dp.apply(lambda row: calc_score_row(row, max_dia_prom), axis=1)
        if len(dp) > 0 and not np.isnan(dp["Score"].mean()):
            df_todos = pd.concat([df_todos, pd.DataFrame([{"score": dp["Score"].mean()}])])
    prom_total = df_todos["score"].mean()
    prom_seleccion = df_graf["score"].mean()

    hover_texts = []
    for _, r in df_graf.iterrows():
        txt = f"<b>vs {r['rival']} · {r['fecha']}</b><br><b>Score: {r['score']}</b><br><br>"
        for col, (label, peso, max_hist) in SCORING_METRICAS.items():
            mejor = mejores_promedios.get(col, MAX_HIST.get(col, 1))
            pct = min(r[col] / mejor * 100, 100) if mejor > 0 else 0
            txt += f"{label}: {r[col]:.0f} ({pct:.0f}% del mejor)<br>"
        hover_texts.append(txt)

    labels_x = df_graf["label"].tolist()
    scores   = df_graf["score"].tolist()
    c1_list  = [colores_rival(r) for r in df_graf["rival"].tolist()]

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Bar(x=labels_x, y=scores, marker_color=c1_list, marker_line_width=0,
        hovertext=hover_texts, hoverinfo="text",
        hoverlabel=dict(bgcolor="#0f1a28", font=dict(color="white", size=12)), showlegend=False))
    fig_sc.add_trace(go.Scatter(x=labels_x, y=[prom_total]*len(df_graf), mode="lines",
        line=dict(color="#00A8CC", dash="dash", width=2), name=f"Prom. total ({prom_total:.0f})", hoverinfo="skip"))
    fig_sc.add_trace(go.Scatter(x=labels_x, y=[prom_seleccion]*len(df_graf), mode="lines",
        line=dict(color="#FF00FF", dash="dot", width=2), name=f"Prom. partidos elegidos ({prom_seleccion:.0f})", hoverinfo="skip"))
    fig_sc.update_layout(paper_bgcolor="#1a2535", plot_bgcolor="#0f1a28", height=350,
        margin=dict(t=20, b=80, l=40, r=20),
        xaxis=dict(tickfont=dict(color="#7a9ab5", size=9), tickangle=-35, showgrid=False),
        yaxis=dict(tickfont=dict(color="#7a9ab5", size=9), gridcolor="#1e3048"),
        showlegend=True, legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"), bargap=0.3)
    st.plotly_chart(fig_sc, use_container_width=True)

    partidos_ordered = [l for l in opciones_sc.keys() if l in partidos_sel]
    todas_fichas_html = '<div style="overflow-x:auto;"><div style="display:flex;flex-wrap:wrap;gap:16px;">'

    for partido_label in partidos_ordered:
        fecha_sc = opciones_sc[partido_label]
        df_p = df_md_sc[df_md_sc["Fecha"] == fecha_sc].copy()
        df_p = df_p.groupby("Player Name").agg(
            {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
        ).reset_index()
        df_p = df_p[df_p["Minutos"] > 30]
        media_cont = df_p["Contact Involvement Total Count Avg"].replace(0, np.nan).mean()
        df_p["Contact Involvement Total Count Avg"] = df_p["Contact Involvement Total Count Avg"].apply(
            lambda x: media_cont if pd.isna(x) or x < 5 else x
        )
        df_todos_partido = df_raw[
            (df_raw["MD"] == "MD") & (df_raw["Fecha"] == fecha_sc)
        ].groupby("Player Name").agg(
            {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
        ).reset_index()
        df_todos_partido = df_todos_partido[df_todos_partido["Minutos"] > 30]
        max_dia = {col: df_todos_partido[col].max() for col in SCORING_METRICAS.keys()}
        df_p["Score"] = df_p.apply(lambda row: calc_score_row(row, max_dia), axis=1)
        score_equipo = int(round(df_p["Score"].mean())) if not np.isnan(df_p["Score"].mean()) else 0
        rival_label  = partido_label.split(" vs ")[-1]
        fecha_label  = partido_label.split(" · ")[1].split(" vs ")[0]

        barras_html = ""
        for col, (lbl, peso, max_hist) in SCORING_METRICAS.items():
            val_prom = df_p[col].mean()
            mejor = mejores_promedios.get(col, MAX_HIST.get(col, 1))
            pct = min(val_prom / mejor * 100, 100) if mejor > 0 else 0
            color_barra = "#00CC44" if pct >= 90 else ("#FFD000" if pct >= 70 else "#FF4444")
            barras_html += (
                '<div style="margin-bottom:8px;">'
                + '<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                + '<span style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:0.5px;">' + lbl + '</span>'
                + '<span style="font-size:10px;font-weight:700;color:#ffffff;">' + f"{val_prom:.0f}" + '</span>'
                + '</div>'
                + '<div style="background:#1e3048;border-radius:3px;height:5px;width:100%;">'
                + '<div style="background:' + color_barra + ';width:' + f"{pct:.0f}" + '%;height:5px;border-radius:3px;"></div>'
                + '</div></div>'
            )

        color_score = "#00CC44" if score_equipo >= 50 else ("#FFD000" if score_equipo >= 35 else "#FF4444")
        todas_fichas_html += (
            '<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:10px;padding:12px;width:190px;flex-shrink:0;">'
            + '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
            + '<div>'
            + '<div style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">' + (sc_jugador or sc_equipo or "Plantel") + ' · ' + fecha_label + '</div>'
            + '<div style="font-size:15px;font-weight:900;color:#ffffff;margin-top:3px;">vs ' + rival_label + '</div>'
            + '<div style="font-size:9px;color:#4a6a80;margin-top:2px;">Fecha ' + partido_label.split(" · ")[0][1:] + '</div>'
            + '</div>'
            + '<div style="text-align:right;">'
            + '<div style="font-size:48px;font-weight:900;color:' + color_score + ';line-height:1;">' + str(score_equipo) + '</div>'
            + '<div style="font-size:9px;color:#4a6a80;text-transform:uppercase;">score</div>'
            + '</div></div>'
            + barras_html + '</div>'
        )

    todas_fichas_html += '</div></div>'
    st.markdown(todas_fichas_html, unsafe_allow_html=True)
    
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: PUNTAJE FINAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">🏅 Puntaje Final</div>', unsafe_allow_html=True)

s4_equipo = None
s4_puesto = None
s4_jugador = None
s4_participacion = "Sesión completa"

s4_col1, s4_col2, s4_col3, s4_col4 = st.columns([4, 2, 2, 2])

with s4_col1:
    st.markdown('<span class="filtro-label"></span>', unsafe_allow_html=True)
    s4_vista = st.radio("", ["Plantel", "Equipo", "Puesto", "Jugador"],
                        horizontal=True, label_visibility="collapsed", key="s4_vista")

with s4_col2:
    if s4_vista == "Jugador":
        jugadores_s4 = sorted(df_raw["Player Name"].dropna().unique())
        st.markdown('<span class="filtro-label">Jugador</span>', unsafe_allow_html=True)
        s4_jugador = st.selectbox("", jugadores_s4, label_visibility="collapsed", key="s4_ju")
    elif s4_vista == "Puesto":
        st.markdown('<span class="filtro-label">Puesto</span>', unsafe_allow_html=True)
        s4_puesto = st.selectbox("", list(GRUPOS_PUESTO.keys()), label_visibility="collapsed", key="s4_pu")
    elif s4_vista == "Equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        s4_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="s4_eq")

with s4_col3:
    if s4_vista in ("Jugador", "Puesto"):
        st.markdown('<span class="filtro-label">Participación</span>', unsafe_allow_html=True)
        s4_participacion = st.radio("", ["Sesión completa", "Solo 1 equipo"],
                                    horizontal=False, label_visibility="collapsed", key="s4_part")

with s4_col4:
    if s4_vista in ("Jugador", "Puesto") and s4_participacion == "Solo 1 equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        s4_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="s4_eq2")

df_md_ranking = df_raw[df_raw["MD"] == "MD"].copy()

df_md_s4 = df_md_ranking.copy()
if s4_vista == "Jugador" and s4_jugador:
    df_md_s4 = df_md_s4[df_md_s4["Player Name"] == s4_jugador]
elif s4_vista == "Puesto" and s4_puesto:
    puestos_s4 = GRUPOS_PUESTO.get(s4_puesto, [])
    df_md_s4 = df_md_s4[df_md_s4["Position Name"].isin(puestos_s4)]

fechas_s4 = sorted(df_md_s4["Fecha"].unique())
fechas_ranking_todas = sorted(df_md_ranking["Fecha"].unique())
todas_fechas_s4 = sorted(df_raw[(df_raw["MD"] == "MD") & (df_raw["Equipo"] == (s4_equipo or equipos_disp[0]))]["Fecha"].unique())
num_fecha_s4 = {f: i+1 for i, f in enumerate(todas_fechas_s4)}

opciones_s4 = {}
for fecha in fechas_s4:
    rival = df_md_s4[df_md_s4["Fecha"] == fecha]["Rival"].iloc[0] if "Rival" in df_md_s4.columns else "—"
    num = num_fecha_s4.get(fecha, "?")
    label = "F" + str(num) + " · " + pd.Timestamp(fecha).strftime("%d/%m") + " vs " + str(rival)
    opciones_s4[label] = fecha

if len(opciones_s4) == 0:
    st.warning("No hay partidos disponibles.")
else:
    st.markdown('<span class="filtro-label">Partidos</span>', unsafe_allow_html=True)
    partidos_s4 = st.multiselect("", list(opciones_s4.keys()),
                                 default=list(opciones_s4.keys()),
                                 label_visibility="collapsed", key="s4_partidos")

    if not partidos_s4:
        st.info("Seleccioná al menos un partido.")
    else:
        r_vista_pre = st.session_state.get("r_vista", "Plantel")
        r_equipo_pre = st.session_state.get("r_eq", None) if r_vista_pre == "Equipo" else None
        r_part_pre = st.session_state.get("r_part", "Sesión completa")
        filas_ranking = []
        scores_por_partido = {}
        perfiles_cache = {
            jug: PERFILES_TODOS.get(jug, pd.Series())
            for jug in df_md_ranking["Player Name"].unique()
        }

        opciones_ranking = {}
        for fecha in sorted(df_md_ranking["Fecha"].unique()):
            rival = df_md_ranking[df_md_ranking["Fecha"] == fecha]["Rival"].iloc[0] if "Rival" in df_md_ranking.columns else "—"
            num = num_fecha_s4.get(fecha, "?")
            label = "F" + str(num) + " · " + pd.Timestamp(fecha).strftime("%d/%m") + " vs " + str(rival)
            opciones_ranking[label] = fecha

        for partido_label in opciones_ranking.keys():
            fecha = opciones_ranking[partido_label]
            if r_part_pre == "Solo 1 equipo" and r_equipo_pre:
                df_p = df_md_ranking[(df_md_ranking["Fecha"] == fecha) & (df_md_ranking["Equipo"] == r_equipo_pre)].copy()
            else:
                df_p = df_md_ranking[df_md_ranking["Fecha"] == fecha].copy()
            

            df_sc = df_p.groupby("Player Name").agg(
                {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
            ).reset_index()
            df_sc = df_sc[df_sc["Minutos"] > 30]
            if len(df_sc) == 0:
                continue
            media_cont = df_sc["Contact Involvement Total Count Avg"].replace(0, np.nan).mean()
            df_sc["Contact Involvement Total Count Avg"] = df_sc["Contact Involvement Total Count Avg"].apply(
                lambda x: media_cont if pd.isna(x) or x < 5 else x
            )
            df_todos_partido = df_raw[
                (df_raw["MD"] == "MD") & (df_raw["Fecha"] == fecha)
            ].groupby("Player Name").agg(
                {**{col: "sum" for col in SCORING_METRICAS.keys()}, "Minutos": "sum"}
            ).reset_index()
            df_todos_partido = df_todos_partido[df_todos_partido["Minutos"] > 30]
            max_dia = {col: df_todos_partido[col].max() for col in SCORING_METRICAS.keys()}
            df_sc["Score"] = df_sc.apply(lambda row: calc_score_row(row, max_dia), axis=1)

            df_int = df_p.groupby("Player Name").agg(
                {**{m: "sum" for m in METRICAS_INTENSIDAD}, "Minutos": "sum"}
            ).reset_index()
            df_int = df_int[df_int["Minutos"] > 30]

            score_partido = []
            for _, row_sc in df_sc.iterrows():
                jug = row_sc["Player Name"]
                perf_jug = perfiles_cache.get(jug, pd.Series())

                row_int = df_int[df_int["Player Name"] == jug]
                if len(row_int) == 0:
                    continue
                intensidad = calc_intensidad(row_int.iloc[0], perf_jug)
                score_fis = row_sc["Score"]
                puntaje_final = round((score_fis / 100) * intensidad)

                filas_ranking.append({
                    "Jugador": jug, "Partido": partido_label,
                    "Equipo": df_p[df_p["Player Name"] == jug]["Equipo"].values[0] if len(df_p[df_p["Player Name"] == jug]) > 0 else "",
                    "Intensidad": intensidad, "Score Físico": score_fis,
                    "Puntaje Final": puntaje_final,
                })
                score_partido.append(puntaje_final)

            scores_por_partido[partido_label] = np.mean(score_partido) if score_partido else 0

        if not filas_ranking:
            st.warning("Sin datos para calcular puntaje.")
        else:
            df_ranking = pd.DataFrame(filas_ranking)

            partidos_ordered_s4 = [l for l in opciones_s4.keys() if l in partidos_s4]
            labels_s4  = partidos_ordered_s4
            scores_s4  = [scores_por_partido.get(l, 0) for l in labels_s4]
            rivales_s4 = [l.split(" vs ")[-1] for l in labels_s4]
            c_s4       = [colores_rival(r) for r in rivales_s4]
            prom_s4    = np.mean(scores_s4)

            fig_s4 = go.Figure()
            fig_s4.add_trace(go.Bar(x=labels_s4, y=scores_s4, marker_color=c_s4, marker_line_width=0,
                showlegend=False, hovertemplate="<b>%{x}</b><br>Puntaje: %{y}<extra></extra>"))
            fig_s4.add_trace(go.Scatter(x=labels_s4, y=[prom_s4]*len(labels_s4), mode="lines",
                line=dict(color="#00A8CC", dash="dash", width=2), name=f"Promedio ({prom_s4:.0f})", hoverinfo="skip"))
            fig_s4.update_layout(paper_bgcolor="#1a2535", plot_bgcolor="#0f1a28", height=350,
                margin=dict(t=20, b=80, l=40, r=20),
                xaxis=dict(tickfont=dict(color="#7a9ab5", size=9), tickangle=-35, showgrid=False),
                yaxis=dict(tickfont=dict(color="#7a9ab5", size=9), gridcolor="#1e3048"),
                showlegend=True, legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"), bargap=0.3)
            st.plotly_chart(fig_s4, use_container_width=True)

            # ── Ranking ───────────────────────────────────────────────────────
            st.markdown('<div class="seccion-header">🏆 Ranking</div>', unsafe_allow_html=True)

            r_col1, r_col2, r_col3, r_col4 = st.columns([4, 2, 2, 2])
            r_equipo = r_puesto = r_jugador = None
            r_participacion = "Sesión completa"

            with r_col1:
                st.markdown('<span class="filtro-label">Vista ranking</span>', unsafe_allow_html=True)
                r_vista = st.radio("", ["Plantel", "Equipo", "Puesto", "Jugador"],
                                   horizontal=True, label_visibility="collapsed", key="r_vista")

            with r_col2:
                if r_vista == "Equipo":
                    st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
                    r_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="r_eq")
                elif r_vista == "Puesto":
                    st.markdown('<span class="filtro-label">Puesto</span>', unsafe_allow_html=True)
                    r_puesto = st.selectbox("", list(GRUPOS_PUESTO.keys()), label_visibility="collapsed", key="r_pu")
                elif r_vista == "Jugador":
                    r_jugadores_disp = sorted(df_ranking["Jugador"].unique())
                    st.markdown('<span class="filtro-label">Jugador</span>', unsafe_allow_html=True)
                    r_jugador = st.selectbox("", r_jugadores_disp, label_visibility="collapsed", key="r_ju")

            with r_col3:
                if r_vista in ("Jugador", "Puesto", "Equipo"):
                    st.markdown('<span class="filtro-label">Participación</span>', unsafe_allow_html=True)
                    r_participacion = st.radio("", ["Sesión completa", "Solo 1 equipo"],
                                            horizontal=False, label_visibility="collapsed", key="r_part")

            with r_col4:
                if r_vista in ("Jugador", "Puesto") and r_participacion == "Solo 1 equipo":
                    st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
                    r_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="r_eq2")

            r_sl1, r_sl2, _ = st.columns([2, 2, 4])

            with r_sl1:
                fechas_ranking = sorted(df_ranking["Partido"].unique(), key=lambda x: opciones_ranking.get(x, pd.Timestamp.min), reverse=True)
                fechas_sel_rk = [f for f in fechas_ranking if st.session_state.get(f"rk_fec_{f}", False)]
                btn_txt = "Todas ▾" if not fechas_sel_rk else (f"{fechas_sel_rk[0].split(' · ')[0]} ▾" if len(fechas_sel_rk) == 1 else f"{len(fechas_sel_rk)} selec. ▾")
                st.markdown('<span class="filtro-label">Fechas</span>', unsafe_allow_html=True)
                with st.popover(btn_txt, use_container_width=True):
                    def borrar_rk_fec():
                        for k in list(st.session_state.keys()):
                            if k.startswith("rk_fec_") and k != "rk_fec_todos":
                                st.session_state[k] = False
                    st.button("✓ Todas", key="rk_fec_todos", use_container_width=True, on_click=borrar_rk_fec)
                    for f in fechas_ranking:
                        num = f.split(" · ")[0][1:]  # extrae el número sin la "F"
                        resto = f.split(" · ")[1]    # "30/05 vs Belgrano"
                        label_display = f"Fecha {num} — {resto}"
                        st.checkbox(label_display, value=st.session_state.get(f"rk_fec_{f}", False), key=f"rk_fec_display_{f}", on_change=lambda k=f: st.session_state.update({f"rk_fec_{k}": st.session_state[f"rk_fec_display_{k}"]}))
                fechas_sel = fechas_sel_rk if fechas_sel_rk else fechas_ranking

            cant = 20

            df_rank_filtrado = df_ranking.copy()
            df_rank_filtrado = df_rank_filtrado[df_rank_filtrado["Partido"].isin(fechas_sel)]

            if r_vista == "Equipo" and r_equipo:
                if r_participacion == "Solo 1 equipo":
                    df_rank_filtrado = df_rank_filtrado[df_rank_filtrado["Equipo"] == r_equipo]
                else:
                    jugs_equipo = df_raw[(df_raw["Equipo"] == r_equipo) & (df_raw["MD"] == "MD")]["Player Name"].unique()
                    df_rank_filtrado = df_rank_filtrado[df_rank_filtrado["Jugador"].isin(jugs_equipo)]
            elif r_vista == "Puesto" and r_puesto:
                jugs_puesto = df_raw[(df_raw["MD"] == "MD") & (df_raw["Position Name"].isin(GRUPOS_PUESTO.get(r_puesto, [])))]["Player Name"].unique()
                df_rank_filtrado = df_rank_filtrado[df_rank_filtrado["Jugador"].isin(jugs_puesto)]
            elif r_vista == "Jugador" and r_jugador:
                df_rank_filtrado = df_rank_filtrado[df_rank_filtrado["Jugador"] == r_jugador]

            df_rank_filtrado = df_rank_filtrado.sort_values("Puntaje Final", ascending=False)
            df_rank_filtrado = df_rank_filtrado.head(cant)
            
            cab_rank = "<tr><th class='col-jugador'>Jugador</th><th>Partido</th><th>Puntaje Final</th></tr>"
            filas_rank = ""
            for _, r in df_rank_filtrado.iterrows():
                color_pf = "#00CC44" if r["Puntaje Final"] >= 50 else ("#FFD000" if r["Puntaje Final"] >= 30 else "#FF4444")
                filas_rank += (
                    "<tr>"
                    + "<td class='col-jugador'>" + r["Jugador"] + "</td>"
                    + "<td style='color:#7a9ab5;font-size:11px;'>" + r["Partido"] + "</td>"
                    + "<td><span class='celda-valor' style='background:" + color_pf + "22;color:" + color_pf + ";font-size:14px;'>" + str(r["Puntaje Final"]) + "</span></td>"
                    + "</tr>"
                )
            st.markdown(
                "<div style='overflow-x:auto;'><table class='tabla-semaforo'>" + cab_rank + filas_rank + "</table></div>",
                unsafe_allow_html=True
            )
          