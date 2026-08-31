import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64, os

st.set_page_config(page_title="Estado de Alerta", layout="wide", initial_sidebar_state="expanded")

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
div[data-testid="stPopover"] > div > button {
    background-color: #0f1a28 !important; border: 1px solid #1e3048 !important;
    border-radius: 6px !important; color: white !important; font-size: 13px !important;
    width: 100% !important; text-align: left !important;
}
div[data-testid="stPopover"] > div > button:hover { border-color: #00A8CC !important; color: #00A8CC !important; }
div[data-testid="stPopoverBody"] { background-color: #0f1a28 !important; border: 1px solid #1e3048 !important; border-radius: 8px !important; }
div[data-testid="stPopoverBody"] label { color: #cce0f0 !important; font-size: 13px !important; }
div[data-testid="stPopoverBody"] p     { color: #7a9ab5 !important; font-size: 11px !important; }
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
    padding: 3px 6px !important; border-radius: 6px !important; font-size: 9px !important;
    font-weight: 700 !important; color: #ffffff !important; cursor: pointer !important;
    background: transparent !important; white-space: nowrap !important;
}
div[data-testid="stRadio"] label:has(input:checked) { background-color: #00A8CC !important; }
div[data-testid="stRadio"] label p { color: #ffffff !important; }
div[data-testid="stRadio"] > label:first-child { display: none !important; }
.seccion-header {
    font-size: 11px; font-weight: 800; letter-spacing: 2px; color: #ffffff;
    background: #0f1a28; border-left: 4px solid #00A8CC;
    padding: 8px 14px; margin: 20px 0 10px 0;
    text-transform: uppercase; border-radius: 0 4px 4px 0;
}
div[data-testid="stButton"] button {
    background-color: #1a2535 !important;
    border: 1px solid #2a4060 !important;
    color: white !important;
    font-size: 11px !important;
    width: 160px !important;
}
div[data-testid="stHorizontalBlock"] {
    gap: 0px !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    padding: 0px !important;
    min-width: 0px !important;
}
.tabla-semaforo { width: 100%; border-collapse: collapse; font-size: 12px; }
.tabla-semaforo th { background: #0f1a28; color: #00A8CC; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; padding: 8px 6px; border-bottom: 2px solid #1e3048; text-align: center; }
.tabla-semaforo th.col-jugador { text-align: left; min-width: 140px; }
.tabla-semaforo td { padding: 6px 6px; border-bottom: 1px solid #1e3048; text-align: center; color: white; }
.tabla-semaforo td.col-jugador { text-align: left; color: #cce0f0; font-weight: 600; }
.tabla-semaforo tr:hover td { background: #1e3048 !important; }
.celda-valor { display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# ── Métricas (10, para tabla de detalle) ──────────────────────────────────────
COLS_DIST_80 = [
    "80% Velocity Band 5 Total Distance (Set 2)",
    "90% Velocity Band 6 Total Distance (Set 2)",
    "95% Velocity Band 7 Total Distance (Set 2)",
    "100% Velocity Band 8 Total Distance (Set 2)",
]
COLS_EFF_80 = [
    "80% Velocity Band 5 Total Effort Count (Set 2)",
    "90% Velocity Band 6 Total Effort Count (Set 2)",
    "95% Velocity Band 7 Total Effort Count (Set 2)",
    "100% Velocity Band 8 Total Effort Count (Set 2)",
]
COL_DIST_80 = "Dist >80% Vel Max"
COL_EFF_80  = "# >80% Vel Max"

# Las 10 métricas se usan SOLO en la tabla de detalle inferior
METRICAS = {
    "Distancia Total":                          ("Dist Tot",     "#7FB3E0"),
    "AI 18 Km/h":                               ("HSR",          "#F2A8C0"),
    "DT + 25 Km/h":                             ("Sprint",       "#C4A8E0"),
    "+25 Km/h #":                               ("N° Sprints",   "#F5C09A"),
    COL_DIST_80:                                ("Dist >80%",    "#FFB347"),
    COL_EFF_80:                                 ("# >80%",       "#FF8C69"),
    "Acel 2,5 m/ss #":                          ("N° Acel",      "#A8DDB5"),
    "Desacel -2,5 m/ss #":                      ("N° Decel",     "#F0DC96"),
    "Contact Involvement Total Count Avg":      ("Impactos",     "#A8E0DC"),
    "Total Player Load":                        ("Player Load",  "#B8A8E0"),
}
COLS = list(METRICAS.keys())

GRUPOS_PUESTO = {
    "Primeras":         ["Pilar izquierdo", "Pilar derecho", "Hooker"],
    "Segundas":         ["Segunda Linea"],
    "Terceras":         ["Ala", "Octavo"],
    "Pareja de medios": ["Medio Scrum", "Apertura"],
    "Centros":          ["Centro"],
    "3 del fondo":      ["Wing", "Full Back"],
}

# ── Ejes de carga (score de riesgo) ───────────────────────────────────────────
# 4 ejes independientes — evitan la inflación por correlación entre métricas.
EJES = {
    "Volumen":       ["Distancia Total"],
    "Intensidad":    ["AI 18 Km/h"],
    "Neuromuscular": ["Acel 2,5 m/ss #", "Desacel -2,5 m/ss #"],
    "Impactos":      ["Contact Involvement Total Count Avg"],
}
EJES_LABELS = {
    "Volumen":       ("Volumen",       "#7FB3E0"),
    "Intensidad":    ("Intensidad",    "#F2A8C0"),
    "Neuromuscular": ("Neuromuscular", "#96E2A9"),
    "Impactos":      ("Impactos",      "#DFE0A8"),
}
COLS_EJES = list(EJES.keys())

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# Semáforo ASIMÉTRICO:
#   zona segura 0.80–1.30 | sobrecarga 1.30–1.50 | riesgo alto >1.50
#   descarga baja (ratio bajo) se muestra pero NO penaliza el score.
def color_ratio(r):
    if r is None or np.isnan(r): return "#4a6a80"
    if r >= 1.50: return "#FF0000"
    if r >= 1.30: return "#FFD000"
    if r >= 0.80: return "#00CC44"
    if r >= 0.60: return "#FF8C00"
    return "#8A2BE2"

def score_ratio(r):
    if r is None or np.isnan(r): return 1
    if r >= 1.50: return 3
    if r >= 1.30: return 2
    return 1

# Umbrales de score: 4 ejes × 1–3 pts c/u → rango 4–12
UMBRAL_VERDE = 6
UMBRAL_AM    = 8

def calcular_score_ejes(row):
    scores = [row[f"score_{eje}"] for eje in COLS_EJES]
    total  = sum(scores)
    if total <= UMBRAL_VERDE: return total, "#00CC44", "✅ Óptimo"
    if total <= UMBRAL_AM:    return total, "#FFD000", "⚠️ Precaución"
    return total, "#FF0000", "🚨 Alerta"

# ── Carga de datos ────────────────────────────────────────────────────────────
def cargar_datos():
    if "df_excel" not in st.session_state:
        st.session_state["df_excel"] = pd.read_parquet("totales_gps.parquet")
    df = st.session_state["df_excel"].copy()
    df = df[
        (df["Period Name"] == "Session") &
        (df["Period Tags"] != "Diferenciado")
    ].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    df[COL_DIST_80] = df[COLS_DIST_80].fillna(0).sum(axis=1)
    df[COL_EFF_80]  = df[COLS_EFF_80].fillna(0).sum(axis=1)
    return df

df_raw = cargar_datos()

# ── EWMA por jugador y métrica (10) — para tabla de detalle ──────────────────
@st.cache_data
def calcular_ewma(df):
    agg = df.groupby(["Player Name", "Position Name", "Fecha"])[COLS].sum().reset_index()
    resultados = []
    for jugador, g in agg.groupby("Player Name"):
        g = g.sort_values("Fecha").copy()
        idx = pd.date_range(g["Fecha"].min(), g["Fecha"].max(), freq="D")
        g_diario = g.set_index("Fecha").reindex(idx)
        for col in COLS:
            g_diario[col] = g_diario[col].fillna(0)
        pos = g["Position Name"].iloc[-1]
        for col in COLS:
            serie       = g_diario[col].astype(float)
            ewma_aguda  = serie.ewm(span=7,  adjust=False).mean()
            ewma_cronica= serie.ewm(span=28, adjust=False).mean()
            for fecha in g["Fecha"]:
                if fecha not in ewma_aguda.index: continue
                ag = ewma_aguda[fecha]; cr = ewma_cronica[fecha]
                resultados.append({
                    "Player Name": jugador, "Position Name": pos,
                    "Fecha": fecha, "Metrica": col,
                    "EWMA_Aguda": ag, "EWMA_Cronica": cr,
                    "Ratio": ag / cr if cr > 0 else np.nan,
                })
    return pd.DataFrame(resultados)

# ── EWMA por jugador y EJE (4) — para score y gráficos ──────────────────────
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
            serie       = g_diario[eje].astype(float)
            ewma_aguda  = serie.ewm(span=7,  adjust=False).mean()
            ewma_cronica= serie.ewm(span=28, adjust=False).mean()
            for fecha in g["Fecha"]:
                if fecha not in ewma_aguda.index: continue
                ag = ewma_aguda[fecha]; cr = ewma_cronica[fecha]
                resultados.append({
                    "Player Name": jugador, "Position Name": pos,
                    "Fecha": fecha, "Eje": eje,
                    "EWMA_Aguda": ag, "EWMA_Cronica": cr,
                    "Ratio": ag / cr if cr > 0 else np.nan,
                })
    return pd.DataFrame(resultados)

df_ewma      = calcular_ewma(df_raw)
df_ewma_ejes = calcular_ewma_ejes(df_raw)

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
    f'<div class="topbar-divider"></div><span class="topbar-page">Control Semanal</span></div>',
    unsafe_allow_html=True
)


# ── Filtros globales ──────────────────────────────────────────────────────────
todos_jugadores_raw = sorted(df_raw[df_raw["MD"] != "MD"]["Player Name"].dropna().unique().tolist())
todos_puestos       = sorted(df_raw["Position Name"].dropna().unique().tolist())
todas_fechas        = sorted(df_ewma["Fecha"].unique(), reverse=True)
DIAS_ES             = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

def borrar_keys(prefix):
    for k in list(st.session_state.keys()):
        if k.startswith(prefix) and not k.endswith(("_todos",)):
            if isinstance(st.session_state[k], bool):
                st.session_state[k] = False

def get_sel(prefix, opciones):
    return [op for op in opciones if st.session_state.get(f"{prefix}{op}", False)]

def render_filtro(col_ctx, label, prefix, opciones):
    sel = [op for op in opciones if st.session_state.get(f"{prefix}{op}", False)]
    btn = "Todos ▾" if not sel else (f"{sel[0]} ▾" if len(sel)==1 else f"{len(sel)} selec. ▾")
    with col_ctx:
        st.markdown(f'<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">{label}</span>', unsafe_allow_html=True)
        with st.popover(btn, use_container_width=True):
            st.button("✓ Todos", key=f"{prefix}todos", use_container_width=True, on_click=borrar_keys, args=(prefix,))
            for op in opciones:
                st.checkbox(str(op), key=f"{prefix}{op}")

def render_filtro_puesto(col_ctx, grupos, prefix, opciones_validas):
    sel = [op for op in sum(grupos.values(), []) if st.session_state.get(f"{prefix}{op}", False)]
    btn = "Todos ▾" if not sel else (f"{sel[0]} ▾" if len(sel)==1 else f"{len(sel)} selec. ▾")
    with col_ctx:
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Puesto</span>', unsafe_allow_html=True)
        with st.popover(btn, use_container_width=True):
            st.button("✓ Todos", key=f"{prefix}todos", use_container_width=True, on_click=borrar_keys, args=(prefix,))
            for grupo, puestos in grupos.items():
                puestos_v = [p for p in puestos if p in opciones_validas]
                if not puestos_v: continue
                todos_g = all(st.session_state.get(f"{prefix}{p}", False) for p in puestos_v)
                g_chk = st.checkbox(grupo.upper(), value=todos_g, key=f"{prefix}grupo_{grupo}")
                if g_chk != todos_g:
                    for p in puestos_v:
                        st.session_state[f"{prefix}{p}"] = g_chk
                    st.rerun()
                for p in puestos_v:
                    _, col_chk = st.columns([0.15, 0.85])
                    with col_chk:
                        st.checkbox(p, key=f"{prefix}{p}")

jug_sel    = get_sel("ew_jug_", todos_jugadores_raw)
pue_sel    = get_sel("ew_pue_", todos_puestos)
jug_activo = jug_sel if jug_sel else todos_jugadores_raw
pue_activo = pue_sel if pue_sel else todos_puestos

# Selector de fecha
opciones_fecha = []
for f in todas_fechas:
    dia = DIAS_ES[f.weekday()]
    fila_md = df_raw[(df_raw["Fecha"] == f) & (df_raw["MD"] == "MD") & (df_raw["Rival"].notna())]
    rival_str = f" · {fila_md['Rival'].iloc[0]}" if not fila_md.empty else ""
    opciones_fecha.append(f"{dia} {f.day:02d}/{f.month:02d}{rival_str}")

fecha_idx_tmp   = st.session_state.get("ew_fecha", 0)
fecha_sel_tmp   = todas_fechas[fecha_idx_tmp] if fecha_idx_tmp < len(todas_fechas) else todas_fechas[0]
fecha_desde_tmp = fecha_sel_tmp - pd.Timedelta(days=28)

todos_jugadores_raw = sorted(df_raw[
    (df_raw["MD"] != "MD") &
    (df_raw["Fecha"] >= fecha_desde_tmp) &
    (df_raw["Fecha"] <= fecha_sel_tmp)
]["Player Name"].dropna().unique().tolist())

f1, f2, f3, f4, f5 = st.columns(5)
render_filtro(f1, "Jugador", "ew_jug_", todos_jugadores_raw)
render_filtro_puesto(f2, GRUPOS_PUESTO, "ew_pue_", todos_puestos)

with f3:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Fecha</span>', unsafe_allow_html=True)
    fecha_idx = st.selectbox(
        label="Fecha", options=range(len(todas_fechas)),
        format_func=lambda i: opciones_fecha[i],
        key="ew_fecha", label_visibility="collapsed",
    )
    fecha_sel   = todas_fechas[fecha_idx]
    fecha_desde = fecha_sel - pd.Timedelta(days=28)
    todos_jugadores = sorted(df_raw[
        (df_raw["Fecha"] >= fecha_desde) &
        (df_raw["Fecha"] <= fecha_sel) &
        (df_raw["MD"] != "MD")
    ]["Player Name"].dropna().unique().tolist())

st.markdown("<hr style='border-color:#1e3048; margin:8px 0 16px 0;'>", unsafe_allow_html=True)

# ── Score EWMA por jugador (4 ejes) ──────────────────────────────────────────
fecha_desde   = fecha_sel - pd.Timedelta(days=28)
jugs_activos_28 = df_raw[
    (df_raw["Fecha"] >= fecha_desde) &
    (df_raw["Fecha"] <= fecha_sel) &
    (df_raw["MD"] != "MD")
]["Player Name"].unique()

df_fecha = df_ewma_ejes[
    (df_ewma_ejes["Fecha"] == fecha_sel) &
    (df_ewma_ejes["Player Name"].isin(jug_activo)) &
    (df_ewma_ejes["Player Name"].isin(jugs_activos_28)) &
    (df_ewma_ejes["Position Name"].isin(pue_activo))
].copy()

if df_fecha.empty:
    st.warning("No hay datos EWMA para la fecha seleccionada.")
    st.stop()

pivot = df_fecha.pivot_table(
    index=["Player Name", "Position Name"], columns="Eje", values="Ratio"
).reset_index()

for eje in COLS_EJES:
    pivot[f"score_{eje}"] = pivot[eje].apply(score_ratio) if eje in pivot.columns else 1

pivot[["Score_Total", "Color_Score", "Label_Score"]] = pivot.apply(
    lambda row: pd.Series(calcular_score_ejes(row)), axis=1
)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — ESTADO GENERAL
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">🚨 Estado general del equipo</div>', unsafe_allow_html=True)

sesiones_28_alerta = df_raw[
    (df_raw["Fecha"] >= fecha_sel - pd.Timedelta(days=28)) &
    (df_raw["Fecha"] <= fecha_sel)
].groupby("Player Name")["Fecha"].nunique()
jugadores_activos_alerta = sesiones_28_alerta[sesiones_28_alerta >= 8].index

pivot_activo = pivot[pivot["Player Name"].isin(jugadores_activos_alerta)]

n_alerta     = len(pivot_activo[pivot_activo["Color_Score"] == "#FF0000"])
n_precaucion = len(pivot_activo[pivot_activo["Color_Score"] == "#FFD000"])
n_optimo     = len(pivot_activo[pivot_activo["Color_Score"] == "#00CC44"])
total_jug    = len(pivot_activo)

if "ew_filtro_estado" not in st.session_state:
    st.session_state["ew_filtro_estado"] = None

def toggle_filtro(estado):
    st.session_state["ew_filtro_estado"] = None if st.session_state["ew_filtro_estado"] == estado else estado

st.markdown(
    f'<div style="display:flex; gap:8px; margin-bottom:8px;">'
    f'<div style="background:#0f1a28; border:{"4px" if st.session_state["ew_filtro_estado"]=="#FF0000" else "2px"} solid #FF0000; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:#FF0000;">{n_alerta}</div></div>'
    f'<div style="background:#0f1a28; border:{"4px" if st.session_state["ew_filtro_estado"]=="#FFD000" else "2px"} solid #FFD000; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:#FFD000;">{n_precaucion}</div></div>'
    f'<div style="background:#0f1a28; border:{"4px" if st.session_state["ew_filtro_estado"]=="#00CC44" else "2px"} solid #00CC44; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:#00CC44;">{n_optimo}</div></div>'
    f'<div style="background:#0f1a28; border:1px solid #1e3048; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:white;">{total_jug}</div>'
    f'<div style="font-size:11px; font-weight:700; color:#7a9ab5; text-transform:uppercase; letter-spacing:1px; margin-top:2px;">Totales</div></div>'
    f'</div>',
    unsafe_allow_html=True
)

col_alerta, col_precaucion, col_optimo, _ = st.columns([0.145, 0.145, 0.145, 0.565])
with col_alerta:    st.button("🚨 Alerta",     key="btn_alerta",     on_click=toggle_filtro, args=("#FF0000",), use_container_width=True)
with col_precaucion:st.button("⚠️ Precaución", key="btn_precaucion", on_click=toggle_filtro, args=("#FFD000",), use_container_width=True)
with col_optimo:    st.button("✅ Óptimo",     key="btn_optimo",     on_click=toggle_filtro, args=("#00CC44",), use_container_width=True)

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

filtro_activo = st.session_state["ew_filtro_estado"]
if filtro_activo:
    df_grid = pivot_activo[pivot_activo["Color_Score"] == filtro_activo].sort_values("Player Name")
else:
    df_grid = pivot_activo[pivot_activo["Color_Score"] == "#FF0000"].sort_values("Score_Total", ascending=False)

if df_grid.empty:
    st.markdown('<div style="color:#00CC44; font-size:14px; font-weight:700;">✅ Todos los jugadores en estado óptimo</div>', unsafe_allow_html=True)
else:
    grid_html = '<div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px;">'
    for _, row in df_grid.iterrows():
        color  = row["Color_Score"]
        label  = row["Label_Score"]
        nombre = row["Player Name"]
        grid_html += (
            f'<div style="background:#0f1a28; border:2px solid {color}; border-radius:10px;'
            f' padding:10px 12px; width:140px; flex:0 0 140px; height:100px;'
            f' display:flex; flex-direction:column; justify-content:space-between;">'
            f'<div style="font-size:12px; font-weight:700; color:white; margin-bottom:2px;">{nombre}</div>'
            f'<div style="font-size:13px; font-weight:900; color:{color};">{label}</div>'
            f'</div>'
        )
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1e3048; margin:20px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — DETALLE POR JUGADOR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">👤 Detalle por jugador</div>', unsafe_allow_html=True)

jug_default = st.session_state.get("ew_jug_sel_detalle", todos_jugadores[0] if todos_jugadores else None)
if not jug_default or jug_default not in todos_jugadores:
    jug_default = todos_jugadores[0] if todos_jugadores else None

if not jug_default:
    st.warning("No hay jugadores disponibles para el período seleccionado.")
    st.stop()

col_sel, col_eje_sel, _ = st.columns([0.25, 0.25, 0.50])
with col_sel:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Jugador</span>', unsafe_allow_html=True)
    jug_detalle = st.selectbox(
        label="Jugador detalle",
        options=todos_jugadores,
        index=todos_jugadores.index(jug_default) if jug_default in todos_jugadores else 0,
        key="ew_jug_detalle",
        label_visibility="collapsed",
    )

with col_eje_sel:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Eje</span>', unsafe_allow_html=True)
    eje_detalle = st.selectbox(
        label="Eje detalle",
        options=COLS_EJES + ["Todos"],
        index=0,
        format_func=lambda e: e if e == "Todos" else EJES_LABELS[e][0],
        key="ew_eje_detalle",
        label_visibility="collapsed",
    )    

# Score actual del jugador
row_actual  = pivot[pivot["Player Name"] == jug_detalle]
score_actual= int(row_actual["Score_Total"].iloc[0])  if not row_actual.empty else None
color_actual= row_actual["Color_Score"].iloc[0]       if not row_actual.empty else "#4a6a80"
label_actual= row_actual["Label_Score"].iloc[0]       if not row_actual.empty else "—"

# ── Header: 4 ejes dentro del cuadrado — label blanco+negrita ─────────────
metricas_html = ""
for eje in COLS_EJES:
    etq, _  = EJES_LABELS[eje]
    row_m   = pivot[pivot["Player Name"] == jug_detalle]
    ratio_m = row_m[eje].iloc[0] if not row_m.empty and eje in row_m.columns else np.nan
    color_m = color_ratio(ratio_m)
    val_str = "—" if (ratio_m is None or np.isnan(ratio_m)) else f"{ratio_m:.2f}".replace(".", ",")
    metricas_html += (
        f'<div style="flex:1; text-align:center; padding:4px;">'
        f'<div style="font-size:11px; font-weight:800; color:white; text-transform:uppercase; '
        f'letter-spacing:1px; margin-bottom:6px;">{etq}</div>'
        f'<div style="font-size:26px; font-weight:900; color:{color_m};">{val_str}</div>'
        f'</div>'
    )

# Leyenda de construcción de ejes
def_html = (
    '<div style="display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; padding-top:10px; '
    'border-top:1px solid #1e3048;">'
    '<div style="font-size:10px; color:#7a9ab5; line-height:1.6;">'
    '<span style="color:#7FB3E0; font-weight:700;">VOLUMEN</span> = Distancia Total &nbsp;|&nbsp; '
    '<span style="color:#F2A8C0; font-weight:700;">INTENSIDAD</span> = HSR &nbsp;|&nbsp; '
    '<span style="color:#96E2A9; font-weight:700;">NEUROMUSCULAR</span> = Acel + Decel &nbsp;|&nbsp; '
    '<span style="color:#DFE0A8; font-weight:700;">IMPACTOS</span> = Contactos'
    '</div></div>'
)

st.markdown(
    f'<div style="background:#0f1a28; border:2px solid {color_actual}; border-radius:10px; '
    f'padding:16px 20px; margin-bottom:16px;">'
    f'<div style="text-align:center; margin-bottom:14px;">'
    f'<span style="font-size:26px; font-weight:900; color:white;">{jug_detalle}</span>'
    f'&nbsp;&nbsp;'
    f'<span style="font-size:22px; font-weight:900; color:{color_actual};">{label_actual}</span>'
    f'</div>'
    f'<div style="display:flex; gap:4px;">{metricas_html}</div>'
    f'{def_html}'
    f'</div>',
    unsafe_allow_html=True
)

# ── Gráficos: línea EWMA ratio (4 ejes) + barras sesiones (4 ejes) ───────────
st.markdown('<div style="margin-bottom:8px; font-size:11px; font-weight:700; color:#7a9ab5; text-transform:uppercase; letter-spacing:1px;">Evolución EWMA · últimos 28 días</div>', unsafe_allow_html=True)

col_graf, col_barras = st.columns([0.6, 0.4])

with col_graf:
    # Línea de ratio EWMA para los 4 ejes
    df_jug_ejes = df_ewma_ejes[
        (df_ewma_ejes["Player Name"] == jug_detalle) &
        (df_ewma_ejes["Fecha"] >= fecha_desde) &
        (df_ewma_ejes["Fecha"] <= fecha_sel)
    ].copy()

    fig_linea = go.Figure()
    ejes_a_graficar = COLS_EJES if eje_detalle == "Todos" else [eje_detalle]
    for eje in ejes_a_graficar:
        etq, color_eje = EJES_LABELS[eje]
        df_eje = df_jug_ejes[df_jug_ejes["Eje"] == eje].sort_values("Fecha")
        if df_eje.empty: continue
        fig_linea.add_trace(go.Scatter(
            x=df_eje["Fecha"], y=df_eje["Ratio"],
            mode="lines+markers", name=etq,
            line=dict(color=color_eje, width=2),
            marker=dict(size=5, color=color_eje),
            hovertemplate="%{x|%d/%m/%Y}<br>Ratio: %{y:,.2f}<extra></extra>",
        ))

    fig_linea.add_hline(y=0.80, line_dash="dash", line_color="#00CC44", line_width=1,
                        annotation_text="0,80", annotation_font_color="#00CC44", annotation_font_size=9)
    fig_linea.add_hline(y=1.30, line_dash="dash", line_color="#FFD000", line_width=1,
                        annotation_text="1,30", annotation_font_color="#FFD000", annotation_font_size=9)
    fig_linea.add_hline(y=1.50, line_dash="dot",  line_color="#FF0000", line_width=1,
                        annotation_text="1,50", annotation_font_color="#FF0000",  annotation_font_size=9)

    fig_linea.update_layout(
    title=dict(text="Ratio EWMA por eje", font=dict(size=12, color="white"), x=0),
    paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
    height=320, margin=dict(t=35, b=20, l=10, r=100),
    xaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=9)),
    yaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=9), zeroline=False),
    legend=dict(font=dict(color="white", size=10), bgcolor="rgba(0,0,0,0)"),
    separators=",.",
)
    st.plotly_chart(fig_linea, use_container_width=True)

with col_barras:
    # Barras de carga aguda por sesión (últimos 28 días), un grupo por eje
    df_jug_raw = df_raw[df_raw["Player Name"] == jug_detalle].copy()
    cols_base_ejes = sorted({c for cols in EJES.values() for c in cols})
    df_jug_agg = df_jug_raw.groupby("Fecha")[cols_base_ejes + ["MD"]].agg(
        {**{c: "sum" for c in cols_base_ejes}, "MD": "first"}
    ).reset_index()
    # Calcular cada eje
    for eje, cols in EJES.items():
        df_jug_agg[eje] = df_jug_agg[cols].sum(axis=1)

    df_jug_agg = df_jug_agg[
        (df_jug_agg["Fecha"] >= fecha_desde) &
        (df_jug_agg["Fecha"] <= fecha_sel)
    ].sort_values("Fecha")

    DIAS_ES2 = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    etqs_b   = [f"{DIAS_ES2[f.weekday()]} {f.day:02d}/{f.month:02d}" for f in df_jug_agg["Fecha"]]
    xs       = list(range(len(df_jug_agg)))

    fig_bar = go.Figure()
    ejes_barras = COLS_EJES if eje_detalle == "Todos" else [eje_detalle]
    for eje in ejes_barras:
        etq, color_eje = EJES_LABELS[eje]
        vals = df_jug_agg[eje].tolist()
        fig_bar.add_trace(go.Bar(
            x=xs, y=vals, name=etq,
            marker_color=color_eje, marker_line_width=0,
            opacity=0.85,
        ))

    fig_bar.update_layout(
    title=dict(text="Carga por sesión", font=dict(size=12, color="white"), x=0),
    paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
    barmode="group",
    height=320, margin=dict(t=35, b=40, l=10, r=10),
    xaxis=dict(tickmode="array", tickvals=xs, ticktext=etqs_b,
               tickfont=dict(color="#7a9ab5", size=8), tickangle=-45, showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=8), zeroline=False),
    legend=dict(font=dict(color="white", size=9), bgcolor="rgba(0,0,0,0)"),
    bargap=0.15, bargroupgap=0.05,
    separators=",.",
)
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Tabla de sesiones: 28 días, formato tabla-semaforo, 10 métricas ──────────
st.markdown('<div class="seccion-header">📋 Sesiones recientes · últimos 28 días</div>', unsafe_allow_html=True)

df_tabla_jug = df_raw[
    (df_raw["Player Name"] == jug_detalle) &
    (df_raw["Fecha"] >= fecha_desde) &
    (df_raw["Fecha"] <= fecha_sel)
].copy()
df_tabla_jug = df_tabla_jug.sort_values("Fecha", ascending=False)

# Agregar por fecha (puede haber varias filas por día por período)
cols_agg = {c: "sum" for c in COLS if c in df_tabla_jug.columns}
cols_agg["MD"]    = "first"
cols_agg["Rival"] = "first"
cols_agg["Equipo"]= "first"
cols_agg["Minutos"] = "sum"
df_tabla_agg = df_tabla_jug.groupby("Fecha").agg(cols_agg).reset_index()
df_tabla_agg = df_tabla_agg.sort_values("Fecha", ascending=False)

# Calcular medias del jugador en los 28 días (para color de celda)
medias_28 = {c: df_tabla_agg[c].mean() for c in COLS if c in df_tabla_agg.columns}

def color_celda(val, media):
    if media is None or media == 0 or np.isnan(media): return "#4a6a80", "#1e3048"
    pct = val / media
    if pct >= 1.20:   return "#00CC44", "#00CC4422"
    if pct >= 0.90:   return "#7a9ab5", "#1e3048"
    if pct >= 0.70:   return "#FFD000", "#FFD00022"
    return "#FF8C00", "#FF8C0022"

DIAS_TABLA = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]

cabecera = "<tr><th class='col-jugador'>Fecha</th><th>Tipo</th><th>Min</th>"
for col in COLS:
    cabecera += f"<th>{METRICAS[col][0]}</th>"
cabecera += "</tr>"

filas = ""
for _, row in df_tabla_agg.iterrows():
    tipo = "🏉 Partido" if row.get("MD") == "MD" else "🏃 Entrenamiento"
    rival_str = f" · {row['Rival']}" if row.get("MD") == "MD" and pd.notna(row.get("Rival")) else ""
    fecha_str = f"{DIAS_TABLA[row['Fecha'].weekday()]} {row['Fecha'].day:02d}/{row['Fecha'].month:02d}"
    min_val = row.get("Minutos", 0)
    fila = f"<tr><td class='col-jugador'>{fecha_str}{rival_str}</td><td>{tipo}</td><td style='color:#cce0f0;'>{min_val:.0f}</td>"
    for col in COLS:
        if col not in df_tabla_agg.columns:
            fila += "<td>—</td>"
            continue
        val = row[col]
        if pd.isna(val):
            fila += "<td>—</td>"
        else:
            fmt_val = f"{val:,.0f}".replace(",", ".") if val >= 10 or val == int(val) else f"{val:.1f}".replace(".", ",")
            fila += f"<td style='color:#cce0f0;'>{fmt_val}</td>"
    fila += "</tr>"
    filas += fila

if filas:
    st.markdown(
        "<div style='overflow-x:auto;'><table class='tabla-semaforo'>" + cabecera + filas + "</table></div>",
        unsafe_allow_html=True
    )
else:
    st.markdown('<div style="color:#7a9ab5; font-size:13px;">Sin sesiones registradas en los últimos 28 días.</div>', unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1e3048; margin:20px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — CARGA SEMANAL
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def calcular_perfil_competitivo(df):
    md_df   = df[df["MD"] == "MD"].copy()
    por_dia = md_df.groupby(["Player Name", "Position Name", "Fecha"]).agg(
        {**{c: "sum" for c in COLS}, "Minutos": "sum"}
    ).reset_index()
    por_dia = por_dia[(por_dia["Minutos"] >= 30) & (por_dia["Minutos"] <= 100)]
    jugadores_validos = por_dia.groupby("Player Name").size()
    jugadores_validos = jugadores_validos[jugadores_validos >= 6].index
    por_dia = por_dia[por_dia["Player Name"].isin(jugadores_validos)]
    resultados = []
    for jug, g in por_dia.groupby("Player Name"):
        pos = g["Position Name"].iloc[-1]
        row = {"Player Name": jug, "Position Name": pos}
        for col in COLS:
            vals    = g[col].dropna()
            row[col]= (vals.max() + vals.mean()) / 2 if len(vals) > 0 else np.nan
        resultados.append(row)
    return pd.DataFrame(resultados)

df_perfil = calcular_perfil_competitivo(df_raw)

st.markdown('<div class="seccion-header">📊 Carga semanal</div>', unsafe_allow_html=True)

# ── Toggle y filtros ──────────────────────────────────────────────────────────
col_tog, col_filt, col_modo, col_eq_s3, col_sem = st.columns([0.30, 0.18, 0.14, 0.14, 0.22])

with col_tog:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Ver por</span>', unsafe_allow_html=True)
    modo_s3 = st.radio(
        label="Ver por", options=["Plantel", "Equipo", "Puesto", "Jugador"],
        index=3, key="s3_modo", horizontal=True, label_visibility="collapsed",
    )

with col_filt:
    if modo_s3 == "Equipo":
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Equipo</span>', unsafe_allow_html=True)
        todos_eq = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw["Equipo"].dropna().unique()]
        filt_s3  = st.selectbox("Equipo", todos_eq, key="s3_equipo", label_visibility="collapsed")
    elif modo_s3 == "Puesto":
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Puesto</span>', unsafe_allow_html=True)
        puestos_s3 = [p for p in sum(GRUPOS_PUESTO.values(), []) if st.session_state.get(f"s3_pue_{p}", False)]
        btn_p_s3   = "Todos ▾" if not puestos_s3 else (f"{puestos_s3[0]} ▾" if len(puestos_s3)==1 else f"{len(puestos_s3)} selec. ▾")
        with st.popover(btn_p_s3, use_container_width=True):
            st.button("✓ Todos", key="s3_pue_todos", use_container_width=True, on_click=borrar_keys, args=("s3_pue_",))
            for grupo, puestos in GRUPOS_PUESTO.items():
                puestos_v = [p for p in puestos if p in df_raw["Position Name"].unique()]
                if not puestos_v: continue
                todos_g = all(st.session_state.get(f"s3_pue_{p}", False) for p in puestos_v)
                g_chk   = st.checkbox(grupo.upper(), value=todos_g, key=f"s3_pue_grupo_{grupo}")
                if g_chk != todos_g:
                    for p in puestos_v: st.session_state[f"s3_pue_{p}"] = g_chk
                    st.rerun()
                for p in puestos_v:
                    _, col_chk = st.columns([0.15, 0.85])
                    with col_chk: st.checkbox(p, key=f"s3_pue_{p}")
        filt_s3 = puestos_s3 if puestos_s3 else list(df_raw["Position Name"].dropna().unique())
    elif modo_s3 == "Jugador":
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Jugador</span>', unsafe_allow_html=True)
        filt_s3 = st.selectbox("Jugador", todos_jugadores, key="s3_jugador", label_visibility="collapsed")
    else:
        filt_s3 = None

with col_modo:
    if modo_s3 in ["Equipo", "Jugador", "Puesto"]:
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Participación</span>', unsafe_allow_html=True)
        modo_eq_s3 = st.radio(
            label="Modo s3", options=["Sesión completa", "Solo 1 equipo"],
            index=0, key="s3_modo_eq", horizontal=False, label_visibility="collapsed",
        )
    else:
        modo_eq_s3 = "Sesión completa"

with col_eq_s3:
    if modo_s3 == "Jugador" and modo_eq_s3 == "Solo 1 equipo":
        todos_eq2 = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw[
            (df_raw["Player Name"] == filt_s3) & (df_raw["MD"] == "MD") & (df_raw["Equipo"].notna())
        ]["Equipo"].unique()]
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Equipo</span>', unsafe_allow_html=True)
        eq_jug_s3 = st.selectbox("Equipo jug", todos_eq2, key="s3_eq_jug", label_visibility="collapsed")
    elif modo_s3 == "Puesto" and modo_eq_s3 == "Solo 1 equipo":
        todos_eq2 = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw["Equipo"].dropna().unique()]
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Equipo</span>', unsafe_allow_html=True)
        eq_jug_s3 = st.selectbox("Equipo pue", todos_eq2, key="s3_eq_pue", label_visibility="collapsed")
    elif modo_s3 == "Equipo" and modo_eq_s3 == "Solo 1 equipo":
        eq_jug_s3 = filt_s3
    else:
        eq_jug_s3 = filt_s3 if modo_s3 == "Equipo" else None

# ── Selector de semana ────────────────────────────────────────────────────────
with col_sem:
    df_raw2 = df_raw.copy()
    df_raw2["SemanaInicio"] = df_raw2["Fecha"] - pd.to_timedelta(df_raw2["Fecha"].dt.weekday, unit="D")
    semanas_s3  = sorted(df_raw2["SemanaInicio"].unique(), reverse=True)
    todas_cal_s3= pd.date_range(semanas_s3[-1], semanas_s3[0], freq="7D")
    num_sem_s3  = {pd.Timestamp(s): i for i, s in enumerate(todas_cal_s3, start=1)}

    etqs_s3 = []
    for sem in semanas_s3:
        sem = pd.Timestamp(sem)
        n   = num_sem_s3.get(sem, 0)
        fin = sem + pd.Timedelta(days=6)
        g   = df_raw2[df_raw2["SemanaInicio"] == sem]
        md_rows = g[g["MD"] == "MD"]
        rival = ""
        if len(md_rows):
            rv = md_rows["Rival"].dropna()
            if len(rv): rival = f" · {str(rv.iloc[0]).replace('Hindú','Hindu')}"
        etqs_s3.append(f"S{n} {sem.day:02d}/{sem.month:02d} - {fin.day:02d}/{fin.month:02d}{rival}")

    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Semana</span>', unsafe_allow_html=True)
    sem_idx_s3 = st.selectbox("Semana", range(len(semanas_s3)),
                               format_func=lambda i: etqs_s3[i],
                               key="s3_semana", label_visibility="collapsed")
    sem_sel_s3 = pd.Timestamp(semanas_s3[sem_idx_s3])
    sem_fin_s3 = sem_sel_s3 + pd.Timedelta(days=6)

# ── Filtrar datos de la semana ────────────────────────────────────────────────
df_raw2["SemanaInicio"] = df_raw2["Fecha"] - pd.to_timedelta(df_raw2["Fecha"].dt.weekday, unit="D")
df_sem_s3 = df_raw2[df_raw2["SemanaInicio"] == sem_sel_s3].copy()

if modo_s3 == "Equipo":
    md_equipo_s3 = df_raw[
        (df_raw["MD"] == "MD") & (df_raw["Equipo"] == filt_s3)
    ][["Player Name", "Fecha"]].copy()
    md_equipo_s3["Fecha"] = pd.to_datetime(md_equipo_s3["Fecha"])
    df_sem_s3["Fecha_dt"] = pd.to_datetime(df_sem_s3["Fecha"])
    filas_validas = []
    for _, row in md_equipo_s3.iterrows():
        mask = (
            (df_sem_s3["Player Name"] == row["Player Name"]) &
            (df_sem_s3["Fecha_dt"] >= row["Fecha"] - pd.Timedelta(days=6)) &
            (df_sem_s3["Fecha_dt"] <= row["Fecha"] + pd.Timedelta(days=6))
        )
        filas_validas.append(df_sem_s3[mask])
    df_sem_s3 = pd.concat(filas_validas).drop_duplicates() if filas_validas else df_sem_s3.iloc[0:0]
    df_sem_s3 = df_sem_s3.drop(columns=["Fecha_dt"])
    if modo_eq_s3 == "Solo 1 equipo":
        df_no_md  = df_sem_s3[df_sem_s3["MD"] != "MD"]
        df_md     = df_sem_s3[(df_sem_s3["MD"] == "MD") & (df_sem_s3["Equipo"] == filt_s3)]
        df_sem_s3 = pd.concat([df_no_md, df_md]).sort_values("Fecha")
elif modo_s3 == "Puesto":
    df_sem_s3 = df_sem_s3[df_sem_s3["Position Name"].isin(filt_s3)]
    if modo_eq_s3 == "Solo 1 equipo" and eq_jug_s3:
        df_no_md  = df_sem_s3[df_sem_s3["MD"] != "MD"]
        df_md     = df_sem_s3[(df_sem_s3["MD"] == "MD") & (df_sem_s3["Equipo"] == eq_jug_s3)]
        df_sem_s3 = pd.concat([df_no_md, df_md]).sort_values("Fecha")
elif modo_s3 == "Jugador":
    df_sem_s3 = df_sem_s3[df_sem_s3["Player Name"] == filt_s3]
    if modo_eq_s3 == "Solo 1 equipo" and eq_jug_s3:
        df_no_md  = df_sem_s3[df_sem_s3["MD"] != "MD"]
        df_md     = df_sem_s3[
            (df_sem_s3["MD"] == "MD") &
            (df_sem_s3["Equipo"] == eq_jug_s3) &
            (df_sem_s3["Player Name"] == filt_s3)
        ]
        df_sem_s3 = pd.concat([df_no_md, df_md]).sort_values("Fecha")

if df_sem_s3.empty:
    st.warning("No hay datos para la selección.")
else:
    # Filtro minutos
    mins = df_sem_s3.groupby(["Player Name", "Fecha"])["Minutos"].sum().reset_index()
    mins.columns = ["Player Name", "Fecha", "Minutos_dia"]
    df_sem_s3 = df_sem_s3.merge(mins, on=["Player Name", "Fecha"])
    df_sem_s3 = df_sem_s3[df_sem_s3["Minutos_dia"] > 30]

    if modo_s3 in ["Equipo", "Puesto"]:
        df_sem_s3["Fecha"] = pd.to_datetime(df_sem_s3["Fecha"])
        mins2 = df_sem_s3.groupby(["Player Name", "Fecha"])["Minutos"].sum()
        jugs_ok = mins2[mins2 > 30].reset_index()[["Player Name", "Fecha"]]
        df_sem_s3 = df_sem_s3.merge(jugs_ok, on=["Player Name", "Fecha"], how="inner")

    # Agregar por fecha usando LOS 4 EJES
    cols_base_s3 = sorted({c for cols in EJES.values() for c in cols})
    df_por_jug  = df_sem_s3.groupby(["Player Name", "Fecha", "MD"])[cols_base_s3].sum().reset_index()
    for eje, cols in EJES.items():
        df_por_jug[eje] = df_por_jug[cols].sum(axis=1)
    df_dias = df_por_jug.groupby(["Fecha", "MD"])[COLS_EJES].mean().reset_index()
    df_dias = df_dias.sort_values("Fecha")

    DIAS_ES3 = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    df_dias["EtqX"] = df_dias["Fecha"].apply(
        lambda f: f"{DIAS_ES3[f.weekday()]} {f.day:02d}/{f.month:02d}"
    )

    # EWMA ratio para la semana (fecha más reciente del bloque)
    fecha_ref_s3 = df_dias["Fecha"].max()
    if modo_s3 == "Jugador":
        df_ewma_s3_eje = df_ewma_ejes[
            (df_ewma_ejes["Player Name"] == filt_s3) &
            (df_ewma_ejes["Fecha"] == fecha_ref_s3)
        ].set_index("Eje")["Ratio"]
    else:
        if modo_s3 == "Equipo":
            jugs_s3 = df_sem_s3["Player Name"].unique()
        elif modo_s3 == "Puesto":
            jugs_s3 = df_sem_s3["Player Name"].unique()
        else:
            jugs_s3 = df_ewma_ejes["Player Name"].unique()
        df_ewma_s3_eje = df_ewma_ejes[
            (df_ewma_ejes["Player Name"].isin(jugs_s3)) &
            (df_ewma_ejes["Fecha"] == fecha_ref_s3)
        ].groupby("Eje")["Ratio"].mean()

    # Perfil competitivo (ejes): usamos el perfil calculado sobre las 10 métricas,
    # pero sumamos las métricas base de cada eje para obtener el perfil del eje.
    if modo_s3 == "Jugador":
        pf_row = df_perfil[df_perfil["Player Name"] == filt_s3]
        perfil_ejes = {}
        for eje, cols in EJES.items():
            perfil_ejes[eje] = pf_row[[c for c in cols if c in pf_row.columns]].sum(axis=1).iloc[0] if not pf_row.empty else np.nan
    elif modo_s3 == "Puesto":
        pf_rows = df_perfil[df_perfil["Position Name"].isin(filt_s3 if isinstance(filt_s3, list) else [filt_s3])]
        perfil_ejes = {eje: pf_rows[[c for c in cols if c in pf_rows.columns]].sum(axis=1).mean() for eje, cols in EJES.items()} if not pf_rows.empty else {e: np.nan for e in COLS_EJES}
    elif modo_s3 == "Equipo":
        jugs_eq = df_raw[(df_raw["MD"] == "MD") & (df_raw["Equipo"] == filt_s3)]["Player Name"].unique()
        pf_rows = df_perfil[df_perfil["Player Name"].isin(jugs_eq)]
        perfil_ejes = {eje: pf_rows[[c for c in cols if c in pf_rows.columns]].sum(axis=1).mean() for eje, cols in EJES.items()} if not pf_rows.empty else {e: np.nan for e in COLS_EJES}
    else:
        perfil_ejes = {eje: df_perfil[[c for c in cols if c in df_perfil.columns]].sum(axis=1).mean() for eje, cols in EJES.items()}

    def color_obj(ratio, obj):
        if ratio is None: return "#4a6a80"
        if abs(ratio - obj) <= 0.25: return "#00CC44"
        if abs(ratio - obj) <= 0.50: return "#FFD000"
        return "#FF0000"

    OBJETIVOS_OPCIONES = ["x1", "x1.5", "x2", "x2.5"]
    OBJETIVOS_VALORES  = {"x1": 1.0, "x1.5": 1.5, "x2": 2.0, "x2.5": 2.5}

    # ── Render: una fila por EJE (4 filas) ───────────────────────────────────
    for eje in COLS_EJES:
        etq_eje, color_eje = EJES_LABELS[eje]
        vals_dias  = df_dias[eje].tolist() if eje in df_dias.columns else []
        etqs_x     = df_dias["EtqX"].tolist()
        mds        = df_dias["MD"].tolist()
        ratio_ewma = df_ewma_s3_eje.get(eje, np.nan) if hasattr(df_ewma_s3_eje, 'get') else (df_ewma_s3_eje[eje] if eje in df_ewma_s3_eje.index else np.nan)
        color_gauge= color_ratio(ratio_ewma)

        perfil_val    = perfil_ejes.get(eje)
        total_sin_md  = sum(v for v, md in zip(vals_dias, mds) if md != "MD")
        ratio_perfil  = total_sin_md / perfil_val if perfil_val and not np.isnan(perfil_val) and perfil_val > 0 else None

        c_barras, c_gauge, c_obj, c_total = st.columns([0.55, 0.20, 0.04, 0.21])

        with c_barras:
            bar_colors = ["#00A8CC" if md == "MD" else color_eje for md in mds]
            fig_b = go.Figure(go.Bar(
                x=list(range(len(vals_dias))), y=vals_dias,
                marker_color=bar_colors, marker_line_width=0,
                text=[f"{v:.0f}" for v in vals_dias],
                textposition="outside", textfont=dict(size=9, color="white"),
                cliponaxis=False,
            ))
            fig_b.update_layout(
                title=dict(text=etq_eje, font=dict(size=11, color="white"), x=0),
                paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
                height=160, margin=dict(t=28, b=30, l=10, r=10),
                xaxis=dict(tickmode="array", tickvals=list(range(len(etqs_x))),
                        ticktext=etqs_x, tickfont=dict(color="#7a9ab5", size=8),
                        tickangle=-30, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1e3048",
                        tickfont=dict(color="#7a9ab5", size=8), zeroline=False),
                showlegend=False, bargap=0.2,
                separators=",.",
            )
            st.plotly_chart(fig_b, use_container_width=True, key=f"s3_bar_{eje}")

        with c_gauge:
            if not np.isnan(ratio_ewma):
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(ratio_ewma, 2),
                    number=dict(font=dict(color=color_gauge, size=20)),
                    gauge=dict(
                        axis=dict(range=[0, 2], tickfont=dict(size=8, color="#7a9ab5")),
                        bar=dict(color=color_gauge, thickness=0.3),
                        bgcolor="#1e3048",
                        steps=[
                            dict(range=[0,    0.60], color="rgba(138,43,226,0.15)"),
                            dict(range=[0.60, 0.80], color="rgba(255,140,0,0.15)"),
                            dict(range=[0.80, 1.30], color="rgba(0,204,68,0.15)"),
                            dict(range=[1.30, 1.50], color="rgba(255,208,0,0.15)"),
                            dict(range=[1.50, 2],    color="rgba(255,0,0,0.15)"),
                        ],
                        threshold=dict(line=dict(color=color_gauge, width=2), thickness=0.75, value=ratio_ewma),
                    ),
                ))
                fig_g.update_layout(
                    paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
                    height=160, margin=dict(t=20, b=10, l=20, r=20),
                    font=dict(color="white"),
                    separators=",.",
                )
                st.plotly_chart(fig_g, use_container_width=True, key=f"s3_gauge_{eje}")
            else:
                st.markdown('<div style="height:160px; display:flex; align-items:center; justify-content:center; color:#4a6a80;">Sin datos EWMA</div>', unsafe_allow_html=True)

        with c_obj:
            obj_val = st.radio(
                label=etq_eje,
                options=OBJETIVOS_OPCIONES,
                index=2,
                key=f"s3_obj_{eje}",
                horizontal=False,
                label_visibility="collapsed",
            )

        with c_total:
            color_rp  = color_obj(ratio_perfil, OBJETIVOS_VALORES[obj_val])
            ratio_str = f"{ratio_perfil:.2f}".replace(".", ",") if ratio_perfil else "—"
            perfil_str= f"{perfil_val:,.0f}" if (perfil_val and not np.isnan(perfil_val)) else "—"
            st.markdown(
                f'<div style="background:#0f1a28; border:1px solid #1e3048; border-radius:8px; padding:6px; '
                f'text-align:center; height:160px; display:flex; flex-direction:column; justify-content:center;">'
                f'<div style="font-size:10px; color:#7a9ab5; text-transform:uppercase;">Sin partido</div>'
                f'<div style="font-size:22px; font-weight:900; color:white;">{total_sin_md:,.0f}</div>'
                f'<div style="font-size:10px; color:#7a9ab5; text-transform:uppercase;">Perfil</div>'
                f'<div style="font-size:14px; font-weight:700; color:#7a9ab5;">{perfil_str}</div>'
                f'<div style="font-size:22px; font-weight:900; color:{color_rp};">{ratio_str}</div>'
                f'</div>',
                unsafe_allow_html=True
            )