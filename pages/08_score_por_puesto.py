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
.matriz { width: 100%; border-collapse: collapse; font-size: 12px; }
.matriz th { background: #0f1a28; color: #00A8CC; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; padding: 8px 6px; border-bottom: 2px solid #1e3048; text-align: center; }
.matriz th.col-linea { text-align: left; min-width: 130px; }
.matriz td { padding: 6px 6px; border-bottom: 1px solid #1e3048; text-align: center; color: white; }
.matriz td.col-linea { text-align: left; color: #cce0f0; font-weight: 600; }
.celda { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; min-width: 46px; }
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
# se cargan partidos nuevos, para que los scores sigan comparables entre fechas.
# Ajustá a mano los valores que tu criterio indique; cada fila debe sumar 1.00.
# Orden: Player Load, ACDC, Contactos, Dist Expl.
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

def color_semaforo(v):
    return "#00CC44" if v >= 50 else ("#FFD000" if v >= 35 else "#FF4444")

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
equipos_disp = [e for e in EQUIPOS_ORDEN if e in df_raw["Equipo"].dropna().unique()] if "Equipo" in df_raw.columns else []

# ══════════════════════════════════════════════════════════════════════════════
# NÚCLEO DEL MÉTODO: techo por bigote + pesos por puesto
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def calcular_bigotes(_df):
    """Bigote superior (Q3 + 1.5*IQR) por métrica, sobre MD de toda la liga,
    agregando por jugador-fecha. Es el techo de normalización, robusto a outliers."""
    base = _df[_df["MD"] == "MD"].groupby(["Player Name", "Fecha"]).agg(
        {c: "sum" for c in METRICAS}
    ).reset_index()
    bigotes = {}
    for c in METRICAS:
        s = base[c].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        bigotes[c] = q3 + 1.5 * (q3 - q1)
    return bigotes

BIGOTES = calcular_bigotes(df_raw)

def norm_metrica(col, val):
    """Normaliza un valor de métrica por su bigote, topeado en 1.0."""
    if pd.isna(val):
        return 0.0
    ref = BIGOTES.get(col, 0)
    return min(val / ref, 1.0) if ref > 0 else 0.0

def calc_score_jugador(row):
    """Score 0-100 de un jugador según el peso de su puesto."""
    pesos = PESOS_PUESTO.get(row.get("Grupo_Puesto"))
    if pesos is None:
        return np.nan
    score = sum(norm_metrica(c, row[c]) * pesos[c] for c in METRICAS)
    return round(score * 100)

def preparar_partido(df_fecha):
    """Agrupa por jugador, aplica filtro de minutos, imputa contactos atípicos y
    calcula el score individual."""
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

def score_equipo(df_part, ponderar):
    """Agregación SIMPLE: todos los jugadores a la misma bolsa."""
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
    """Agregación POR LÍNEA: promedia cada grupo y después promedia los grupos."""
    d = df_part.dropna(subset=["Score"])
    if len(d) == 0:
        return 0
    por_linea = []
    for _, g in d.groupby("Grupo_Puesto"):
        if ponderar:
            if g["Minutos"].sum() == 0:
                continue
            por_linea.append(np.average(g["Score"], weights=g["Minutos"]))
        else:
            por_linea.append(g["Score"].mean())
    if not por_linea:
        return 0
    val = np.mean(por_linea)
    return int(round(val)) if not np.isnan(val) else 0

def scores_por_linea(df_part, ponderar):
    """Score de cada línea por separado."""
    d = df_part.dropna(subset=["Score"])
    out = {}
    for grp, g in d.groupby("Grupo_Puesto"):
        if ponderar and g["Minutos"].sum() > 0:
            out[grp] = int(round(np.average(g["Score"], weights=g["Minutos"])))
        elif len(g) > 0:
            out[grp] = int(round(g["Score"].mean()))
    return out

def rango_y(valores, margen=5, piso=0):
    """Rango dinámico para el eje Y: un poco por debajo del mínimo y 'margen'
    por encima del máximo, para que se aprecien las diferencias."""
    vals = [v for v in valores if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if not vals:
        return [0, 100]
    lo = max(piso, min(vals) - margen)
    hi = max(vals) + margen
    if hi <= lo:
        hi = lo + 10
    return [lo, hi]

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
# FILTROS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">💪 Scoring Físico por Puesto</div>', unsafe_allow_html=True)

sc_equipo = None
sc_puesto = None
sc_jugador = None
sc_participacion = "Sesión completa"

f1, f2, f3, f4, f5 = st.columns([3, 2, 2, 2, 2])

with f1:
    st.markdown('<span class="filtro-label">Vista</span>', unsafe_allow_html=True)
    sc_vista = st.radio("", ["Plantel", "Equipo", "Puesto", "Jugador"],
                        horizontal=True, label_visibility="collapsed", key="sp_vista")

with f2:
    if sc_vista == "Jugador":
        st.markdown('<span class="filtro-label">Jugador</span>', unsafe_allow_html=True)
        sc_jugador = st.selectbox("", sorted(df_raw["Player Name"].dropna().unique()),
                                  label_visibility="collapsed", key="sp_ju")
    elif sc_vista == "Puesto":
        st.markdown('<span class="filtro-label">Puesto</span>', unsafe_allow_html=True)
        sc_puesto = st.selectbox("", list(GRUPOS_PUESTO.keys()),
                                 label_visibility="collapsed", key="sp_pu")
    elif sc_vista == "Equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        sc_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="sp_eq")

with f3:
    if sc_vista in ("Jugador", "Puesto"):
        st.markdown('<span class="filtro-label">Participación</span>', unsafe_allow_html=True)
        sc_participacion = st.radio("", ["Sesión completa", "Solo 1 equipo"],
                                    horizontal=False, label_visibility="collapsed", key="sp_part")

with f4:
    if sc_vista in ("Jugador", "Puesto") and sc_participacion == "Solo 1 equipo":
        st.markdown('<span class="filtro-label">Equipo</span>', unsafe_allow_html=True)
        sc_equipo = st.selectbox("", equipos_disp, label_visibility="collapsed", key="sp_eq2")

with f5:
    st.markdown('<span class="filtro-label">Cálculo del equipo</span>', unsafe_allow_html=True)
    sc_modo = st.radio("", ["Sin ponderar", "Ponderado x minutos"],
                       horizontal=False, label_visibility="collapsed", key="sp_modo")
ponderar = (sc_modo == "Ponderado x minutos")

# ── Aplicar filtros ──────────────────────────────────────────────────────────
df_md_sc = df_raw[df_raw["MD"] == "MD"].copy()
if sc_equipo:
    df_md_sc = df_md_sc[df_md_sc["Equipo"] == sc_equipo]
if sc_vista == "Jugador" and sc_jugador:
    df_md_sc = df_md_sc[df_md_sc["Player Name"] == sc_jugador]
elif sc_vista == "Puesto" and sc_puesto:
    df_md_sc = df_md_sc[df_md_sc["Position Name"].isin(GRUPOS_PUESTO.get(sc_puesto, []))]

# Numeración de fechas según el equipo de referencia
equipo_ref = sc_equipo or (equipos_disp[0] if equipos_disp else None)
fechas_ref = sorted(df_raw[(df_raw["MD"] == "MD") & (df_raw["Equipo"] == equipo_ref)]["Fecha"].unique()) if equipo_ref else []
num_fecha = {f: i + 1 for i, f in enumerate(fechas_ref)}

fechas_sc = sorted(df_md_sc["Fecha"].unique())
opciones = {}
for fecha in fechas_sc:
    rival = df_md_sc[df_md_sc["Fecha"] == fecha]["Rival"].iloc[0] if "Rival" in df_md_sc.columns else "—"
    num = num_fecha.get(fecha, "?")
    label = "F" + str(num) + " · " + pd.Timestamp(fecha).strftime("%d/%m") + " vs " + str(rival)
    opciones[label] = fecha

if len(opciones) == 0:
    st.warning("No hay partidos disponibles para esta selección.")
    st.stop()

st.markdown('<span class="filtro-label">Partidos</span>', unsafe_allow_html=True)
partidos_sel = st.multiselect("", list(opciones.keys()), default=list(opciones.keys()),
                              label_visibility="collapsed", key="sp_partidos")
if not partidos_sel:
    st.info("Seleccioná al menos un partido.")
    st.stop()

# ── Mejores promedios por métrica (vara de las barras) ──────────────────────────
mejores_promedios = {}
for col in METRICAS:
    proms = []
    for fec in fechas_sc:
        dp = preparar_partido(df_md_sc[df_md_sc["Fecha"] == fec])
        if len(dp) > 0:
            proms.append(dp[col].mean())
    mejores_promedios[col] = max(proms) if proms else 1

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1: SCORE (agregación simple) + fichas con 4 métricas
# ══════════════════════════════════════════════════════════════════════════════
scores_todos = []
for fec in fechas_sc:
    dp = preparar_partido(df_md_sc[df_md_sc["Fecha"] == fec])
    if len(dp) > 0:
        scores_todos.append(score_equipo(dp, ponderar))
prom_total = np.mean(scores_todos) if scores_todos else 0

datos = []
for label in [l for l in opciones.keys() if l in partidos_sel]:
    dp = preparar_partido(df_md_sc[df_md_sc["Fecha"] == opciones[label]])
    if len(dp) == 0:
        continue
    datos.append({
        "label": label, "rival": label.split(" vs ")[-1],
        "fecha": label.split(" · ")[1].split(" vs ")[0],
        "score": score_equipo(dp, ponderar),
        **{col: dp[col].mean() for col in METRICAS},
    })

df_graf = pd.DataFrame(datos)
df_graf["fecha_dt"] = pd.to_datetime(df_graf["fecha"], format="%d/%m")
df_graf = df_graf.sort_values("fecha_dt").reset_index(drop=True)
prom_sel = df_graf["score"].mean()

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
    yaxis=dict(tickfont=dict(color="#7a9ab5", size=9), gridcolor="#1e3048",
               range=rango_y(scores + [prom_total, prom_sel])),
    showlegend=True, legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"), bargap=0.3)
st.plotly_chart(fig, use_container_width=True)

# Fichas con las 4 métricas
titulo_ficha = sc_jugador or (sc_puesto if sc_vista == "Puesto" else None) or sc_equipo or "Plantel"
fichas_html = '<div style="overflow-x:auto;"><div style="display:flex;flex-wrap:wrap;gap:16px;">'
for label in [l for l in opciones.keys() if l in partidos_sel]:
    dp = preparar_partido(df_md_sc[df_md_sc["Fecha"] == opciones[label]])
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
        cb = "#00CC44" if pct >= 90 else ("#FFD000" if pct >= 70 else "#FF4444")
        barras_html += (
            '<div style="margin-bottom:8px;">'
            + '<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
            + '<span style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:0.5px;">' + SCORING_METRICAS[col] + '</span>'
            + '<span style="font-size:10px;font-weight:700;color:#ffffff;">' + f"{val_prom:.0f}" + '</span>'
            + '</div>'
            + '<div style="background:#1e3048;border-radius:3px;height:5px;width:100%;">'
            + '<div style="background:' + cb + ';width:' + f"{pct:.0f}" + '%;height:5px;border-radius:3px;"></div>'
            + '</div></div>'
        )
    cs = color_semaforo(sc_eq)
    fichas_html += (
        '<div style="background:#0f1a28;border:1px solid #1e3048;border-radius:10px;padding:12px;width:190px;flex-shrink:0;">'
        + '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">'
        + '<div>'
        + '<div style="font-size:10px;color:#7a9ab5;text-transform:uppercase;letter-spacing:1px;">' + str(titulo_ficha) + ' · ' + fecha_label + '</div>'
        + '<div style="font-size:15px;font-weight:900;color:#ffffff;margin-top:3px;">vs ' + rival_label + '</div>'
        + '<div style="font-size:9px;color:#4a6a80;margin-top:2px;">Fecha ' + label.split(" · ")[0][1:] + '</div>'
        + '</div>'
        + '<div style="text-align:right;">'
        + '<div style="font-size:48px;font-weight:900;color:' + cs + ';line-height:1;">' + str(sc_eq) + '</div>'
        + '<div style="font-size:9px;color:#4a6a80;text-transform:uppercase;">score</div>'
        + '</div></div>'
        + barras_html + '</div>'
    )
fichas_html += '</div></div>'
st.markdown(fichas_html, unsafe_allow_html=True)

# ── Tabla de pesos por puesto (referencia) ──────────────────────────────────────
st.markdown('<div class="seccion-header">⚖️ Pesos por puesto (fijos)</div>', unsafe_allow_html=True)
filas = ""
for grp in GRUPOS_PUESTO.keys():
    if grp not in PESOS_PUESTO:
        continue
    celdas = "".join(f'<td>{PESOS_PUESTO[grp][c]*100:.0f}</td>' for c in METRICAS)
    filas += f'<tr><td class="col-linea">{grp}</td>{celdas}</tr>'
cab = "".join(f'<th>{SCORING_METRICAS[c]}</th>' for c in METRICAS)
st.markdown(
    '<table class="matriz"><tr><th class="col-linea">Puesto</th>' + cab + '</tr>' + filas + '</table>',
    unsafe_allow_html=True
)

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2: SCORE AGREGADO POR LÍNEA + matriz línea × métrica
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">🧩 Score agregado por línea</div>', unsafe_allow_html=True)

scores_lin_todos = []
for fec in fechas_sc:
    dp = preparar_partido(df_md_sc[df_md_sc["Fecha"] == fec])
    if len(dp) > 0:
        scores_lin_todos.append(score_equipo_por_linea(dp, ponderar))
prom_lin_total = np.mean(scores_lin_todos) if scores_lin_todos else 0

datos_lin = []
for label in [l for l in opciones.keys() if l in partidos_sel]:
    dp = preparar_partido(df_md_sc[df_md_sc["Fecha"] == opciones[label]])
    if len(dp) == 0:
        continue
    datos_lin.append({
        "label": label, "rival": label.split(" vs ")[-1],
        "fecha": label.split(" · ")[1].split(" vs ")[0],
        "score_simple": score_equipo(dp, ponderar),
        "score_linea": score_equipo_por_linea(dp, ponderar),
    })

df_lin = pd.DataFrame(datos_lin)
df_lin["fecha_dt"] = pd.to_datetime(df_lin["fecha"], format="%d/%m")
df_lin = df_lin.sort_values("fecha_dt").reset_index(drop=True)
prom_lin_sel = df_lin["score_linea"].mean()

labels_lx = df_lin["label"].tolist()
y_lin = df_lin["score_linea"].tolist() + df_lin["score_simple"].tolist() + [prom_lin_total]
fig_lin = go.Figure()
fig_lin.add_trace(go.Bar(x=labels_lx, y=df_lin["score_linea"].tolist(), name="Por línea",
    marker_color="#00A8CC", marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>Por línea: %{y}<extra></extra>"))
fig_lin.add_trace(go.Bar(x=labels_lx, y=df_lin["score_simple"].tolist(), name="Simple",
    marker_color="#4a6a80", marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>Simple: %{y}<extra></extra>"))
fig_lin.add_trace(go.Scatter(x=labels_lx, y=[prom_lin_total]*len(df_lin), mode="lines",
    line=dict(color="#FF00FF", dash="dot", width=2),
    name=f"Prom. por línea ({prom_lin_total:.0f})", hoverinfo="skip"))
fig_lin.update_layout(paper_bgcolor="#1a2535", plot_bgcolor="#0f1a28", height=350,
    margin=dict(t=20, b=80, l=40, r=20), barmode="group",
    xaxis=dict(tickfont=dict(color="#7a9ab5", size=9), tickangle=-35, showgrid=False),
    yaxis=dict(tickfont=dict(color="#7a9ab5", size=9), gridcolor="#1e3048", range=rango_y(y_lin)),
    showlegend=True, legend=dict(font=dict(color="white", size=10), bgcolor="#0f1a28"), bargap=0.3)
st.plotly_chart(fig_lin, use_container_width=True)

# ── Matriz línea × métrica (un partido a la vez) ─────────────────────────────────
st.markdown('<div class="seccion-header">📊 Detalle línea × métrica</div>', unsafe_allow_html=True)

m1, _ = st.columns([2, 6])
with m1:
    st.markdown('<span class="filtro-label">Partido</span>', unsafe_allow_html=True)
    partido_matriz = st.selectbox("", [l for l in opciones.keys() if l in partidos_sel],
                                  label_visibility="collapsed", key="sp_matriz")

dp_m = preparar_partido(df_md_sc[df_md_sc["Fecha"] == opciones[partido_matriz]])
if len(dp_m) == 0:
    st.warning("Sin datos para este partido.")
else:
    filas_m = ""
    for grp in GRUPOS_PUESTO.keys():
        g = dp_m[dp_m["Grupo_Puesto"] == grp].dropna(subset=["Score"])
        if len(g) == 0:
            continue
        if ponderar and g["Minutos"].sum() > 0:
            sc_l = int(round(np.average(g["Score"], weights=g["Minutos"])))
        else:
            sc_l = int(round(g["Score"].mean()))
        celdas = ""
        for col in METRICAS:
            if ponderar and g["Minutos"].sum() > 0:
                val_crudo = np.average(g[col], weights=g["Minutos"])
            else:
                val_crudo = g[col].mean()
            nivel = round(norm_metrica(col, val_crudo) * 100)   # % del techo (bigote)
            cc = "#00CC44" if nivel >= 75 else ("#FFD000" if nivel >= 50 else "#FF4444")
            celdas += f'<td><span class="celda" style="background:{cc}22;color:{cc};">{nivel}</span></td>'
        csl = color_semaforo(sc_l)
        filas_m += (
            f'<tr><td class="col-linea">{grp}</td>'
            + f'<td><span class="celda" style="background:{csl}33;color:{csl};font-size:13px;">{sc_l}</span></td>'
            + celdas + '</tr>'
        )
    cab_m = "".join(f'<th>{SCORING_METRICAS[c]}</th>' for c in METRICAS)
    st.markdown(
        '<div style="overflow-x:auto;"><table class="matriz">'
        + '<tr><th class="col-linea">Línea</th><th>Score</th>' + cab_m + '</tr>'
        + filas_m + '</table></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-size:10px;color:#4a6a80;margin-top:8px;">'
        'Score = puntaje de la línea (0-100). Cada métrica muestra su nivel como % del techo (bigote superior).'
        '</div>', unsafe_allow_html=True
    )