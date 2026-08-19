import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64, os
from datetime import date, timedelta

st.set_page_config(page_title="Velocidades", layout="wide", initial_sidebar_state="expanded")

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
section[data-testid="collapsedControl"] { margin-top: 72px !important; background-color: #0f1a28 !important; z-index: 999999 !important; }
section[data-testid="collapsedControl"] svg { stroke: white !important; }
section[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    margin-top: 72px !important;
}
div[data-testid="stPopover"] > div > button {
    background-color: #0f1a28 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 6px !important;
    color: white !important;
    font-size: 13px !important;
    width: 100% !important;
    text-align: left !important;
}
div[data-testid="stPopover"] > div > button:hover {
    border-color: #00A8CC !important;
    color: #00A8CC !important;
}
div[data-testid="stPopoverBody"] {
    background-color: #0f1a28 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 8px !important;
}
div[data-testid="stPopoverBody"] label { color: #cce0f0 !important; font-size: 13px !important; }
div[data-testid="stPopoverBody"] p     { color: #7a9ab5 !important; font-size: 11px !important; }
div[data-testid="stRadio"] input[type="radio"] { display: none !important; }
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 4px !important;
    background-color: #1e3048 !important;
    border: 1px solid #2a4060 !important;
    border-radius: 8px !important;
    padding: 3px !important;
}
div[data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 5px 14px !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    cursor: pointer !important;
    background: transparent !important;
    white-space: nowrap !important;
}
div[data-testid="stRadio"] label:has(input:checked) { background-color: #00A8CC !important; color: #ffffff !important; }
div[data-testid="stRadio"] label p { color: #ffffff !important; }
div[data-testid="stRadio"] label:not(:has(input:checked)):hover { color: #00A8CC !important; }
div[data-testid="stRadio"] label:not(:has(input:checked)):hover p { color: #00A8CC !important; }
div[data-testid="stRadio"] > label:first-child { display: none !important; }
.seccion-header {
    font-size: 11px; font-weight: 800; letter-spacing: 2px;
    color: #ffffff; background: #0f1a28;
    border-left: 4px solid #00A8CC;
    padding: 8px 14px; margin: 20px 0 10px 0;
    text-transform: uppercase; border-radius: 0 4px 4px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Constantes ────────────────────────────────────────────────────────────────
COLOR_PARTIDO = "#00A8CC"
COLOR_ENTRENO = "#8a9bac"

BANDAS_PCT_DIST = {
    "0-50%":   ["0-33% Velocity Band 1 Total Distance (Set 2)", "33-50% Velocity Band 2 Total Distance (Set 2)"],
    "50-70%":  ["50-70% Velocity Band 3 Total Distance (Set 2)"],
    "70-80%":  ["70-80% Velocity Band 4 Total Distance (Set 2)"],
    "80-90%":  ["80% Velocity Band 5 Total Distance (Set 2)"],
    "90-95%":  ["90% Velocity Band 6 Total Distance (Set 2)"],
    "95-100%": ["95% Velocity Band 7 Total Distance (Set 2)"],
    "+100%":   ["100% Velocity Band 8 Total Distance (Set 2)"],
}

BANDAS_PCT_EFF = {
    "0-50%":   ["33-50% Velocity Band 2 Total Effort Count (Set 2)"],
    "50-70%":  ["50-70% Velocity Band 3 Total Effort Count (Set 2)"],
    "70-80%":  ["70-80% Velocity Band 4 Total Effort Count (Set 2)"],
    "80-90%":  ["80% Velocity Band 5 Total Effort Count (Set 2)"],
    "90-95%":  ["90% Velocity Band 6 Total Effort Count (Set 2)"],
    "95-100%": ["95% Velocity Band 7 Total Effort Count (Set 2)"],
    "+100%":   ["100% Velocity Band 8 Total Effort Count (Set 2)"],
}

COLORES_BANDAS = ["#1e3048", "#2a4a6a", "#1e6a8a", "#0090b0", "#00A8CC", "#00ccaa", "#00ee88"]

GRUPOS_PUESTO = {
    "Primeras":         ["Pilar izquierdo", "Pilar derecho", "Hooker"],
    "Segundas":         ["Segunda Linea"],
    "Terceras":         ["Ala", "Octavo"],
    "Pareja de medios": ["Medio Scrum", "Apertura"],
    "Centros":          ["Centro"],
    "3 del fondo":      ["Wing", "Full Back"],
}

MEDALLAS = {0: "🥇", 1: "🥈", 2: "🥉"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def tiempo_en_distancia(distancia_m, velocidad_kmh):
    if velocidad_kmh <= 0:
        return None
    return distancia_m * 3.6 / velocidad_kmh

# ── Carga de datos ────────────────────────────────────────────────────────────
def cargar_datos():
    df = st.session_state["df_excel"].copy()
    df = df[
        (df["Period Name"] == "Session") &
        (df["Period Tags"] != "Diferenciado")
    ].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    df["Es_Partido"] = df["MD"] == "MD"
    return df

def cargar_datos_todos_periodos():
    df = st.session_state["df_excel"].copy()
    df = df[df["Period Tags"] != "Diferenciado"].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    df["Es_Partido"] = df["MD"] == "MD"
    return df

def cargar_datos_sem():
    df = st.session_state["df_excel"].copy()
    df = df[df["Period Tags"] != "Diferenciado"].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    df["Es_Partido"] = df["MD"] == "MD"
    cols_80_d = ["80% Velocity Band 5 Total Distance (Set 2)", "90% Velocity Band 6 Total Distance (Set 2)",
                 "95% Velocity Band 7 Total Distance (Set 2)", "100% Velocity Band 8 Total Distance (Set 2)"]
    cols_90_d = ["90% Velocity Band 6 Total Distance (Set 2)", "95% Velocity Band 7 Total Distance (Set 2)",
                 "100% Velocity Band 8 Total Distance (Set 2)"]
    cols_95_d = ["95% Velocity Band 7 Total Distance (Set 2)", "100% Velocity Band 8 Total Distance (Set 2)"]
    cols_80_e = ["80% Velocity Band 5 Total Effort Count (Set 2)", "90% Velocity Band 6 Total Effort Count (Set 2)",
                 "95% Velocity Band 7 Total Effort Count (Set 2)", "100% Velocity Band 8 Total Effort Count (Set 2)"]
    cols_90_e = ["90% Velocity Band 6 Total Effort Count (Set 2)", "95% Velocity Band 7 Total Effort Count (Set 2)",
                 "100% Velocity Band 8 Total Effort Count (Set 2)"]
    cols_95_e = ["95% Velocity Band 7 Total Effort Count (Set 2)", "100% Velocity Band 8 Total Effort Count (Set 2)"]
    df["dist_80"] = df[[c for c in cols_80_d if c in df.columns]].fillna(0).sum(axis=1)
    df["dist_90"] = df[[c for c in cols_90_d if c in df.columns]].fillna(0).sum(axis=1)
    df["dist_95"] = df[[c for c in cols_95_d if c in df.columns]].fillna(0).sum(axis=1)
    df["eff_80"]  = df[[c for c in cols_80_e if c in df.columns]].fillna(0).sum(axis=1)
    df["eff_90"]  = df[[c for c in cols_90_e if c in df.columns]].fillna(0).sum(axis=1)
    df["eff_95"]  = df[[c for c in cols_95_e if c in df.columns]].fillna(0).sum(axis=1)
    return df

df_raw      = cargar_datos()
df_raw_all  = cargar_datos_todos_periodos()
df_sem_full = cargar_datos_sem()

vel_max_individual = df_raw.groupby("Player Name")["Maximum Velocity"].max()

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
    f'<div class="topbar-divider"></div><span class="topbar-page">Velocidades</span></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="padding-top:6px; padding-bottom:4px;">'
    '<span style="font-size:22px; font-weight:900; color:white;">VELOCIDADES</span>'
    '<span style="font-size:22px; font-weight:900; color:#00A8CC;"> · CASI</span></div>',
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — TOP DE VELOCIDADES MÁXIMAS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">🏆 Top de velocidades máximas</div>', unsafe_allow_html=True)

col_radio_tiempo, col_sep, col_radio_tipo, col_empty = st.columns([0.55, 0.02, 0.35, 0.08])

with col_radio_tiempo:
    periodo_top = st.radio(
        label="Período",
        options=["1 semana", "15 días", "1 mes", "Todo el año"],
        index=3, key="periodo_top", horizontal=True, label_visibility="collapsed",
    )
with col_radio_tipo:
    tipo_top = st.radio(
        label="Tipo",
        options=["Todo", "Partido", "Entrenamiento"],
        index=0, key="tipo_top", horizontal=True, label_visibility="collapsed",
    )

hoy = date.today()
if periodo_top == "1 semana":
    fecha_corte = hoy - timedelta(days=7)
elif periodo_top == "15 días":
    fecha_corte = hoy - timedelta(days=15)
elif periodo_top == "1 mes":
    fecha_corte = hoy - timedelta(days=30)
else:
    fecha_corte = df_raw["Fecha"].min()

df_top_base = df_raw[df_raw["Fecha"] >= fecha_corte].copy()
if tipo_top == "Partido":
    df_top_base = df_top_base[df_top_base["Es_Partido"]]
elif tipo_top == "Entrenamiento":
    df_top_base = df_top_base[~df_top_base["Es_Partido"]]

if df_top_base.empty:
    st.warning("No hay datos para el período y tipo de sesión seleccionados.")
else:
    df_top = df_top_base.copy()
    df_top = df_top.sort_values("Maximum Velocity", ascending=False).reset_index(drop=True)
    df_top = df_top.head(10)

    vel_min_escala = df_top["Maximum Velocity"].min()
    vel_max_escala = df_top["Maximum Velocity"].max()

    bar_colors = [COLOR_PARTIDO if es else COLOR_ENTRENO for es in df_top["Es_Partido"]]

    nombres_display = []
    for i, (_, row) in enumerate(df_top.iterrows()):
        medalla = MEDALLAS.get(i, "")
        nombre  = row["Player Name"] + "\u200b" * i
        nombres_display.append(f"{medalla} {nombre}" if medalla else f"    {nombre}")

    hover_texts = []
    for _, row in df_top.iterrows():
        hover_texts.append(
            f"<b>{row['Player Name']}</b><br>"
            f"Velocidad: {row['Maximum Velocity']:.2f} km/h<br>"
            f"Actividad: {row['Activity Name']}<br>"
            f"Fecha: {row['Fecha']}<br>"
            f"Tipo: {'Partido' if row['Es_Partido'] else 'Entrenamiento'}"
        )

    bar_texts = [f"{v:.2f} km/h" for v in df_top["Maximum Velocity"]]

    fig_top = go.Figure(go.Bar(
        x=df_top["Maximum Velocity"],
        y=nombres_display,
        orientation="h",
        marker_color=bar_colors,
        marker_line_width=0,
        text=bar_texts,
        textposition="outside",
        textfont=dict(size=11, color="white"),
        cliponaxis=False,
        hovertext=hover_texts,
        hoverinfo="text",
    ))
    fig_top.update_layout(
        paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
        height=max(350, len(df_top) * 34),
        margin=dict(t=20, b=20, l=10, r=120),
        xaxis=dict(range=[vel_min_escala - 0.5, vel_max_escala + 1.0],
                   showgrid=True, gridcolor="#1e3048",
                   tickfont=dict(color="#7a9ab5", size=10), ticksuffix=" km/h", zeroline=False),
        yaxis=dict(tickfont=dict(size=11, color="#cce0f0"), showgrid=False, autorange="reversed"),
        showlegend=False, bargap=0.3,
    )
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown(
        '<div style="font-size:11px; color:#7a9ab5; margin-bottom:6px;">💡 Pasá el mouse sobre las barras para ver detalles</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="margin-top:-8px; margin-bottom:16px; display:flex; gap:20px;">'
        f'<span style="font-size:11px; color:#7a9ab5; display:flex; align-items:center; gap:6px;">'
        f'<span style="width:12px; height:12px; border-radius:2px; background:{COLOR_PARTIDO}; display:inline-block;"></span>'
        f'Partido</span>'
        f'<span style="font-size:11px; color:#7a9ab5; display:flex; align-items:center; gap:6px;">'
        f'<span style="width:12px; height:12px; border-radius:2px; background:{COLOR_ENTRENO}; display:inline-block;"></span>'
        f'Entrenamiento</span></div>',
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color:#1e3048; margin:12px 0 20px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — SEMÁFORO DE VELOCIDAD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">🚦 Semáforo de velocidad</div>', unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:11px; color:#7a9ab5; margin-bottom:12px;">'
    '% alcanzado respecto al máximo o promedio personal · por grupo posicional</div>',
    unsafe_allow_html=True
)

METRICAS_SEM = {
    "Vel Max":              ("Maximum Velocity",  "max_personal"),
    "Sprints (#)":          ("+25 Km/h #",        "max_personal"),
    "Distancia Sprint":     ("DT + 25 Km/h",      "max_personal"),
    "Distancia HSR":        ("AI 18 Km/h",        "prom_5partidos"),
    "Distancia +80% vel":   ("dist_80",           "max_personal"),
    "Cantidad +80% vel":    ("eff_80",            "max_personal"),
    "Distancia +90% vel":   ("dist_90",           "max_personal"),
    "Cantidad +90% vel":    ("eff_90",            "max_personal"),
    "Distancia +95% vel":   ("dist_95",           "max_personal"),
    "Cantidad +95% vel":    ("eff_95",            "max_personal"),
    "Max Acel":             ("Max Acceleration",  "max_personal"),
    "Max Decel":            ("Max Deceleration",  "max_personal"),
}

BANDAS_SEM = [
    (">95%",   lambda p: p > 95,        "#00CC44"),
    ("90-95%", lambda p: 90 < p <= 95,  "#4CAF50"),
    ("85-90%", lambda p: 85 < p <= 90,  "#FFD000"),
    ("80-85%", lambda p: 80 < p <= 85,  "#FF8C00"),
    ("<80%",   lambda p: p <= 80,       "#FF0000"),
]

GRUPOS_SEM = {
    "Primeras":         ["Pilar izquierdo", "Pilar derecho", "Hooker"],
    "Segundas":         ["Segunda Linea"],
    "Terceras":         ["Ala", "Octavo"],
    "Pareja de medios": ["Medio Scrum", "Apertura"],
    "Centros":          ["Centro"],
    "3 del fondo":      ["Wing", "Full Back"],
}

# ── Filtros del semáforo ──────────────────────────────────────────────────────
DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
todas_fechas_sem   = sorted(df_sem_full["Fecha"].unique(), reverse=True)
todos_periodos_sem = [
    "Session", "Velocidad", "Juego", "Destrezas",
    "RHIE", "RSA", "Backs - Pie", "Primer Tiempo", 
    "Segundo Tiempo", "Backs - Lanzamientos",
    "Fowards - Scrum", "Fowards - Line"
]
# Solo mostrar los que existen en el dataset
todos_periodos_sem = [p for p in todos_periodos_sem if p in df_sem_full["Period Name"].unique()]

fs1, fs2, fs3 = st.columns([0.30, 0.30, 0.30])

# Leer selección actual antes de renderizar
periodo_sem_actual = st.session_state.get("periodo_sem", todos_periodos_sem[0])
if periodo_sem_actual not in todos_periodos_sem:
    periodo_sem_actual = todos_periodos_sem[0]

fecha_sem_actual_idx = st.session_state.get("fecha_sem", 0)
if not isinstance(fecha_sem_actual_idx, int):
    fecha_sem_actual_idx = 0
fecha_sem_actual = todas_fechas_sem[fecha_sem_actual_idx] if fecha_sem_actual_idx < len(todas_fechas_sem) else todas_fechas_sem[0]

# Fechas válidas para el período seleccionado
fechas_validas = sorted(
    df_sem_full[df_sem_full["Period Name"] == periodo_sem_actual]["Fecha"].unique(),
    reverse=True
)
fechas_validas = [f for f in fechas_validas if f in todas_fechas_sem]
if not fechas_validas:
    fechas_validas = todas_fechas_sem

with fs1:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Fecha</span>', unsafe_allow_html=True)
    opciones_fecha_sem = []
    for f in fechas_validas:
        dia = DIAS_ES[f.weekday()]
        fila_md = df_sem_full[(df_sem_full["Fecha"] == f) & (df_sem_full["MD"] == "MD") & (df_sem_full["Rival"].notna())]
        rival_str = f" · {fila_md['Rival'].iloc[0]}" if not fila_md.empty else ""
        opciones_fecha_sem.append(f"{dia} {f.day:02d}/{f.month:02d}{rival_str}")

    fecha_sem_idx = st.selectbox(
        label="Fecha", options=range(len(fechas_validas)),
        format_func=lambda i: opciones_fecha_sem[i],
        key="fecha_sem", label_visibility="collapsed",
    )
    fecha_sem_sel = fechas_validas[fecha_sem_idx]

# Períodos válidos para la fecha seleccionada
periodos_validos = [p for p in todos_periodos_sem if not df_sem_full[
    (df_sem_full["Fecha"] == fecha_sem_sel) &
    (df_sem_full["Period Name"] == p)
].empty]
if not periodos_validos:
    periodos_validos = todos_periodos_sem

with fs2:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Período</span>', unsafe_allow_html=True)
    NOMBRES_PERIODO = {"Session": "Sesión Total", "Primer Tiempo": "Primer tiempo", "Segundo Tiempo": "Segundo tiempo",
    "RSA": "RSA", "Fowards - Scrum": "Scrum", "Fowards - Line": "Line", "Backs - Pie": "Juego con el Pie", "Backs - Lanzamientos": "Lanzamientos"}
    periodo_sem = st.selectbox(
        label="Período",
        options=periodos_validos,
        format_func=lambda x: NOMBRES_PERIODO.get(x, x),
        index=0,
        key="periodo_sem",
        label_visibility="collapsed",
    )

with fs3:
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Métrica</span>', unsafe_allow_html=True)
    metrica_sem = st.selectbox(
        label="Métrica", options=list(METRICAS_SEM.keys()),
        key="metrica_sem", label_visibility="collapsed",
    )

# ── Filtrar y calcular ────────────────────────────────────────────────────────
col_metrica, tipo_ref = METRICAS_SEM[metrica_sem]

df_fecha = df_sem_full[
    (df_sem_full["Fecha"] == fecha_sem_sel) &
    (df_sem_full["Period Name"] == periodo_sem)
].copy()


if df_fecha.empty:
    st.warning("No hay datos para la fecha y período seleccionados.")
else:
    agg_func = "max" if col_metrica in ["Maximum Velocity", "Max Acceleration", "Max Deceleration"] else "sum"
    df_val_sesion = df_fecha.groupby(["Player Name", "Position Name"])[col_metrica].agg(agg_func).reset_index()
    df_val_sesion.columns = ["Player Name", "Position Name", "Valor_Sesion"]

    df_hist = df_sem_full[
        (df_sem_full["Fecha"] < fecha_sem_sel) &
        (df_sem_full["Period Name"] == "Session")
    ].copy()

    if tipo_ref == "max_personal":
        ref = df_hist.groupby("Player Name")[col_metrica].max()
    else:
        df_hist_md = df_hist[df_hist["Es_Partido"]].sort_values("Fecha")
        ref = (
            df_hist_md.groupby(["Player Name", "Fecha"])[col_metrica]
            .sum().reset_index()
            .groupby("Player Name")
            .apply(lambda x: x.tail(5)[col_metrica].mean())
        )

    df_val_sesion["Referencia"] = df_val_sesion["Player Name"].map(ref)
    df_val_sesion["Pct"] = (df_val_sesion["Valor_Sesion"] / df_val_sesion["Referencia"] * 100).round(1)
    df_val_sesion = df_val_sesion.dropna(subset=["Pct"])

    total_jug = len(df_val_sesion)

    # ── Header de columnas ────────────────────────────────────────────────────
    cols_h = st.columns([0.16] + [0.168] * 5)
    with cols_h[0]:
        st.markdown("&nbsp;", unsafe_allow_html=True)

    for i, (banda, cond, color) in enumerate(BANDAS_SEM):
        n_b   = len(df_val_sesion[df_val_sesion["Pct"].apply(cond)])
        pct_b = round(n_b / total_jug * 100) if total_jug > 0 else 0
        with cols_h[i + 1]:
            st.markdown(
                f'<div style="background:#0f1a28; border:2px solid {color}; border-radius:8px;'
                f'text-align:center; padding:10px 4px; margin-bottom:6px;">'
                f'<div style="font-size:16px; font-weight:900; color:{color};">{banda}</div>'
                f'<div style="font-size:12px; color:{color}; opacity:0.8;">{n_b} · {pct_b}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # ── Filas por grupo posicional ────────────────────────────────────────────
    for grupo, puestos in GRUPOS_SEM.items():
        df_grupo = df_val_sesion[df_val_sesion["Position Name"].isin(puestos)]
        if df_grupo.empty:
            continue

        st.markdown("<div style='border-top:1px solid #2a4060; margin:6px 0;'></div>", unsafe_allow_html=True)
        cols_f = st.columns([0.16] + [0.168] * 5)

        with cols_f[0]:
            st.markdown(
                f'<div style="display:flex; align-items:center; min-height:80px;">'
                f'<span style="font-size:11px; font-weight:800; color:#FFD000;'
                f'text-transform:uppercase; letter-spacing:1px;">{grupo}</span></div>',
                unsafe_allow_html=True
            )

        for i, (banda, cond, color) in enumerate(BANDAS_SEM):
            jug_banda = df_grupo[df_grupo["Pct"].apply(cond)].sort_values("Pct", ascending=False)
            with cols_f[i + 1]:
                if jug_banda.empty:
                    st.markdown("&nbsp;", unsafe_allow_html=True)
                else:
                    items_html = ""
                    for _, row in jug_banda.iterrows():
                        items_html += (
                            f'<div style="display:flex; justify-content:space-between; align-items:center;'
                            f'padding:5px 8px; border-bottom:1px solid #1e3048;">'
                            f'<div>'
                            f'<div style="font-size:12px; font-weight:700; color:#cce0f0;">{row["Player Name"]}</div>'
                            f'<div style="font-size:10px; color:#5a7a90;">{row["Valor_Sesion"]:.1f}</div>'
                            f'</div>'
                            f'<div style="font-size:13px; font-weight:900; color:{color};">{row["Pct"]:.0f}%</div>'
                            f'</div>'
                        )
                    borde = color + "40"
                    st.markdown(
                        f'<div style="background:#0f1a28; border:1px solid {borde};'
                        f'border-radius:8px; margin-bottom:4px; overflow-y:auto; max-height:200px; box-shadow: 0 -8px 8px -4px #1a2535 inset;">'
                        f'{items_html}</div>',
                        unsafe_allow_html=True
                    )
st.markdown("<hr style='border-color:#1e3048; margin:12px 0 20px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — GRILLA HISTÓRICA DE % VEL MÁX POR SEMANA
# Muestra Max Vel (% Max) de cada jugador por semana, agrupado por posición
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">📈 Historial % velocidad máxima por semana</div>', unsafe_allow_html=True)

# ── Filtros de jugador y puesto ───────────────────────────────────────────────
# Opciones disponibles
todos_jug_g   = sorted(df_raw["Player Name"].dropna().unique().tolist())
todos_pue_g   = sorted(df_raw["Position Name"].dropna().unique().tolist())
todos_equ_g   = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw["Equipo"].dropna().unique()]

jug_sel_g = [j for j in todos_jug_g if st.session_state.get(f"gj_{j}", False)]
pue_sel_g = [p for p in todos_pue_g if st.session_state.get(f"gp_{p}", False)]
equ_sel_g = [e for e in todos_equ_g if st.session_state.get(f"ge_{e}", False)]

jug_act_g = jug_sel_g if jug_sel_g else todos_jug_g
pue_act_g = pue_sel_g if pue_sel_g else todos_pue_g
equ_act_g = equ_sel_g if equ_sel_g else None

def borrar_keys_g(prefix):
    for k in list(st.session_state.keys()):
        if k.startswith(prefix) and not k.endswith(("_todos",)):
            if isinstance(st.session_state[k], bool):
                st.session_state[k] = False

# ── Filtro de semanas ─────────────────────────────────────────────────────────
df_cat = df_raw.copy()
df_cat["SemanaInicio"] = pd.to_datetime(df_cat["Fecha"]) - pd.to_timedelta(
    pd.to_datetime(df_cat["Fecha"]).dt.weekday, unit="D"
)
semanas_cat = sorted(df_cat["SemanaInicio"].unique())
inicio_cal2 = pd.Timestamp(semanas_cat[0])
todas_cal2  = pd.date_range(inicio_cal2, pd.Timestamp(semanas_cat[-1]), freq="7D")
num_por_sem2 = {pd.Timestamp(s): i for i, s in enumerate(todas_cal2, start=1)}

etq_semanas_filtro = []
for sem in sorted(semanas_cat, reverse=True):
    sem = pd.Timestamp(sem)
    n   = num_por_sem2.get(sem, 0)
    g   = df_cat[df_cat["SemanaInicio"] == sem]
    md_rows = g[g["MD"] == "MD"]
    rival = None
    if len(md_rows):
        rv = md_rows["Rival"].dropna()
        if len(rv):
            rival = str(rv.iloc[0]).replace("Hindú", "Hindu")
    fin_sem = sem + pd.Timedelta(days=6)
    etq = f"S{n} {sem.day:02d}/{sem.month:02d} - {fin_sem.day:02d}/{fin_sem.month:02d}"
    if rival:
        etq += f" {rival}"
    etq_semanas_filtro.append(etq)

mapa_sem_etq = dict(zip([pd.Timestamp(s) for s in sorted(semanas_cat, reverse=True)], etq_semanas_filtro))

sem_sel_g = [e for e in etq_semanas_filtro if st.session_state.get(f"gs_{e}", False)]
sem_act_g = sem_sel_g if sem_sel_g else etq_semanas_filtro
semanas_sel_ts = [s for s, e in mapa_sem_etq.items() if e in sem_act_g]

# ── Render filtros en una sola fila ──────────────────────────────────────────
fg1, fg2, fg3, fg4, fg5 = st.columns(5)

with fg1:
    btn_j = "Todos ▾" if not jug_sel_g else (f"{jug_sel_g[0]} ▾" if len(jug_sel_g)==1 else f"{len(jug_sel_g)} selec. ▾")
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Jugador</span>', unsafe_allow_html=True)
    with st.popover(btn_j, use_container_width=True):
        st.button("✓ Todos", key="gj_todos", use_container_width=True, on_click=borrar_keys_g, args=("gj_",))
        for j in todos_jug_g:
            st.checkbox(j, key=f"gj_{j}")

with fg2:
    btn_p = "Todos ▾" if not pue_sel_g else (f"{pue_sel_g[0]} ▾" if len(pue_sel_g)==1 else f"{len(pue_sel_g)} selec. ▾")
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Puesto</span>', unsafe_allow_html=True)
    with st.popover(btn_p, use_container_width=True):
        st.button("✓ Todos", key="gp_todos", use_container_width=True, on_click=borrar_keys_g, args=("gp_",))
        for grupo, puestos in GRUPOS_PUESTO.items():
            puestos_v = [p for p in puestos if p in todos_pue_g]
            if not puestos_v:
                continue
            todos_g_sel = all(st.session_state.get(f"gp_{p}", False) for p in puestos_v)
            g_chk = st.checkbox(grupo.upper(), value=todos_g_sel, key=f"gp_grupo_{grupo}")
            if g_chk != todos_g_sel:
                for p in puestos_v:
                    st.session_state[f"gp_{p}"] = g_chk
                st.rerun()
            for p in puestos_v:
                _, col_chk = st.columns([0.15, 0.85])
                with col_chk:
                    st.checkbox(p, key=f"gp_{p}")

with fg3:
    btn_e = "Todos ▾" if not equ_sel_g else (f"{equ_sel_g[0]} ▾" if len(equ_sel_g)==1 else f"{len(equ_sel_g)} selec. ▾")
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Equipo</span>', unsafe_allow_html=True)
    with st.popover(btn_e, use_container_width=True):
        st.button("✓ Todos", key="ge_todos", use_container_width=True, on_click=borrar_keys_g, args=("ge_",))
        for e in todos_equ_g:
            st.checkbox(e, key=f"ge_{e}")

with fg4:
    btn_s = "Todas ▾" if not sem_sel_g else (f"{sem_sel_g[0][:12]}... ▾" if len(sem_sel_g)==1 else f"{len(sem_sel_g)} sem. ▾")
    st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Semana</span>', unsafe_allow_html=True)
    with st.popover(btn_s, use_container_width=True):
        st.button("✓ Todas", key="gs_todos", use_container_width=True, on_click=borrar_keys_g, args=("gs_",))
        for e in etq_semanas_filtro:
            st.checkbox(e, key=f"gs_{e}")

col_radio_g, _ = st.columns([0.4, 0.6])
with col_radio_g:
    tipo_grilla = st.radio(
        label="Sesión grilla",
        options=["Todo", "Partido", "Entrenamiento"],
        index=0, key="tipo_grilla_2", horizontal=True, label_visibility="collapsed",
    )


# ── Preparar datos ────────────────────────────────────────────────────────────
# Usar df_raw (Period Name == Session, Period Tags != Diferenciado, sin filtro minutos)
df_g = df_raw.copy()

# Filtrar tipo de sesión
if tipo_grilla == "Partido":
    df_g = df_g[df_g["Es_Partido"]]
elif tipo_grilla == "Entrenamiento":
    df_g = df_g[~df_g["Es_Partido"]]

# Filtrar jugador, puesto y semanas
df_g = df_g[df_g["Player Name"].isin(jug_act_g)]
df_g = df_g[df_g["Position Name"].isin(pue_act_g)]
df_g["SemanaInicio"] = pd.to_datetime(df_g["Fecha"]) - pd.to_timedelta(
    pd.to_datetime(df_g["Fecha"]).dt.weekday, unit="D"
)
df_g = df_g[df_g["SemanaInicio"].isin(semanas_sel_ts)]

if equ_act_g and "Equipo" in df_g.columns:
    md_equipo = df_raw[
        (df_raw["MD"] == "MD") &
        (df_raw["Equipo"].isin(equ_act_g))
    ][["Player Name", "Fecha"]].drop_duplicates()
    md_equipo["Fecha"] = pd.to_datetime(md_equipo["Fecha"])
    df_g["Fecha_dt"] = pd.to_datetime(df_g["Fecha"])
    filas_validas = []
    for _, row in md_equipo.iterrows():
        mask = (
            (df_g["Player Name"] == row["Player Name"]) &
            (df_g["Fecha_dt"] >= row["Fecha"] - pd.Timedelta(days=6)) & 
            (df_g["Fecha_dt"] <= row["Fecha"] + pd.Timedelta(days=6))
        )
        filas_validas.append(df_g[mask])
    if filas_validas:
        df_g = pd.concat(filas_validas).drop_duplicates()
    else:
        df_g = df_g.iloc[0:0]
    df_g = df_g.drop(columns=["Fecha_dt"])

if df_g.empty:
    st.warning("No hay datos para los filtros seleccionados.")
else:

# Quedarse con el último puesto registrado por jugador
    ultimo_puesto = (
        df_g.sort_values("Fecha")
        .groupby("Player Name")["Position Name"]
        .last()
    )
    df_g["Position Name"] = df_g["Player Name"].map(ultimo_puesto)
    # Max del % por jugador por semana
    grilla = (
        df_g.groupby(["Player Name", "Position Name", "SemanaInicio"])["Max Vel (% Max)"]
        .max()
        .reset_index()
    )

    # Construir mapa semana → etiqueta corta (rival si hay MD, si no fecha)
    df_g_sem = df_raw.copy()
    df_g_sem["SemanaInicio"] = pd.to_datetime(df_g_sem["Fecha"]) - pd.to_timedelta(
        pd.to_datetime(df_g_sem["Fecha"]).dt.weekday, unit="D"
    )
    semanas_con_datos = sorted(df_g_sem["SemanaInicio"].unique())
    inicio_cal = pd.Timestamp(semanas_con_datos[0])
    todas_cal   = pd.date_range(inicio_cal, pd.Timestamp(semanas_con_datos[-1]), freq="7D")
    num_por_sem = {pd.Timestamp(s): i for i, s in enumerate(todas_cal, start=1)}

    mapa_sem_corta = {}
    for sem, g in df_g_sem.groupby("SemanaInicio"):
        sem = pd.Timestamp(sem)
        n   = num_por_sem.get(sem, 0)
        md_rows = g[g["MD"] == "MD"]
        rival = None
        if len(md_rows):
            rv = md_rows["Rival"].dropna()
            if len(rv):
                rival = str(rv.iloc[0]).replace("Hindú", "Hindu")
        etq = f"S{n} {rival}" if rival else f"S{n} {sem.day:02d}/{sem.month:02d}"
        mapa_sem_corta[sem] = etq

    grilla["EtqSem"] = grilla["SemanaInicio"].map(mapa_sem_corta)
    mask_sin = grilla["EtqSem"].isna()
    grilla.loc[mask_sin, "EtqSem"] = grilla.loc[mask_sin, "SemanaInicio"].dt.strftime("S %d/%m")

    semanas_ord  = sorted(grilla["SemanaInicio"].unique())
    etqs_semanas = [mapa_sem_corta.get(s, pd.Timestamp(s).strftime("S %d/%m")) for s in semanas_ord]

    # Color según % de vel max — bandas semáforo
    def color_vel(pct):
        if pd.isna(pct):    return "#1e3048"
        if pct > 100:       return "#9B59B6"
        if pct > 95:        return "#00CC44"
        if pct > 90:        return "#4CAF50"
        if pct > 85:        return "#FFD000"
        if pct > 80:        return "#FF8C00"
        return "#FF0000"

    # ── Render por grupo posicional — 4 jugadores por fila ───────────────────
    for grupo, puestos in GRUPOS_PUESTO.items():
        df_grp = grilla[grilla["Position Name"].isin(puestos)]
        if df_grp.empty:
            continue

        jugadores_grp = sorted(df_grp["Player Name"].unique())

        # Título del grupo
        st.markdown(
            f'<div style="font-size:11px; font-weight:800; color:#FFD000; text-transform:uppercase;'
            f' letter-spacing:2px; margin:14px 0 6px 0; padding:4px 0; border-bottom:1px solid #2a4060;">'
            f'{grupo}</div>',
            unsafe_allow_html=True
        )

        # Dividir jugadores en filas de 4
        for fila_start in range(0, len(jugadores_grp), 4):
            fila_jugs = jugadores_grp[fila_start:fila_start + 4]
            cols_fila = st.columns(4)

            for col_idx, jug in enumerate(fila_jugs):
                df_jug   = df_grp[df_grp["Player Name"] == jug]
                mapa_val = dict(zip(df_jug["SemanaInicio"], df_jug["Max Vel (% Max)"]))

                with cols_fila[col_idx]:
                    # Nombre del jugador
                    st.markdown(
                        f'<div style="font-size:11px; font-weight:700; color:#cce0f0;'
                        f' margin-bottom:4px;">{jug}</div>',
                        unsafe_allow_html=True
                    )

                    # Mini gráfico de barras HTML
                    MAX_H = 100
                    barras_html = '<div style="display:flex; align-items:flex-end; gap:2px; height:110px; background:#0f1a28; border-radius:6px; padding:6px 4px 4px 4px;">'
                    for sem in semanas_ord:
                        val = mapa_val.get(sem, None)
                        tiene_val = val is not None and not np.isnan(val)
                        color  = color_vel(val) if tiene_val else "#1e3048"
                        texto  = f"{val:.0f}" if tiene_val else ""
                        altura = max(4, int(10 + (val - 50) * (90 / 50))) if tiene_val else 4
                        altura = min(altura, MAX_H)
                        etq    = etqs_semanas[semanas_ord.index(sem)]
                        barras_html += (
                            f'<div style="flex:1; display:flex; flex-direction:column;'
                            f' align-items:center; justify-content:flex-end; gap:1px;">'
                            f'<div style="font-size:7px; color:#ffffff; font-weight:700;">{texto}</div>'
                            f'<div title="{etq}" style="width:100%; height:{altura}px; background:{color};'
                            f' border-radius:2px 2px 0 0;"></div>'
                            f'</div>'
                        )
                    barras_html += '</div>'

                    # Etiquetas de semana debajo
                    etqs_html = '<div style="display:flex; gap:2px; margin-top:2px;">'
                    for sem in semanas_ord:
                        etq = etqs_semanas[semanas_ord.index(sem)]
                        etq_corta = etq.split()[-1] if etq else ""
                        etqs_html += f'<div style="flex:1; font-size:6px; color:#5a7a90; text-align:center; overflow:hidden;">{etq_corta}</div>'
                    etqs_html += '</div>'

                    st.markdown(barras_html + etqs_html, unsafe_allow_html=True)

    # ── Leyenda ───────────────────────────────────────────────────────────────
    bandas_leyenda = [
        (">100%", "#9B59B6"), (">95%", "#00CC44"), ("90–95%", "#4CAF50"), ("85–90%", "#FFD000"),
        ("80–85%", "#FF8C00"), ("<80%", "#FF0000"),
    ]
    leyenda_html = '<div style="display:flex; flex-wrap:wrap; gap:14px; margin-top:14px; padding-top:10px; border-top:1px solid #1e3048;">'
    for etq, col in bandas_leyenda:
        leyenda_html += (
            f'<span style="display:inline-flex; align-items:center; gap:6px;">'
            f'<span style="width:14px; height:14px; border-radius:3px; background:{col}; display:inline-block;"></span>'
            f'<span style="font-size:11px; color:#cce0f0;">{etq}</span></span>'
        )
    leyenda_html += "</div>"
    st.markdown(leyenda_html, unsafe_allow_html=True)