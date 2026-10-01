import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64, os

st.set_page_config(page_title="Scoring por Puesto", layout="wide", initial_sidebar_state="expanded")

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
POS2GRUPO = {pos: grp for grp, puestos in GRUPOS_PUESTO.items() for pos in puestos}

EQUIPOS_ORDEN = ["Primera", "Intermedia", "Pre A"]

# Las 4 métricas del scoring. El peso ya NO es fijo: se deriva por puesto desde los datos.
SCORING_METRICAS = {
    "Total Player Load":                     "Player Load",
    "# ACDC":                                "ACDC",
    "Contact Involvement Total Count Avg":   "Contactos",
    "Distancia Explosiva":                   "Dist Expl",
}
METRICAS = list(SCORING_METRICAS.keys())

FILTRO_MIN = 45   # umbral mínimo de minutos para entrar al cálculo

# ── PESOS POR PUESTO (FIJOS) ────────────────────────────────────────────────────
# Derivados de los datos (cuánto se destaca cada puesto en cada métrica vs el
# promedio de los puestos). Son FIJOS a propósito: la vara no debe cambiar cuando
# se cargan partidos nuevos, para que los scores sigan siendo comparables entre
# fechas. Ajustá a mano los valores que tu criterio indique; cada fila debe
# sumar 1.00. Orden de las claves: Player Load, ACDC, Contactos, Dist Expl.
PESOS_PUESTO = {
    "Primeras":         {"Total Player Load": 0.32, "# ACDC": 0.15, "Contact Involvement Total Count Avg": 0.42, "Distancia Explosiva": 0.11},
    "Segundas":         {"Total Player Load": 0.28, "# ACDC": 0.18, "Contact Involvement Total Count Avg": 0.38, "Distancia Explosiva": 0.16},
    "Terceras":         {"Total Player Load": 0.22, "# ACDC": 0.23, "Contact Involvement Total Count Avg": 0.36, "Distancia Explosiva": 0.19},
    "Pareja de medios": {"Total Player Load": 0.26, "# ACDC": 0.27, "Contact Involvement Total Count Avg": 0.19, "Distancia Explosiva": 0.28},
    "Centros":          {"Total Player Load": 0.23, "# ACDC": 0.30, "Contact Involvement Total Count Avg": 0.19, "Distancia Explosiva": 0.28},
    "3 del fondo":      {"Total Player Load": 0.23, "# ACDC": 0.28, "Contact Involvement Total Count Avg": 0.11, "Distancia Explosiva": 0.38},
}

COLORES_RIVALES = {
    "Los Tilos": "#228B22", "Tilos": "#228B22", "Matreros": "#D32F2F",
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
    df["Grupo_Puesto"] = df["Position Name"].map(POS2GRUPO)
    return df

df_raw = cargar_datos()

# ══════════════════════════════════════════════════════════════════════════════
# NÚCLEO DEL MÉTODO NUEVO
# ══════════════════════════════════════════════════════════════════════════════
# 1) TECHO POR BIGOTE: en vez del máximo histórico (sensible a outliers), el techo
#    de cada métrica es el bigote superior del boxplot (Q3 + 1.5*IQR). Los valores
#    por encima son outliers y se topean en 1.0, sin inflar la vara del resto.
# 2) PESOS POR PUESTO: el peso de cada métrica en cada grupo refleja cuánto se
#    destaca ese puesto en esa métrica respecto del promedio de los puestos
#    (índice = valor_grupo / promedio_entre_grupos, repartido para sumar 1).

@st.cache_data
def calcular_bigotes(_df):
    """Bigote superior (Q3 + 1.5*IQR) por métrica, sobre MD de toda la liga,
    agregando por jugador-fecha (igual criterio que el resto del scoring)."""
    base = _df[_df["MD"] == "MD"].groupby(["Player Name", "Fecha"]).agg(
        {c: "sum" for c in METRICAS}
    ).reset_index()
    bigotes = {}
    for c in METRICAS:
        s = base[c].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        bigotes[c] = q3 + 1.5 * iqr
    return bigotes

BIGOTES = calcular_bigotes(df_raw)

def calc_score_jugador(row):
    """Score 0-100 de un jugador: normaliza cada métrica por su bigote (topeada
    en 1.0) y la pondera con el peso del puesto del jugador."""
    grupo = row.get("Grupo_Puesto")
    pesos = PESOS_PUESTO.get(grupo)
    if pesos is None:
        return np.nan
    score = 0.0
    for c in METRICAS:
        val = row[c]
        if pd.isna(val):
            continue
        ref = BIGOTES.get(c, 0)
        norm = min(val / ref, 1.0) if ref > 0 else 0
        score += norm * pesos[c]
    return round(score * 100)

def score_equipo(df_part, ponderar):
    """Combina los scores individuales en el score del equipo (AGREGACIÓN SIMPLE:
    todos los jugadores a la misma bolsa).
    ponderar=True -> media ponderada por minutos; False -> media simple."""
    d = df_part.dropna(subset=["Score"])
    if len(d) == 0:
        return 0
    if ponderar:
        if d["Minutos"].sum() == 0:
            return 0
        val = np.average(d["Score"], weights=d["Minutos"])
    else:
        val = d["Score"].mean()
    return int(round(val)) if not np.isnan(val) else 0

def score_equipo_por_linea(df_part, ponderar):
    """Score del equipo AGREGANDO POR LÍNEA: primero promedia el score dentro de
    cada grupo de puesto, y después promedia esos valores de grupo. Así cada línea
    pesa igual en el total, sin importar cuántos jugadores tenga.
    ponderar=True -> dentro de cada línea pondera por minutos."""
    d = df_part.dropna(subset=["Score"])
    if len(d) == 0:
        return 0
    scores_linea = []
    for grp, g in d.groupby("Grupo_Puesto"):
        if ponderar:
            if g["Minutos"].sum() == 0:
                continue
            scores_linea.append(np.average(g["Score"], weights=g["Minutos"]))
        else:
            scores_linea.append(g["Score"].mean())
    if not scores_linea:
        return 0
    val = np.mean(scores_linea)
    return int(round(val)) if not np.isnan(val) else 0

def scores_por_linea(df_part, ponderar):
    """Devuelve el score de cada línea por separado (para mostrar el desglose)."""
    d = df_part.dropna(subset=["Score"])
    out = {}
    for grp, g in d.groupby("Grupo_Puesto"):
        if ponderar and g["Minutos"].sum() > 0:
            out[grp] = int(round(np.average(g["Score"], weights=g["Minutos"])))
        elif len(g) > 0:
            out[grp] = int(round(g["Score"].mean()))
    return out

def preparar_partido(df_fecha):
    """Agrupa por jugador en un partido, aplica el filtro de minutos, imputa
    contactos atípicos y calcula el score individual."""
    dp = df_fecha.groupby(["Player Name", "Grupo_Puesto"]).agg(
        {**{c: "sum" for c in METRICAS}, "Minutos": "sum"}
    ).reset_index()
    dp = dp[dp["Minutos"] >= FILTRO_MIN]
    if len(dp) == 0:
        return dp
    media_cont = dp["Contact Involvement Total Count Avg"].replace(0, np.nan).mean()
    dp["Contact Involvement Total Count Avg"] = dp["Contact Involvement Total Count Avg"].apply(
        lambda x: media_cont if pd.isna(x) or x < 5 else x
    )
    dp["Score"] = dp.apply(calc_score_jugador, axis=1)
    return dp

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
    <span class="topbar-page">Scoring por Puesto</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCORING FÍSICO POR PARTIDO (techo por bigote + pesos por puesto)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">💪 Scoring Físico por Puesto</div>', unsafe_allow_html=True)

equipos_disp = [e for e in EQUIPOS_ORDEN if e in df_raw["Equipo"].dropna().unique()] if "Equipo" in df_raw.columns else []

c1, c2 = st.columns([2, 2])
with c1:
    st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
    sc_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="sp_eq")
with c2:
    st.markdown('<span class="filtro-label">Cálculo del score del equipo</span>', unsafe_allow_html=True)
    sc_modo = st.radio("", ["Sin ponderar", "Ponderado x minutos"],
                       horizontal=True, label_visibility="collapsed", key="sp_modo")
ponderar = (sc_modo == "Ponderado x minutos")

df_md = df_raw[(df_raw["MD"] == "MD") & (df_raw["Equipo"] == sc_equipo)].copy()
fechas = sorted(df_md["Fecha"].unique())
num_fecha = {f: i + 1 for i, f in enumerate(fechas)}

opciones = {}
for fecha in fechas:
    rival = df_md[df_md["Fecha"] == fecha]["Rival"].iloc[0] if "Rival" in df_md.columns else "—"
    label = "F" + str(num_fecha[fecha]) + " · " + pd.Timestamp(fecha).strftime("%d/%m") + " vs " + str(rival)
    opciones[label] = fecha

if len(opciones) == 0:
    st.warning("No hay partidos disponibles.")
    st.stop()

st.markdown('<span class="filtro-label">Partidos</span>', unsafe_allow_html=True)
partidos_sel = st.multiselect("", list(opciones.keys()), default=list(opciones.keys()),
                              label_visibility="collapsed", key="sp_partidos")

if not partidos_sel:
    st.info("Seleccioná al menos un partido.")
    st.stop()

# Mejor promedio por partido de cada métrica (para las barras explicativas)
mejores_promedios = {}
for col in METRICAS:
    proms = []
    for fec in fechas:
        dp = preparar_partido(df_md[df_md["Fecha"] == fec])
        if len(dp) > 0:
            proms.append(dp[col].mean())
    mejores_promedios[col] = max(proms) if proms else 1

# Score de todos los partidos (para la línea de promedio total)
scores_todos = []
for fec in fechas:
    dp = preparar_partido(df_md[df_md["Fecha"] == fec])
    if len(dp) > 0:
        scores_todos.append(score_equipo(dp, ponderar))
prom_total = np.mean(scores_todos) if scores_todos else 0

# Datos de los partidos seleccionados
datos = []
for label in [l for l in opciones.keys() if l in partidos_sel]:
    dp = preparar_partido(df_md[df_md["Fecha"] == opciones[label]])
    if len(dp) == 0:
        continue
    datos.append({
        "label": label,
        "rival": label.split(" vs ")[-1],
        "fecha": label.split(" · ")[1].split(" vs ")[0],
        "score": score_equipo(dp, ponderar),
        **{col: dp[col].mean() for col in METRICAS},
    })

df_graf = pd.DataFrame(datos)
df_graf["fecha_dt"] = pd.to_datetime(df_graf["fecha"], format="%d/%m")
df_graf = df_graf.sort_values("fecha_dt").reset_index(drop=True)
prom_sel = df_graf["score"].mean()

# ── Gráfico de barras ──────────────────────────────────────────────────────────
hover_texts = []
for _, r in df_graf.iterrows():
    txt = f"<b>vs {r['rival']} · {r['fecha']}</b><br><b>Score: {r['score']}</b><br><br>"
    for col in METRICAS:
        mejor = mejores_promedios.get(col, 1)
        pct = min(r[col] / mejor * 100, 100) if mejor > 0 else 0
        txt += f"{SCORING_METRICAS[col]}: {r[col]:.0f} ({pct:.0f}% del mejor)<br>"
    hover_texts.append(txt)

labels_x = df_graf["label"].tolist()
scores   = df_graf["score"].tolist()
colores  = [colores_rival(r) for r in df_graf["rival"].tolist()]

fig = go.Figure()
fig.add_trace(go.Bar(x=labels_x, y=scores, marker_color=colores, marker_line_width=0,
    hovertext=hover_texts, hoverinfo="text",
    hoverlabel=dict(bgcolor="#0f1a28", font=dict(color="white", size=12)), showlegend=False))
fig.add_trace(go.Scatter(x=labels_x, y=[prom_total]*len(df_graf), mode="lines",
    line=dict(color="#00A8CC", dash="dash", width=2), name=f"Prom. total ({prom_total:.0f})", hoverinfo="skip"))
fig.add_trace(go.Scatter(x=labels_x, y=[prom_sel]*len(df_graf), mode="lines",
    line=dict(color="#FF00FF", dash="dot", width=2), name=f"Prom. elegidos ({prom_sel:.0f})", hoverinfo="skip"))
fig.update_layout(paper_bgcolor="#1a2535", plot_bgcolor="#0f1a28", height=350,
    margin=dict(t=20, b=80, l=40, r=20),
    xaxis=dict(tickfont=dict(color="#7a9ab5", size=9), tickangle=-35, showgrid=False),
    yaxis=dict(tickfont=dict(color="#7a9ab5", size=9), gridcolor="#1e3048", range=[0, 100]),
    showlegend=True, legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"), bargap=0.3)
st.plotly_chart(fig, use_container_width=True)

# ── Fichas por partido ─────────────────────────────────────────────────────────
fichas_html = '<div style="overflow-x:auto;"><div style="display:flex;flex-wrap:wrap;gap:16px;">'
for label in [l for l in opciones.keys() if l in partidos_sel]:
    dp = preparar_partido(df_md[df_md["Fecha"] == opciones[label]])
    if len(dp) == 0:
        continue
    sc_eq = score_equipo(dp, ponderar)
    rival_label = label.split(" vs ")[-1]
    fecha_label = label.split(" · ")[1].split(" vs ")[0]

    barras_html = ""
    for col in METRICAS:
        val_prom = dp[col].mean()
        mejor = mejores_promedios.get(col, 1)
        pct = min(val_prom / mejor * 100, 100) if mejor > 0 else 0
        color_barra = "#00CC44" if pct >= 90 else ("#FFD000" if pct >= 70 else "#FF4444")
        barras_html += (
            '<div style="margin-bottom:8px;">'
            + '<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
            + '<span style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:0.5px;">' + SCORING_METRICAS[col] + '</span>'
            + '<span style="font-size:10px;font-weight:700;color:#ffffff;">' + f"{val_prom:.0f}" + '</span>'
            + '</div>'
            + '<div style="background:#1e3048;border-radius:3px;height:5px;width:100%;">'
            + '<div style="background:' + color_barra + ';width:' + f"{pct:.0f}" + '%;height:5px;border-radius:3px;"></div>'
            + '</div></div>'
        )

    color_score = "#00CC44" if sc_eq >= 50 else ("#FFD000" if sc_eq >= 35 else "#FF4444")
    fichas_html += (
        '<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:10px;padding:12px;width:190px;flex-shrink:0;">'
        + '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
        + '<div>'
        + '<div style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">' + sc_equipo + ' · ' + fecha_label + '</div>'
        + '<div style="font-size:15px;font-weight:900;color:#ffffff;margin-top:3px;">vs ' + rival_label + '</div>'
        + '<div style="font-size:9px;color:#4a6a80;margin-top:2px;">Fecha ' + label.split(" · ")[0][1:] + '</div>'
        + '</div>'
        + '<div style="text-align:right;">'
        + '<div style="font-size:48px;font-weight:900;color:' + color_score + ';line-height:1;">' + str(sc_eq) + '</div>'
        + '<div style="font-size:9px;color:#4a6a80;text-transform:uppercase;">score</div>'
        + '</div></div>'
        + barras_html + '</div>'
    )
fichas_html += '</div></div>'
st.markdown(fichas_html, unsafe_allow_html=True)

# ── Tabla de pesos por puesto (referencia) ──────────────────────────────────────
st.markdown('<div class="seccion-header">⚖️ Pesos por puesto (derivados de los datos)</div>', unsafe_allow_html=True)
filas = ""
for grp in GRUPOS_PUESTO.keys():
    if grp not in PESOS_PUESTO:
        continue
    celdas = "".join(
        f'<td style="text-align:center;color:white;padding:6px;border-bottom:1px solid #1e3048;">{PESOS_PUESTO[grp][c]*100:.0f}</td>'
        for c in METRICAS
    )
    filas += f'<tr><td style="color:#cce0f0;font-weight:600;padding:6px;border-bottom:1px solid #1e3048;">{grp}</td>{celdas}</tr>'
cab = "".join(f'<th style="color:#00A8CC;font-size:10px;text-transform:uppercase;padding:8px 6px;border-bottom:2px solid #1e3048;">{SCORING_METRICAS[c]}</th>' for c in METRICAS)
st.markdown(
    '<table style="width:100%;border-collapse:collapse;font-size:12px;">'
    + '<tr><th style="text-align:left;color:#00A8CC;font-size:10px;text-transform:uppercase;padding:8px 6px;border-bottom:2px solid #1e3048;">Puesto</th>'
    + cab + '</tr>' + filas + '</table>',
    unsafe_allow_html=True
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SCORE AGREGADO POR LÍNEA
# ══════════════════════════════════════════════════════════════════════════════
# Mismo score individual por jugador (bigote + pesos por puesto), pero la forma de
# llegar al total del equipo cambia: en vez de promediar los 15 jugadores juntos,
# primero se promedia cada línea y después se promedian las líneas entre sí. Así
# cada sector de la cancha pesa igual, sin importar cuántos jugadores tenga, y se
# puede leer el desgaste línea por línea.
st.markdown('<div class="seccion-header">🧩 Score agregado por línea</div>', unsafe_allow_html=True)

# Score de todos los partidos con agregación por línea (para la línea de promedio)
scores_lin_todos = []
for fec in fechas:
    dp = preparar_partido(df_md[df_md["Fecha"] == fec])
    if len(dp) > 0:
        scores_lin_todos.append(score_equipo_por_linea(dp, ponderar))
prom_lin_total = np.mean(scores_lin_todos) if scores_lin_todos else 0

datos_lin = []
for label in [l for l in opciones.keys() if l in partidos_sel]:
    dp = preparar_partido(df_md[df_md["Fecha"] == opciones[label]])
    if len(dp) == 0:
        continue
    datos_lin.append({
        "label": label,
        "rival": label.split(" vs ")[-1],
        "fecha": label.split(" · ")[1].split(" vs ")[0],
        "score_simple": score_equipo(dp, ponderar),
        "score_linea": score_equipo_por_linea(dp, ponderar),
        "desglose": scores_por_linea(dp, ponderar),
    })

df_lin = pd.DataFrame(datos_lin)
df_lin["fecha_dt"] = pd.to_datetime(df_lin["fecha"], format="%d/%m")
df_lin = df_lin.sort_values("fecha_dt").reset_index(drop=True)
prom_lin_sel = df_lin["score_linea"].mean()

# ── Gráfico: compara agregación simple vs por línea ──────────────────────────────
labels_lx = df_lin["label"].tolist()
fig_lin = go.Figure()
fig_lin.add_trace(go.Bar(x=labels_lx, y=df_lin["score_linea"].tolist(), name="Por línea",
    marker_color="#00A8CC", marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>Por línea: %{y}<extra></extra>"))
fig_lin.add_trace(go.Bar(x=labels_lx, y=df_lin["score_simple"].tolist(), name="Simple (15 jug.)",
    marker_color="#4a6a80", marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>Simple: %{y}<extra></extra>"))
fig_lin.add_trace(go.Scatter(x=labels_lx, y=[prom_lin_total]*len(df_lin), mode="lines",
    line=dict(color="#FF00FF", dash="dot", width=2),
    name=f"Prom. por línea ({prom_lin_total:.0f})", hoverinfo="skip"))
fig_lin.update_layout(paper_bgcolor="#1a2535", plot_bgcolor="#0f1a28", height=350,
    margin=dict(t=20, b=80, l=40, r=20), barmode="group",
    xaxis=dict(tickfont=dict(color="#7a9ab5", size=9), tickangle=-35, showgrid=False),
    yaxis=dict(tickfont=dict(color="#7a9ab5", size=9), gridcolor="#1e3048", range=[0, 100]),
    showlegend=True, legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"), bargap=0.3)
st.plotly_chart(fig_lin, use_container_width=True)

# ── Fichas: score por línea con desglose de cada sector ──────────────────────────
fichas_lin = '<div style="overflow-x:auto;"><div style="display:flex;flex-wrap:wrap;gap:16px;">'
for _, r in df_lin.iterrows():
    sc_eq = int(r["score_linea"])
    color_score = "#00CC44" if sc_eq >= 50 else ("#FFD000" if sc_eq >= 35 else "#FF4444")

    desglose_html = ""
    for grp in GRUPOS_PUESTO.keys():
        if grp not in r["desglose"]:
            continue
        v = r["desglose"][grp]
        cv = "#00CC44" if v >= 50 else ("#FFD000" if v >= 35 else "#FF4444")
        desglose_html += (
            '<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
            + '<span style="font-size:10px;color:#7a9ab5;">' + grp + '</span>'
            + '<span style="font-size:11px;font-weight:700;color:' + cv + ';">' + str(v) + '</span>'
            + '</div>'
        )

    fichas_lin += (
        '<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:10px;padding:12px;width:200px;flex-shrink:0;">'
        + '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
        + '<div>'
        + '<div style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">' + sc_equipo + ' · ' + r["fecha"] + '</div>'
        + '<div style="font-size:15px;font-weight:900;color:#ffffff;margin-top:3px;">vs ' + r["rival"] + '</div>'
        + '<div style="font-size:9px;color:#4a6a80;margin-top:2px;">Fecha ' + r["label"].split(" · ")[0][1:] + '</div>'
        + '</div>'
        + '<div style="text-align:right;">'
        + '<div style="font-size:48px;font-weight:900;color:' + color_score + ';line-height:1;">' + str(sc_eq) + '</div>'
        + '<div style="font-size:9px;color:#4a6a80;text-transform:uppercase;">x línea</div>'
        + '</div></div>'
        + '<div style="border-top:1px solid #1e3048;padding-top:8px;">' + desglose_html + '</div>'
        + '</div>'
    )
fichas_lin += '</div></div>'
st.markdown(fichas_lin, unsafe_allow_html=True)