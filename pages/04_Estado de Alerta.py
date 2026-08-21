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
</style>
""", unsafe_allow_html=True)

# ── Métricas ──────────────────────────────────────────────────────────────────
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

METRICAS = {
    "Distancia Total":                          ("Dist Tot",     "#7FB3E0"),
    "AI 18 Km/h":                               ("HSR",          "#F2A8C0"),
    "DT + 25 Km/h":                             ("Sprint",       "#C4A8E0"),
    "+25 Km/h #":                               ("N° Sprints",   "#F5C09A"),
    COL_DIST_80:                                ("Dist >80%",    "#FFB347"),
    COL_EFF_80:                                 ("# >80%",       "#FF8C69"),
    "Acel 2,5 m/ss #":                          ("N° Acel",      "#A8DDB5"),
    "Desacel -2,5 m/ss #":                      ("N° Decel",     "#F0DC96"),
    "Contact Involvement Total Count Avg":      ("Contactos",    "#A8E0DC"),
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

RANGOS_PERFIL = {
    "Distancia Total":                          (2.0, 2.5),
    "AI 18 Km/h":                               (2.0, 2.5),
    "DT + 25 Km/h":                             (1.7, 2.2),
    "+25 Km/h #":                               (1.7, 2.2),
    COL_DIST_80:                                (1.7, 2.2),
    COL_EFF_80:                                 (1.7, 2.2),
    "Acel 2,5 m/ss #":                          (2.0, 2.5),
    "Desacel -2,5 m/ss #":                      (2.0, 2.5),
    "Contact Involvement Total Count Avg":      (1.5, 2.0),
    "Total Player Load":                        (2.0, 2.5),
}

def color_ratio_perfil(ratio, col):
    if ratio is None or np.isnan(ratio): return "#4a6a80"
    rango = RANGOS_PERFIL.get(col, (1.0, 1.0))
    lo, hi = rango
    if lo <= ratio <= hi:             return "#00CC44"
    if lo - 0.25 <= ratio <= hi + 0.25: return "#FFD000"
    return "#FF0000"

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def color_ratio(r):
    if r is None or np.isnan(r): return "#4a6a80"
    if 0.85 <= r <= 1.15: return "#00CC44"
    if 0.75 <= r <= 1.25: return "#FFD000"
    return "#FF0000"

def score_ratio(r):
    if r is None or np.isnan(r): return 1
    if 0.85 <= r <= 1.15: return 1
    if 0.75 <= r <= 1.25: return 2
    return 3

def color_score(s):
    if s <= 15: return "#00CC44"
    if s <= 21: return "#FFD000"
    return "#FF0000"

def label_score(s):
    if s <= 15: return "✅ Óptimo"
    if s <= 21: return "⚠️ Precaución"
    return "🚨 Alerta"

# ── Carga de datos ────────────────────────────────────────────────────────────
def cargar_datos():
    if "df_excel" not in st.session_state:
        st.session_state["df_excel"] = pd.read_excel("TOTALES GPS.xlsx")
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

# ── Calcular EWMA por jugador ─────────────────────────────────────────────────
@st.cache_data
def calcular_ewma(df):
    """
    Para cada jugador y métrica calcula EWMA aguda (7 días) y crónica (28 días).
    Devuelve un df con una fila por jugador+fecha con los ratios EWMA.
    """
    # Sumar por jugador+fecha
    agg = df.groupby(["Player Name", "Position Name", "Fecha"])[COLS].sum().reset_index()

    resultados = []
    for jugador, g in agg.groupby("Player Name"):
        g = g.sort_values("Fecha").copy()
        # Crear serie diaria completa (rellenando días sin sesión con 0)
        fecha_min = g["Fecha"].min()
        fecha_max = g["Fecha"].max()
        idx = pd.date_range(fecha_min, fecha_max, freq="D")
        g_diario = g.set_index("Fecha").reindex(idx)
        
        pos = g["Position Name"].iloc[-1]

        for col in COLS:
            serie = g_diario[col].astype(float)
            # EWMA: lambda = 2/(N+1)
            ewma_aguda   = serie.ewm(span=7,  adjust=False).mean()
            ewma_cronica = serie.ewm(span=28, adjust=False).mean()

            for fecha in g["Fecha"]:
                if fecha not in ewma_aguda.index:
                    continue
                ag = ewma_aguda[fecha]
                cr = ewma_cronica[fecha]
                ratio = ag / cr if cr > 0 else np.nan
                resultados.append({
                    "Player Name":    jugador,
                    "Position Name":  pos,
                    "Fecha":          fecha,
                    "Metrica":        col,
                    "EWMA_Aguda":     ag,
                    "EWMA_Cronica":   cr,
                    "Ratio":          ratio,
                })

    return pd.DataFrame(resultados)

df_ewma = calcular_ewma(df_raw)

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
    f'<div class="topbar-divider"></div><span class="topbar-page">Estado de Alerta</span></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="padding-top:6px; padding-bottom:4px;">'
    '<span style="font-size:22px; font-weight:900; color:white;">Estado de Alerta</span>'
    '<span style="font-size:22px; font-weight:900; color:#00A8CC;"> · CASI</span></div>',
    unsafe_allow_html=True
)

# ── Filtros ───────────────────────────────────────────────────────────────────
todos_jugadores_raw = sorted(df_raw[df_raw["MD"] != "MD"]["Player Name"].dropna().unique().tolist())
todos_puestos   = sorted(df_raw["Position Name"].dropna().unique().tolist())
todas_fechas    = sorted(df_ewma["Fecha"].unique(), reverse=True)

DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

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

jug_sel = get_sel("ew_jug_", todos_jugadores_raw)
pue_sel = get_sel("ew_pue_", todos_puestos)

jug_activo = jug_sel if jug_sel else todos_jugadores_raw
pue_activo = pue_sel if pue_sel else todos_puestos

# Selector de fecha primero
opciones_fecha = []
for f in todas_fechas:
    dia = DIAS_ES[f.weekday()]
    fila_md = df_raw[(df_raw["Fecha"] == f) & (df_raw["MD"] == "MD") & (df_raw["Rival"].notna())]
    rival_str = f" · {fila_md['Rival'].iloc[0]}" if not fila_md.empty else ""
    opciones_fecha.append(f"{dia} {f.day:02d}/{f.month:02d}{rival_str}")

fecha_idx_tmp = st.session_state.get("ew_fecha", 0)
fecha_sel_tmp = todas_fechas[fecha_idx_tmp] if fecha_idx_tmp < len(todas_fechas) else todas_fechas[0]
fecha_desde_tmp = fecha_sel_tmp - pd.Timedelta(days=28)

todos_jugadores_raw = sorted(df_raw[
    (df_raw["MD"] != "MD") &
    (df_raw["Fecha"] >= fecha_desde_tmp) &
    (df_raw["Fecha"] <= fecha_sel_tmp)
]["Player Name"].dropna().unique().tolist())

f1, f2, f3 = st.columns(3)
render_filtro(f1, "Jugador", "ew_jug_", todos_jugadores_raw)
render_filtro_puesto(f2, GRUPOS_PUESTO, "ew_pue_", todos_puestos)

with f3:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Fecha de referencia</span>', unsafe_allow_html=True)
    fecha_idx = st.selectbox(
        label="Fecha", options=range(len(todas_fechas)),
        format_func=lambda i: opciones_fecha[i],
        key="ew_fecha", label_visibility="collapsed",
    )
    fecha_sel = todas_fechas[fecha_idx]
    fecha_desde = fecha_sel - pd.Timedelta(days=28)
    todos_jugadores = sorted(df_raw[
        (df_raw["Fecha"] >= fecha_desde) &
        (df_raw["Fecha"] <= fecha_sel) &
        (df_raw["MD"] != "MD")
    ]["Player Name"].dropna().unique().tolist())
st.markdown("<hr style='border-color:#1e3048; margin:8px 0 16px 0;'>", unsafe_allow_html=True)

# ── Calcular scores para la fecha seleccionada ────────────────────────────────
# Solo jugadores con al menos una sesión no-MD en los últimos 28 días
fecha_desde = fecha_sel - pd.Timedelta(days=28)
jugs_activos_28 = df_raw[
    (df_raw["Fecha"] >= fecha_desde) &
    (df_raw["Fecha"] <= fecha_sel) &
    (df_raw["MD"] != "MD")
]["Player Name"].unique()

df_fecha = df_ewma[
    (df_ewma["Fecha"] == fecha_sel) &
    (df_ewma["Player Name"].isin(jug_activo)) &
    (df_ewma["Player Name"].isin(jugs_activos_28)) &
    (df_ewma["Position Name"].isin(pue_activo))
].copy()

if df_fecha.empty:
    st.warning("No hay datos EWMA para la fecha seleccionada.")
    st.stop()

# Pivot: jugador × métrica → ratio
pivot = df_fecha.pivot_table(index=["Player Name", "Position Name"], columns="Metrica", values="Ratio").reset_index()

# Score por jugador
# Identificar métricas con historial cero por jugador
hist_por_jugador = df_raw.groupby("Player Name")[COLS].sum()

for col in COLS:
    if col in pivot.columns:
        pivot[f"score_{col}"] = pivot[col].apply(score_ratio)
    else:
        pivot[f"score_{col}"] = 1

def calcular_score_ajustado(row):
    jugador = row["Player Name"]
    scores = []
    for col in COLS:
        # Si el jugador tiene 0 histórico en esa métrica, ignorarla
        hist = hist_por_jugador.loc[jugador, col] if jugador in hist_por_jugador.index else 0
        if hist == 0:
            continue
        scores.append(row[f"score_{col}"])
    if not scores:
        return 10, 10, "#00CC44", "✅ Óptimo"
    n = len(scores)
    total = sum(scores)
    # Escalar umbrales proporcionalmente a n métricas
    umbral_verde  = round(n * 15 / 10)
    umbral_am     = round(n * 21 / 10)
    color = color_score_n(total, umbral_verde, umbral_am)
    label = label_score_n(total, umbral_verde, umbral_am)
    return total, n, color, label

def color_score_n(s, u1, u2):
    if s <= u1: return "#00CC44"
    if s <= u2: return "#FFD000"
    return "#FF0000"

def label_score_n(s, u1, u2):
    if s <= u1: return "✅ Óptimo"
    if s <= u2: return "⚠️ Precaución"
    return "🚨 Alerta"

pivot[["Score_Total", "N_Metricas", "Color_Score", "Label_Score"]] = pivot.apply(
    lambda row: pd.Series(calcular_score_ajustado(row)), axis=1
)
# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — ESTADO GENERAL (solo jugadores en alerta o precaución)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">🚨 Estado general del equipo</div>', unsafe_allow_html=True)

# Contadores
n_alerta    = len(pivot[pivot["Color_Score"] == "#FF0000"])
n_precaucion= len(pivot[pivot["Color_Score"] == "#FFD000"])
n_optimo    = len(pivot[pivot["Color_Score"] == "#00CC44"])
total_jug   = len(pivot)

# Filtro activo por click
if "ew_filtro_estado" not in st.session_state:
    st.session_state["ew_filtro_estado"] = None

def toggle_filtro(estado):
    if st.session_state["ew_filtro_estado"] == estado:
        st.session_state["ew_filtro_estado"] = None
    else:
        st.session_state["ew_filtro_estado"] = estado

st.markdown(
    f'<div style="display:flex; gap:8px; margin-bottom:8px;">'
    f'<div style="background:#0f1a28; border:{"4px" if st.session_state["ew_filtro_estado"]=="#FF0000" else "2px"} solid #FF0000; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:#FF0000;">{n_alerta}</div></div>'
    f'<div style="background:#0f1a28; border:{"4px" if st.session_state["ew_filtro_estado"]=="#FFD000" else "2px"} solid #FFD000; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:#FFD000;">{n_precaucion}</div></div>'
    f'<div style="background:#0f1a28; border:{"4px" if st.session_state["ew_filtro_estado"]=="#00CC44" else "2px"} solid #00CC44; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:#00CC44;">{n_optimo}</div></div>'
    f'<div style="background:#0f1a28; border:1px solid #1e3048; border-radius:10px; padding:12px 24px; text-align:center; width:160px;">'
    f'<div style="font-size:28px; font-weight:900; color:white;">{total_jug}</div></div>'
    f'</div>',
    unsafe_allow_html=True
)

col_alerta, col_precaucion, col_optimo, _ = st.columns([0.145, 0.145, 0.145, 0.565])
with col_alerta:
    st.button("🚨 Alerta", key="btn_alerta", on_click=toggle_filtro, args=("#FF0000",), use_container_width=True)
with col_precaucion:
    st.button("⚠️ Precaución", key="btn_precaucion", on_click=toggle_filtro, args=("#FFD000",), use_container_width=True)
with col_optimo:
    st.button("✅ Óptimo", key="btn_optimo", on_click=toggle_filtro, args=("#00CC44",), use_container_width=True)

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# Grid filtrado
filtro_activo = st.session_state["ew_filtro_estado"]
if filtro_activo:
    df_grid = pivot[pivot["Color_Score"] == filtro_activo].sort_values("Player Name")
else:
    df_grid = pivot[pivot["Color_Score"] != "#00CC44"].sort_values("Score_Total", ascending=False)

if df_grid.empty:
    st.markdown('<div style="color:#00CC44; font-size:14px; font-weight:700;">✅ Todos los jugadores en estado óptimo</div>', unsafe_allow_html=True)
else:
    grid_html = '<div style="display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px;">'
    for _, row in df_grid.iterrows():
        color  = row["Color_Score"]
        label  = row["Label_Score"]
        nombre = row["Player Name"]
        puesto = row["Position Name"]
        grid_html += (
            f'<div style="background:#0f1a28; border:2px solid {color}; border-radius:10px;'
            f' padding:10px 12px; width:140px; flex:0 0 140px; height:100px; display:flex; flex-direction:column; justify-content:space-between;">'
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

# Selector de jugador — se puede precargar desde click en sección 1
jug_default = st.session_state.get("ew_jug_sel_detalle", todos_jugadores[0])
if jug_default not in todos_jugadores:
    jug_default = todos_jugadores[0]

col_sel, col_met, _ = st.columns([0.25, 0.25, 0.50])

with col_sel:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Jugador</span>', unsafe_allow_html=True)
    jug_detalle = st.selectbox(
        label="Jugador detalle",
        options=todos_jugadores,
        index=todos_jugadores.index(jug_default) if jug_default in todos_jugadores else 0,
        key="ew_jug_detalle",
        label_visibility="collapsed",
    )

with col_met:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Métrica</span>', unsafe_allow_html=True)
    met_detalle = st.selectbox(
        label="Métrica detalle",
        options=COLS,
        format_func=lambda c: METRICAS[c][0],
        key="ew_met_detalle",
        label_visibility="collapsed",
    )

# Datos del jugador seleccionado
df_jug = df_ewma[df_ewma["Player Name"] == jug_detalle].copy()
df_jug_met = df_jug[df_jug["Metrica"] == met_detalle].sort_values("Fecha")

if df_jug_met.empty:
    st.warning("No hay datos para este jugador y métrica.")
else:
    # Score actual del jugador
    row_actual = pivot[pivot["Player Name"] == jug_detalle]
    score_actual = int(row_actual["Score_Total"].iloc[0]) if not row_actual.empty else None
    color_actual = color_score(score_actual) if score_actual else "#4a6a80"
    label_actual = label_score(score_actual) if score_actual else "—"

    # Header del jugador
    metricas_html = ""
    for col in COLS:
        etq, _ = METRICAS[col]
        row_m = pivot[pivot["Player Name"] == jug_detalle]
        ratio_m = row_m[col].iloc[0] if not row_m.empty and col in row_m.columns else np.nan
        color_m = color_ratio(ratio_m)
        val_str = "—" if np.isnan(ratio_m) else f"{ratio_m:.2f}"
        metricas_html += (
            f'<div style="flex:1; text-align:center; padding:4px;">'
            f'<div style="font-size:10px; color:#7a9ab5; text-transform:uppercase; margin-bottom:4px;">{etq}</div>'
            f'<div style="font-size:22px; font-weight:900; color:{color_m};">{val_str}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div style="background:#0f1a28; border:2px solid {color_actual}; border-radius:10px; '
        f'padding:16px 20px; margin-bottom:16px;">'
        f'<div style="text-align:center; margin-bottom:12px;">'
        f'<span style="font-size:26px; font-weight:900; color:white;">{jug_detalle}</span>'
        f'&nbsp;&nbsp;'
        f'<span style="font-size:22px; font-weight:900; color:{color_actual};">{label_actual}</span>'
        f'</div>'
        f'<div style="display:flex; gap:4px;">{metricas_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Gráfico EWMA + barras
    col_graf, col_barras = st.columns([0.6, 0.4])

    with col_graf:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_jug_met["Fecha"], y=df_jug_met["Ratio"],
            mode="lines+markers", name="Ratio EWMA",
            line=dict(color="#00A8CC", width=2),
            marker=dict(size=6, color="#00A8CC"),
        ))
        fig.add_hline(y=0.85, line_dash="dash", line_color="#00CC44", line_width=1,
                      annotation_text="0.85", annotation_font_color="#00CC44", annotation_font_size=9)
        fig.add_hline(y=1.15, line_dash="dash", line_color="#00CC44", line_width=1,
                      annotation_text="1.15", annotation_font_color="#00CC44", annotation_font_size=9)
        fig.add_hline(y=0.75, line_dash="dot", line_color="#FFD000", line_width=1,
                      annotation_text="0.75", annotation_font_color="#FFD000", annotation_font_size=9)
        fig.add_hline(y=1.25, line_dash="dot", line_color="#FFD000", line_width=1,
                      annotation_text="1.25", annotation_font_color="#FFD000", annotation_font_size=9)
        fig.update_layout(
            title=dict(text=f"EWMA Ratio — {METRICAS[met_detalle][0]}", font=dict(size=12, color="white"), x=0),
            paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
            height=300, margin=dict(t=35, b=20, l=10, r=80),
            xaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=9)),
            yaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=9), zeroline=False),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_barras:
        # Barras de carga aguda por sesión (últimas 8 sesiones)
        df_jug_raw = df_raw[df_raw["Player Name"] == jug_detalle].sort_values("Fecha")
        df_jug_agg = df_jug_raw.groupby("Fecha")[met_detalle].sum().reset_index()
        df_jug_agg = df_jug_agg[df_jug_agg["Fecha"] >= (fecha_sel - pd.Timedelta(days=28))]
        df_jug_agg = df_jug_agg[df_jug_agg["Fecha"] <= fecha_sel]
        bar_colors = ["#00A8CC" if (df_raw[(df_raw["Player Name"] == jug_detalle) & (df_raw["Fecha"] == f)]["MD"] == "MD").any() else "#c9d4de" for f in df_jug_agg["Fecha"]]
        DIAS_ES2 = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        etqs = [f"{DIAS_ES2[f.weekday()]} {f.day:02d}/{f.month:02d}" for f in df_jug_agg["Fecha"]]

        fig_b = go.Figure(go.Bar(
            x=list(range(len(df_jug_agg))),
            y=df_jug_agg[met_detalle].tolist(),
            marker_color=bar_colors, marker_line_width=0,
            text=[f"{v:.0f}" for v in df_jug_agg[met_detalle]],
            textposition="outside", textfont=dict(size=9, color="white"),
            cliponaxis=False,
        ))
        fig_b.update_layout(
            title=dict(text="Últimas sesiones", font=dict(size=12, color="white"), x=0),
            paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
            height=300, margin=dict(t=35, b=40, l=10, r=10),
            xaxis=dict(tickmode="array", tickvals=list(range(len(etqs))), ticktext=etqs,
                       tickfont=dict(color="#7a9ab5", size=8), tickangle=-45, showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=8), zeroline=False),
            showlegend=False, bargap=0.25,
        )
        st.plotly_chart(fig_b, use_container_width=True)

    # Tabla de sesiones recientes
    st.markdown('<div class="seccion-header">📋 Sesiones recientes</div>', unsafe_allow_html=True)

    df_tabla_jug = df_raw[df_raw["Player Name"] == jug_detalle].copy()
    df_tabla_jug = df_tabla_jug.sort_values("Fecha", ascending=False)

    cols_tabla = ["Fecha", "MD", "Rival", "Equipo"] + [c for c in COLS if c in df_tabla_jug.columns]
    df_tabla_jug = df_tabla_jug[cols_tabla].head(20)

    rename = {"Fecha": "Fecha", "MD": "MD", "Rival": "Rival", "Equipo": "Equipo"}
    for c in COLS:
        if c in df_tabla_jug.columns:
            rename[c] = METRICAS[c][0]
    df_tabla_jug = df_tabla_jug.rename(columns=rename)
    df_tabla_jug["Fecha"] = df_tabla_jug["Fecha"].dt.date

    st.dataframe(df_tabla_jug, use_container_width=True, hide_index=True, height=350)

    st.markdown("<hr style='border-color:#1e3048; margin:20px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — CARGA SEMANAL CON EWMA
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def calcular_perfil_competitivo(df):
    """
    Para cada jugador, calcula el perfil competitivo por métrica:
    - Tomar todos los MD
    - Sumar métricas por jugador+fecha
    - Filtrar donde suma minutos entre 30 y 100
    - Perfil = (max + promedio) / 2
    """
    md_df = df[df["MD"] == "MD"].copy()
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
            vals = g[col].dropna()
            if len(vals) == 0:
                row[col] = np.nan
            else:
                row[col] = (vals.max() + vals.mean()) / 2
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
        filt_s3 = st.selectbox("Equipo", todos_eq, key="s3_equipo", label_visibility="collapsed")
    elif modo_s3 == "Puesto":
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Puesto</span>', unsafe_allow_html=True)
        puestos_s3 = [p for p in sum(GRUPOS_PUESTO.values(), []) if st.session_state.get(f"s3_pue_{p}", False)]
        btn_p_s3 = "Todos ▾" if not puestos_s3 else (f"{puestos_s3[0]} ▾" if len(puestos_s3)==1 else f"{len(puestos_s3)} selec. ▾")
        with st.popover(btn_p_s3, use_container_width=True):
            st.button("✓ Todos", key="s3_pue_todos", use_container_width=True, on_click=borrar_keys, args=("s3_pue_",))
            for grupo, puestos in GRUPOS_PUESTO.items():
                puestos_v = [p for p in puestos if p in df_raw["Position Name"].unique()]
                if not puestos_v: continue
                todos_g = all(st.session_state.get(f"s3_pue_{p}", False) for p in puestos_v)
                g_chk = st.checkbox(grupo.upper(), value=todos_g, key=f"s3_pue_grupo_{grupo}")
                if g_chk != todos_g:
                    for p in puestos_v:
                        st.session_state[f"s3_pue_{p}"] = g_chk
                    st.rerun()
                for p in puestos_v:
                    _, col_chk = st.columns([0.15, 0.85])
                    with col_chk:
                        st.checkbox(p, key=f"s3_pue_{p}")
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
            label="Modo s3",
            options=["Sesión completa", "Solo 1 equipo"],
            index=0, key="s3_modo_eq", horizontal=False, label_visibility="collapsed",
        )
    else:
        modo_eq_s3 = "Sesión completa"

with col_eq_s3:
    if modo_s3 == "Jugador" and modo_eq_s3 == "Solo 1 equipo":
        todos_eq2 = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw[
            (df_raw["Player Name"] == filt_s3) &
            (df_raw["MD"] == "MD") &
            (df_raw["Equipo"].notna())
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
    # Construir catálogo de semanas
    df_raw2 = df_raw.copy()
    df_raw2["SemanaInicio"] = df_raw2["Fecha"] - pd.to_timedelta(df_raw2["Fecha"].dt.weekday, unit="D")
    semanas_s3 = sorted(df_raw2["SemanaInicio"].unique(), reverse=True)
    todas_cal_s3 = pd.date_range(semanas_s3[-1], semanas_s3[0], freq="7D")
    num_sem_s3 = {pd.Timestamp(s): i for i, s in enumerate(todas_cal_s3, start=1)}

    etqs_s3 = []
    for sem in semanas_s3:
        sem = pd.Timestamp(sem)
        n = num_sem_s3.get(sem, 0)
        fin = sem + pd.Timedelta(days=6)
        g = df_raw2[df_raw2["SemanaInicio"] == sem]
        md_rows = g[g["MD"] == "MD"]
        rival = ""
        if len(md_rows):
            rv = md_rows["Rival"].dropna()
            if len(rv):
                rival = f" · {str(rv.iloc[0]).replace('Hindú','Hindu')}"
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
        (df_raw["MD"] == "MD") &
        (df_raw["Equipo"] == filt_s3)
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
    if filas_validas:
        df_sem_s3 = pd.concat(filas_validas).drop_duplicates()
    else:
        df_sem_s3 = df_sem_s3.iloc[0:0]
    df_sem_s3 = df_sem_s3.drop(columns=["Fecha_dt"])
    if modo_eq_s3 == "Solo 1 equipo":
        df_no_md = df_sem_s3[df_sem_s3["MD"] != "MD"]
        df_md    = df_sem_s3[(df_sem_s3["MD"] == "MD") & (df_sem_s3["Equipo"] == filt_s3)]
        df_sem_s3 = pd.concat([df_no_md, df_md]).sort_values("Fecha")
elif modo_s3 == "Puesto":
    df_sem_s3 = df_sem_s3[df_sem_s3["Position Name"].isin(filt_s3)]
    if modo_eq_s3 == "Solo 1 equipo" and eq_jug_s3:
        df_no_md = df_sem_s3[df_sem_s3["MD"] != "MD"]
        df_md    = df_sem_s3[(df_sem_s3["MD"] == "MD") & (df_sem_s3["Equipo"] == eq_jug_s3)]
        df_sem_s3 = pd.concat([df_no_md, df_md]).sort_values("Fecha")
elif modo_s3 == "Jugador":
    df_sem_s3 = df_sem_s3[df_sem_s3["Player Name"] == filt_s3]
    if modo_eq_s3 == "Solo 1 equipo" and eq_jug_s3:
        df_no_md = df_sem_s3[df_sem_s3["MD"] != "MD"]
        df_md    = df_sem_s3[
            (df_sem_s3["MD"] == "MD") &
            (df_sem_s3["Equipo"] == eq_jug_s3) &
            (df_sem_s3["Player Name"] == filt_s3)
        ]
        df_sem_s3 = pd.concat([df_no_md, df_md]).sort_values("Fecha")

if df_sem_s3.empty:
    st.warning("No hay datos para la selección.")
else:
    # Filtro minutos: suma por jugador+fecha según modo
    mins = df_sem_s3.groupby(["Player Name", "Fecha"])["Minutos"].sum().reset_index()
    mins.columns = ["Player Name", "Fecha", "Minutos_dia"]
    df_sem_s3 = df_sem_s3.merge(mins, on=["Player Name", "Fecha"])
    df_sem_s3 = df_sem_s3[df_sem_s3["Minutos_dia"] > 30]

    if modo_s3 in ["Equipo", "Puesto"]:
        df_sem_s3["Fecha"] = pd.to_datetime(df_sem_s3["Fecha"])
        mins = df_sem_s3.groupby(["Player Name", "Fecha"])["Minutos"].sum()
        jugadores_ok = mins[mins > 30].reset_index()[["Player Name", "Fecha"]]
        df_sem_s3 = df_sem_s3.merge(jugadores_ok, on=["Player Name", "Fecha"], how="inner")

    df_por_jug = df_sem_s3.groupby(["Player Name", "Fecha", "MD"])[COLS].sum().reset_index()
    df_dias = df_por_jug.groupby(["Fecha", "MD"])[COLS].mean().reset_index()
    df_dias = df_dias.sort_values("Fecha")
    DIAS_ES3 = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    df_dias["EtqDia"] = df_dias.apply(
        lambda r: f"{'MD' if r['MD']=='MD' else r['MD']}", axis=1
    )
    df_dias["EtqX"] = df_dias["Fecha"].apply(
        lambda f: f"{DIAS_ES3[f.weekday()]} {f.day:02d}/{f.month:02d}"
    )

    # EWMA ratio para la semana seleccionada
    # Para cada métrica, calcular ratio EWMA a la fecha del MD o último día
    fecha_ref_s3 = df_dias["Fecha"].max()

    if modo_s3 == "Jugador":
        df_ewma_s3 = df_ewma[
            (df_ewma["Player Name"] == filt_s3) &
            (df_ewma["Fecha"] == fecha_ref_s3)
        ].set_index("Metrica")["Ratio"]
    else:
        # Promedio de ratios del grupo
        if modo_s3 == "Equipo":
            jugs_s3 = df_sem_s3["Player Name"].unique()
        elif modo_s3 == "Puesto":
            jugs_s3 = df_sem_s3["Player Name"].unique()
        else:
            jugs_s3 = df_ewma["Player Name"].unique()
        df_ewma_s3 = df_ewma[
            (df_ewma["Player Name"].isin(jugs_s3)) &
            (df_ewma["Fecha"] == fecha_ref_s3)
        ].groupby("Metrica")["Ratio"].mean()

    # ── Render: una fila por métrica ──────────────────────────────────────────
    # ── Perfil competitivo según modo ─────────────────────────────────────────

    if modo_s3 == "Jugador":
        perfil_vals = df_perfil[df_perfil["Player Name"] == filt_s3].iloc[0] if filt_s3 in df_perfil["Player Name"].values else None
    elif modo_s3 == "Puesto":
        df_p = df_perfil[df_perfil["Position Name"].isin(filt_s3 if isinstance(filt_s3, list) else [filt_s3])]
        perfil_vals = df_p[COLS].mean() if not df_p.empty else None
    elif modo_s3 == "Equipo":
        jugs_eq = df_raw[(df_raw["MD"] == "MD") & (df_raw["Equipo"] == filt_s3)]["Player Name"].unique()
        df_p = df_perfil[df_perfil["Player Name"].isin(jugs_eq)]
        perfil_vals = df_p[COLS].mean() if not df_p.empty else None
    else:  # Plantel
        perfil_vals = df_perfil[COLS].mean()

    OBJETIVOS_OPCIONES = ["x1", "x1.5", "x2", "x2.5"]
    OBJETIVOS_VALORES  = {"x1": 1.0, "x1.5": 1.5, "x2": 2.0, "x2.5": 2.5}

    for col in COLS:
        etq_met, color_met = METRICAS[col]
        vals_dias = df_dias[col].tolist() if col in df_dias.columns else []
        etqs_x    = df_dias["EtqX"].tolist()
        mds       = df_dias["MD"].tolist()
        ratio_ewma = df_ewma_s3.get(col, np.nan) if hasattr(df_ewma_s3, 'get') else (df_ewma_s3[col] if col in df_ewma_s3.index else np.nan)
        color_gauge = color_ratio(ratio_ewma)

        # Perfil competitivo
        perfil_val = perfil_vals[col] if perfil_vals is not None and col in perfil_vals and not np.isnan(perfil_vals[col]) else None
        total_sin_md = sum(v for v, md in zip(vals_dias, mds) if md != "MD")
        ratio_perfil = total_sin_md / perfil_val if perfil_val and perfil_val > 0 else None

        c_barras, c_gauge, c_obj, c_total = st.columns([0.55, 0.20, 0.04, 0.21])

        
        # Color ratio perfil según objetivo elegido
        def color_obj(ratio, obj):
            if ratio is None: return "#4a6a80"
            if abs(ratio - obj) <= 0.25: return "#00CC44"
            if abs(ratio - obj) <= 0.50: return "#FFD000"
            return "#FF0000"

        with c_barras:
            bar_colors = ["#00A8CC" if md == "MD" else "#c9d4de" for md in mds]
            fig_b = go.Figure(go.Bar(
                x=list(range(len(vals_dias))), y=vals_dias,
                marker_color=bar_colors, marker_line_width=0,
                text=[f"{v:.0f}" for v in vals_dias],
                textposition="outside", textfont=dict(size=9, color="white"),
                cliponaxis=False,
            ))
            fig_b.update_layout(
                title=dict(text=etq_met, font=dict(size=11, color="white"), x=0),
                paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
                height=160, margin=dict(t=28, b=30, l=10, r=10),
                xaxis=dict(tickmode="array", tickvals=list(range(len(etqs_x))),
                           ticktext=etqs_x, tickfont=dict(color="#7a9ab5", size=8),
                           tickangle=-30, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#1e3048",
                           tickfont=dict(color="#7a9ab5", size=8), zeroline=False),
                showlegend=False, bargap=0.2,
            )
            st.plotly_chart(fig_b, use_container_width=True, key=f"s3_bar_{col}")

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
                            dict(range=[0, 0.75],    color="rgba(255,0,0,0.15)"),
                            dict(range=[0.75, 0.85], color="rgba(255,208,0,0.15)"),
                            dict(range=[0.85, 1.15], color="rgba(0,204,68,0.15)"),
                            dict(range=[1.15, 1.25], color="rgba(255,208,0,0.15)"),
                            dict(range=[1.25, 2],    color="rgba(255,0,0,0.15)"),
                        ],
                        threshold=dict(line=dict(color=color_gauge, width=2), thickness=0.75, value=ratio_ewma),
                    ),
                ))
                fig_g.update_layout(
                    paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
                    height=160, margin=dict(t=20, b=10, l=20, r=20),
                    font=dict(color="white"),
                )
                st.plotly_chart(fig_g, use_container_width=True, key=f"s3_gauge_{col}")
            else:
                st.markdown('<div style="height:160px; display:flex; align-items:center; justify-content:center; color:#4a6a80;">Sin datos EWMA</div>', unsafe_allow_html=True)

        with c_obj:
            obj_val = st.radio(
                label=etq_met,
                options=OBJETIVOS_OPCIONES,
                index=2,
                key=f"s3_obj_{col}",
                horizontal=False,
                label_visibility="collapsed",
            )

        with c_total:
            color_rp = color_obj(ratio_perfil, OBJETIVOS_VALORES[obj_val])
            ratio_str = f"{ratio_perfil:.2f}" if ratio_perfil else "—"
            perfil_str = f"{perfil_val:,.0f}" if perfil_val else "—"
            st.markdown(
                f'<div style="background:#0f1a28; border:1px solid #1e3048; border-radius:8px; padding:6px; text-align:center; height:160px; display:flex; flex-direction:column; justify-content:center;">'
                f'<div style="font-size:10px; color:#7a9ab5; text-transform:uppercase;">Sin partido</div>'
                f'<div style="font-size:22px; font-weight:900; color:white;">{total_sin_md:,.0f}</div>'
                f'<div style="font-size:10px; color:#7a9ab5; text-transform:uppercase;">Perfil</div>'
                f'<div style="font-size:14px; font-weight:700; color:#7a9ab5;">{perfil_str}</div>'
                f'<div style="font-size:22px; font-weight:900; color:{color_rp};">{ratio_str}</div>'
                f'</div>',
                unsafe_allow_html=True
            )