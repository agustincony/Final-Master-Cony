from sys import prefix

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64, os

st.set_page_config(page_title="Informe de sesión", layout="wide", initial_sidebar_state="expanded")

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
header[data-testid="stHeader"]   { display: none !important; }
.stApp                           { background-color: #1a2535; color: white; }
.block-container                 { padding-top: 90px !important; padding-left: 2rem !important; padding-right: 2rem !important; }
section[data-testid="stSidebar"] { background-color: #0f1a28 !important; margin-top: 72px !important; }
section[data-testid="stSidebar"] span { color: white !important; }
section[data-testid="stSidebar"] p    { color: white !important; }
section[data-testid="stSidebar"] a    { color: white !important; }
div[data-testid="stSidebarCollapseButton"] { display: none !important; }
section[data-testid="collapsedControl"] { display: none !important; }
div[data-testid="stMultiSelect"] > label { color: #7a9ab5 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
div[data-testid="stMultiSelect"] > div > div { background-color: #0f1a28 !important; border-color: #1e3048 !important; color: white !important; }
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
div[data-testid="stRadio"] label:has(input:checked) { background-color: #00A8CC !important; }
div[data-testid="stRadio"] label p { color: #ffffff !important; }
div[data-testid="stRadio"] > label:first-child { display: none !important; }

/* ── Popover botones (filtros) ── */
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
/* Panel del popover */
div[data-testid="stPopoverBody"] {
    background-color: #0f1a28 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 8px !important;
}
/* Checkboxes dentro del popover */
div[data-testid="stPopoverBody"] label {
    color: #cce0f0 !important;
    font-size: 13px !important;
}
div[data-testid="stPopoverBody"] p {
    color: #7a9ab5 !important;
    font-size: 11px !important;
}

/* ── Label encima del popover (igual que otros filtros) ── */
.filtro-label {
    font-size: 11px;
    color: #7a9ab5;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
    display: block;
}
.seccion-header {
    font-size: 11px; font-weight: 800; letter-spacing: 2px;
    color: #ffffff; background: #0f1a28;
    border-left: 4px solid #00A8CC;
    padding: 8px 14px; margin: 20px 0 10px 0;
    text-transform: uppercase; border-radius: 0 4px 4px 0;
}
.tarjeta-cruda { background: #0f1a28; border: 1px solid #1e3048; border-radius: 10px; padding: 14px 10px 12px 14px; min-height: 90px; }
.tarjeta-cruda .label  { font-size: 10px; color: #00A8CC; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.tarjeta-cruda .valor  { font-size: 28px; font-weight: 800; color: #ffffff; line-height: 1; }
.tarjeta-cruda .unidad { font-size: 10px; color: #3a5a70; margin-top: 3px; }
.tarjeta-comp { border-radius: 10px; padding: 14px 14px 10px 14px; min-height: 130px; }
.tarjeta-comp .metrica-label { font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px; }
.tarjeta-comp .sub-label     { font-size: 9px; color: #5a7a90; margin-bottom: 8px; }
.tarjeta-comp .pct           { font-size: 34px; font-weight: 900; line-height: 1; margin-bottom: 6px; }
.tarjeta-comp .valores       { font-size: 10px; color: #5a7a90; margin-bottom: 8px; }
.barra-contenedor { background: #1e3048; border-radius: 4px; height: 5px; width: 100%; overflow: hidden; }
.barra-fill       { height: 5px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Métricas ──────────────────────────────────────────────────────────────────
METRICAS = {
    "Minutos":                             ("Minutos",        "min",      "⏱️"),
    "Distancia Total":                     ("Distancia",      "mts",        "📍"),
    "AI 18 Km/h":                          ("HSR",            "mts",        "⚡"),
    "DT + 25 Km/h":                        ("Sprint",         "mts",        "🚀"),
    "+25 Km/h #":                          ("N° Sprints",     "cantidad", "🏃"),
    "Acel 2,5 m/ss #":                     ("Acel",           "cantidad", "▲"),
    "Desacel -2,5 m/ss #":                 ("Decel",          "cantidad", "▼"),
    "Contact Involvement Total Count Avg": ("Contactos",      "cantidad", "💥"),
}
COLS = list(METRICAS.keys())

# ── Grupos de puestos ─────────────────────────────────────────────────────────
GRUPOS_PUESTO = {
    "Primeras":        ["Pilar izquierdo", "Pilar derecho", "Hooker"],
    "Segundas":        ["Segunda Linea"],
    "Terceras":        ["Ala", "Octavo"],
    "Pareja de medios":["Medio Scrum", "Apertura"],
    "Centros":         ["Centro"],
    "3 del fondo":     ["Wing", "Full Back"],
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def color_pct(pct):
    """Devuelve color según porcentaje respecto al benchmark."""
    if pct is None or np.isnan(pct): return "#4a6a80"
    if pct < 0.70:  return "#FF0000"
    if pct < 0.85:  return "#FFD000"
    if pct < 1.15:  return "#00CC44"
    if pct <= 1.30: return "#FFD000"
    return "#FF0000"

def fondo_tarjeta(pct):
    """Devuelve (fondo, borde) según porcentaje.
    El borde solo se pinta en exceso (>115%): amarillo hasta 130%, rojo si pasa."""
    if pct is None or np.isnan(pct): return "#0f1a28", "#1e3048"
    if pct <= 1.15: return "#0f1a28", "#1e3048"   # sin borde coloreado
    if pct <= 1.30: return "#0f1a28", "#FFD000"   # borde amarillo
    return "#0f1a28", "#FF0000"                    # borde rojo

def fmt(val):
    """Formatea un número para mostrar en pantalla."""
    if val is None or (isinstance(val, float) and np.isnan(val)): return "—"
    if val >= 10: return f"{val:,.0f}"
    return f"{val:.1f}"

def barra_html(pct, color):
    """Genera HTML de barra de progreso."""
    ancho = min(int(pct * 100), 100) if pct and not np.isnan(pct) else 0
    return f'<div class="barra-contenedor"><div class="barra-fill" style="width:{ancho}%; background:{color};"></div></div>'

def calc_bench(df_base, col):
    """Promedio histórico replicando el DAX de Power BI:
    1. Agrupar por jugador+fecha sumando minutos y la métrica
    2. Filtrar solo los que sumen más de 30 minutos (como el FILTER del ADDCOLUMNS en DAX)
    3. Promediar los valores resultantes (AVERAGEX)
    """
    por_dia = df_base.groupby(["Player Name", "Fecha"]).agg(
        minutos=("Minutos", "sum"),
        valor=(col, "sum")
    ).reset_index()
    por_dia = por_dia[por_dia["minutos"] > 30]  # filtro DAX: [@MinutosDia] > 30
    return por_dia["valor"].mean() if len(por_dia) > 0 else np.nan

def img_base64(path):
    """Convierte imagen a base64 para incrustar en HTML."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    """Dataset principal con filtro Minutos > 30 por fila — para mostrar datos de sesión."""
    df = pd.read_excel("TOTALES GPS.xlsx")
    df = df[
        (df["Period Name"] == "Session") &
        (df["Period Tags"] != "Diferenciado")
    ].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    # Corregir typo en el dataset original
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    return df

@st.cache_data
def cargar_datos_sin_filtro_minutos():
    """Dataset SIN filtro de minutos por fila — para el benchmark DAX.
    El DAX filtra Minutos > 30 sobre la SUMA por jugador+fecha, no fila por fila."""
    df = pd.read_excel("TOTALES GPS.xlsx")
    df = df[
        (df["Period Name"] == "Session") &
        (df["Period Tags"] != "Diferenciado")
    ].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
    df["Position Name"] = df["Position Name"].str.replace("Pilar izquiero", "Pilar izquierdo", regex=False)
    return df

df_raw      = cargar_datos()                    # para filtros y datos de sesión
df_raw_full = cargar_datos_sin_filtro_minutos() # para benchmarks históricos

# ── Topbar fija ───────────────────────────────────────────────────────────────
logo_b64  = img_base64("LOGO_CASI_SIN_FONDO.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:62px; width:auto;">' if logo_b64 else "⚡"

st.markdown(f"""
<style>
.topbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
    background: #0f1a28; border-bottom: 3px solid #00A8CC; height: 72px;
    display: flex; align-items: center; padding: 0 24px; gap: 16px;
}}
.topbar-logo    {{ display: flex; align-items: center; }}
.topbar-divider {{ width: 1px; height: 36px; background: #2a4060; margin: 0 16px; }}
.topbar-club    {{ font-size: 18px; font-weight: 900; color: white; letter-spacing: 1px; text-transform: uppercase; }}
.topbar-sub     {{ font-size: 13px; font-weight: 600; color: #00A8CC; letter-spacing: 2px; text-transform: uppercase; }}
.topbar-page    {{ font-size: 13px; font-weight: 700; color: #7a9ab5; letter-spacing: 2px; text-transform: uppercase; }}
</style>
<div class="topbar">
    <div class="topbar-logo">{logo_html}</div>
    <div class="topbar-divider"></div>
    <span class="topbar-club">Club Atlético de San Isidro</span>
    <div class="topbar-divider"></div>
    <span class="topbar-sub">Análisis de rendimiento</span>
    <div class="topbar-divider"></div>
    <span class="topbar-page">Informe de Sesión</span>
</div>
""", unsafe_allow_html=True)

# ── Título ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding-top:6px; padding-bottom:4px;">
    <span style="font-size:22px; font-weight:900; color:white;">INFORME DE SESIÓN</span>
    <span style="font-size:22px; font-weight:900; color:#00A8CC;"> · CASI</span>
</div>
""", unsafe_allow_html=True)

# ── FILTROS con popover (menú desplegable con checkboxes) ────────────────────
#
# Regla: vacío = todos
# Cascada: Jugador → Puesto → (MD y Fecha independientes entre sí) → Equipo
#
# Cada filtro es un st.popover — botón que abre panel con checkboxes adentro.
# El label del botón muestra "Todos" o "N seleccionados" según el estado.

def label_filtro(seleccion, fecha_mode=False):
    """Botón compacto: Todos, el valor si hay uno, o N jugadores/fechas/etc."""
    if not seleccion:
        return "Todos ▾"
    if len(seleccion) == 1:
        if fecha_mode:
            DIAS_ES = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
            f = seleccion[0]
            return f"{DIAS_ES[f.weekday()]} {f.day:02d}/{f.month:02d} ▾"
        return f"{seleccion[0]} ▾"
    if fecha_mode:
        return f"{len(seleccion)} fechas ▾"
    return f"{len(seleccion)} selec. ▾"

def borrar_keys(prefix):
    """Resetea a False todos los checkboxes de un filtro dado su prefijo."""
    SUFIJOS_EXCLUIR = ("_todos", "_borrar")
    for k in list(st.session_state.keys()):
        if k.startswith(prefix) and not any(k.endswith(s) for s in SUFIJOS_EXCLUIR):
            if isinstance(st.session_state[k], bool):
                st.session_state[k] = False

def render_filtro_puesto(col_ctx, grupos, prefix, opciones_validas):
    """Filtro de puesto con grupos clicables y puestos individuales."""
    sel = [op for op in sum(grupos.values(), []) if st.session_state.get(f"{prefix}{op}", False)]
    btn_txt = "Todos ▾" if not sel else (f"{sel[0]} ▾" if len(sel)==1 else f"{len(sel)} selec. ▾")

    with col_ctx:
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Puesto</span>', unsafe_allow_html=True)
        with st.popover(btn_txt, use_container_width=True):
            st.button("✓ Todos", key=f"{prefix}todos",
                      use_container_width=True, on_click=borrar_keys, args=(prefix,))
            for grupo, puestos in grupos.items():
                # Solo mostrar grupo si tiene puestos válidos
                puestos_validos = [p for p in puestos if p in opciones_validas]
                if not puestos_validos:
                    continue
                # Encabezado del grupo — al tildar selecciona todos los puestos del grupo
                todos_grupo_sel = all(st.session_state.get(f"{prefix}{p}", False) for p in puestos_validos)
                grupo_check = st.checkbox(
                    grupo.upper(),
                    value=todos_grupo_sel,
                    key=f"{prefix}grupo_{grupo}"
                )
                # Si el estado del grupo cambió, actualizar puestos individuales
                if grupo_check != todos_grupo_sel:
                    for p in puestos_validos:
                        st.session_state[f"{prefix}{p}"] = grupo_check
                    st.rerun()
                # Puestos individuales con indent
                for p in puestos_validos:
                    col_ind, col_chk = st.columns([0.15, 0.85])
                    with col_chk:
                        st.checkbox(p, key=f"{prefix}{p}")

def render_filtro(col_ctx, label, prefix, opciones, fecha_mode=False):
    """Renderiza un filtro con checkboxes y botón Todos dentro de un popover."""
    sel = [op for op in opciones if st.session_state.get(f"{prefix}{op}", False)]
    btn_txt = label_filtro(sel, fecha_mode=fecha_mode)

    with col_ctx:
        st.markdown(f'<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">{label}</span>', unsafe_allow_html=True)
        with st.popover(btn_txt, use_container_width=True):
            st.button("✓ Todos", key=f"{prefix}todos",
                      use_container_width=True,
                      on_click=borrar_keys, args=(prefix,))
            if fecha_mode:
                DIAS_ES  = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
                MESES_ES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
                            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
                mes_actual = None
                for op in opciones:
                    mes_año = (op.year, op.month)
                    if mes_año != mes_actual:
                        mes_actual = mes_año
                        st.markdown(
                            f'<div style="font-size:10px;color:#7a9ab5;text-transform:uppercase;'+
                            f'letter-spacing:1px;margin-top:8px;margin-bottom:2px;">'+
                            f'── {MESES_ES[op.month]} {op.year} ──</div>',
                            unsafe_allow_html=True)
                    dia = DIAS_ES[op.weekday()]
                    fila_md = df_raw[(df_raw["Fecha"] == op) & (df_raw["MD"] == "MD") & (df_raw["Rival"].notna())]
                    rival_str = f" · {fila_md['Rival'].iloc[0]}" if not fila_md.empty else ""
                    st.checkbox(f"{dia} {op.day:02d}/{op.month:02d}{rival_str}", key=f"{prefix}{op}")
            else:
                for op in opciones:
                    st.checkbox(str(op), key=f"{prefix}{op}")

# ── FILTRADO CRUZADO ─────────────────────────────────────────────────────────
# Cada filtro muestra solo las opciones válidas dado el estado de TODOS los
# demás filtros. Para eso, primero leemos los valores actuales del session_state,
# luego calculamos las opciones cruzadas, y finalmente renderizamos los widgets.

# ── Leer valores actuales de session_state (lo que el usuario tildó) ──────────
def get_sel(prefix, opciones_todas):
    """Lee los checkboxes del session_state para un filtro dado."""
    return [op for op in opciones_todas if st.session_state.get(f"{prefix}{op}", False)]

# Opciones base (sin filtrar) para cada dimensión
orden_md      = ["MD+3", "MD+2", "MD-5", "MD-4", "MD-2", "MD", "Pretemporada", "MD+5"]
todas_md      = [m for m in orden_md if m in df_raw["MD"].unique()]
todos_jugadores = sorted(df_raw["Player Name"].dropna().unique().tolist())
todos_puestos   = sorted(df_raw["Position Name"].dropna().unique().tolist())
todas_fechas    = sorted(df_raw["Fecha"].unique(), reverse=True)
todos_equipos   = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw["Equipo"].dropna().unique()] if "Equipo" in df_raw.columns else []

# Leer selección actual
md_sel      = get_sel("md_",  todas_md)
jug_sel     = get_sel("jug_", todos_jugadores)
pue_sel     = get_sel("pue_", todos_puestos)
fec_sel     = get_sel("fec_", todas_fechas)
equ_sel     = get_sel("equ_", todos_equipos)

# Valores activos (vacío = todos)
md_activo   = md_sel   if md_sel   else todas_md
jug_activo  = jug_sel  if jug_sel  else todos_jugadores
pue_activo  = pue_sel  if pue_sel  else todos_puestos
fec_activa  = fec_sel  if fec_sel  else todas_fechas
equ_activo  = equ_sel  if equ_sel  else None  # None = no filtrar

# ── Calcular jugadores válidos por equipo (por semana) ────────────────────────
def jugadores_validos_por_equipo(equ_sel):
    if not equ_sel:
        return None  # None = todos
    md_equipo = df_raw[
        (df_raw["MD"] == "MD") &
        (df_raw["Equipo"].isin(equ_sel))
    ][["Player Name", "Fecha"]].copy()
    md_equipo["Fecha"] = pd.to_datetime(md_equipo["Fecha"])
    md_equipo["SemanaInicio"] = md_equipo["Fecha"] - pd.to_timedelta(md_equipo["Fecha"].dt.weekday, unit="D")
    return md_equipo[["Player Name", "SemanaInicio"]].drop_duplicates()

df_base = df_raw.copy()
df_base["Fecha_dt"] = pd.to_datetime(df_base["Fecha"])
df_base["SemanaInicio"] = df_base["Fecha_dt"] - pd.to_timedelta(df_base["Fecha_dt"].dt.weekday, unit="D")

jug_val = jugadores_validos_por_equipo(equ_sel)
if jug_val is not None:
    df_base = df_base.merge(jug_val, on=["Player Name", "SemanaInicio"], how="inner")

df_base = df_base.drop(columns=["Fecha_dt", "SemanaInicio"])

def filtrar_cruzado(excluir):
    d = df_base.copy()
    if excluir != "md"  and md_activo:  d = d[d["MD"].isin(md_activo)]
    if excluir != "jug" and jug_activo: d = d[d["Player Name"].isin(jug_activo)]
    if excluir != "pue" and pue_activo: d = d[d["Position Name"].isin(pue_activo)]
    if excluir != "fec" and fec_activa: d = d[d["Fecha"].isin(fec_activa)]
    return d

opciones_md      = [m for m in todas_md if m in filtrar_cruzado("md")["MD"].unique()]
opciones_jugador = sorted(filtrar_cruzado("jug")["Player Name"].dropna().unique().tolist())
opciones_puesto  = sorted(filtrar_cruzado("pue")["Position Name"].dropna().unique().tolist())
import datetime
df_fec          = filtrar_cruzado("fec")
opciones_fechas = sorted(df_fec["Fecha"].unique(), reverse=True)
def opciones_equipo_cruzado():
    d = df_raw.copy()
    if md_activo:  d = d[d["MD"].isin(md_activo)]
    if jug_activo: d = d[d["Player Name"].isin(jug_activo)]
    if pue_activo: d = d[d["Position Name"].isin(pue_activo)]
    if fec_activa: d = d[d["Fecha"].isin(fec_activa)]
    return [e for e in ["Primera", "Intermedia", "Pre A"] if e in d["Equipo"].dropna().unique()] if "Equipo" in d.columns else []

opciones_equipo = opciones_equipo_cruzado()

# ── Renderizar filtros ────────────────────────────────────────────────────────
f1, f2, f3, f4, f5 = st.columns(5)

render_filtro(f1, "Jugador",          "jug_", opciones_jugador)
render_filtro_puesto(f2, GRUPOS_PUESTO, "pue_", opciones_puesto)
render_filtro(f3, "Tipo de día (MD)", "md_",  opciones_md)
render_filtro(f4, "Fecha",            "fec_", opciones_fechas, fecha_mode=True)
render_filtro(f5, "Equipo",           "equ_", opciones_equipo)

fecha_activa = fec_sel if fec_sel else opciones_fechas

# ── Botonera sesión completa / solo 1 equipo ────────────────────────────────────
if equ_activo:
    col_btn, _ = st.columns([0.4, 0.6])
    with col_btn:
        modo_equipo = st.radio(
            label="Modo equipo",
            options=["Sesión completa", "Solo 1 equipo"],
            index=0, key="modo_equipo", horizontal=True, label_visibility="collapsed",
        )
else:
    modo_equipo = "Sesión completa"

# ── Aplicar filtro final al df ────────────────────────────────────────────────
if modo_equipo == "Solo 1 equipo" and equ_activo:
    df = df_raw.copy()
    df["Fecha_dt"] = pd.to_datetime(df["Fecha"])
    df["SemanaInicio"] = df["Fecha_dt"] - pd.to_timedelta(df["Fecha_dt"].dt.weekday, unit="D")
    jug_val2 = jugadores_validos_por_equipo(equ_sel)
    if jug_val2 is not None:
        df = df.merge(jug_val2, on=["Player Name", "SemanaInicio"], how="inner")
    df = df[df["Equipo"].isin(equ_activo)]
    df = df.drop(columns=["Fecha_dt", "SemanaInicio"])
else:
    df = df_base.copy()

df = df[df["MD"].isin(md_activo)]
df = df[df["Player Name"].isin(jug_activo)]
df = df[df["Position Name"].isin(pue_activo)]
df = df[df["Fecha"].isin(fecha_activa)]
df = df.copy()

st.markdown("<hr style='border-color:#1e3048; margin:8px 0 16px 0;'>", unsafe_allow_html=True)

# ── Datos de la sesión ────────────────────────────────────────────────────────
df_sesion = df.copy()

# Jugadores que suman >30 min (sobre df completo para sesión completa, sobre equipo para solo 1 equipo)
mins_por_dia = df_sesion.groupby(["Player Name", "Fecha"])["Minutos"].sum().reset_index()
mins_por_dia.columns = ["Player Name", "Fecha", "Minutos_dia"]
df_sesion = df_sesion.merge(mins_por_dia, on=["Player Name", "Fecha"])
df_sesion["bajo_30"] = df_sesion["Minutos_dia"] < 30

# Para promedios: solo los que superan 30 min
df_sesion_ok = df_sesion[~df_sesion["bajo_30"]]

_agg = df_sesion_ok.groupby(["Player Name", "Fecha"]).agg({"Minutos": "sum", **{c: "sum" for c in COLS}}).reset_index()
avg_sesion = _agg[COLS].mean()

st.markdown("<hr style='border-color:#1e3048; margin:8px 0 16px 0;'>", unsafe_allow_html=True)
# ── Datos de la sesión ────────────────────────────────────────────────────────
df_sesion = df.copy()

# Promedio por jugador+fecha para no sobre-ponderar sesiones con más filas
# Replicar DAX: sumar por jugador+fecha, filtrar Minutos > 30, luego promediar
_agg = df_sesion.groupby(["Player Name", "Fecha"]).agg({"Minutos": "sum", **{c: "sum" for c in COLS}}).reset_index()
_agg = _agg[_agg["Minutos"] > 30]
avg_sesion = _agg[COLS].mean()

# ── Barra de resumen de filtros activos ──────────────────────────────────────
DIAS_ES_RES = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]

def fmt_fechas(sel, todas):
    if not sel or set(sel) == set(todas):
        return "Todos"
    if len(sel) == 1:
        f = sel[0]
        return f"{DIAS_ES_RES[f.weekday()]} {f.day:02d}/{f.month:02d}/{f.year}"
    return f"{len(sel)} fechas"

def fmt_lista(sel, todas, fecha_mode=False):
    """Texto detallado: muestra todos los valores seleccionados."""
    if not sel or set(sel) == set(todas):
        return "Todos"
    if fecha_mode:
        DIAS_ES = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
        return ", ".join(f"{DIAS_ES[f.weekday()]} {f.day:02d}/{f.month:02d}/{f.year}" for f in sorted(sel))
    return ", ".join(str(s) for s in sel)

jug_txt  = fmt_lista(jug_sel, todos_jugadores)
# Para puesto: si todos los del grupo están seleccionados, mostrar nombre del grupo
def fmt_puestos(sel, grupos):
    if not sel:
        return "Todos"
    partes = []
    ya_cubiertos = set()
    for grupo, puestos in grupos.items():
        puestos_en_sel = [p for p in puestos if p in sel]
        if puestos_en_sel and set(puestos_en_sel) == set(puestos):
            # Todos los puestos del grupo están seleccionados → mostrar grupo
            partes.append(grupo)
            ya_cubiertos.update(puestos)
        elif puestos_en_sel:
            # Solo algunos puestos del grupo → mostrar individualmente
            for p in puestos_en_sel:
                if p not in ya_cubiertos:
                    partes.append(p)
                    ya_cubiertos.add(p)
    return ", ".join(partes) if partes else "Todos"

pue_txt  = fmt_puestos(pue_sel, GRUPOS_PUESTO)
md_txt   = fmt_lista(md_sel,  todas_md)
fec_txt  = fmt_lista(fec_sel, opciones_fechas, fecha_mode=True)
equ_txt  = fmt_lista(equ_sel, todos_equipos)

# md_label para usar en el header de sección 3
md_label = md_txt

def chip(label, val):
    color = "#00A8CC" if val != "Todos" else "#5a7a90"
    peso  = "700" if val != "Todos" else "400"
    return (f'<span style="font-size:11px; color:#5a7a90;">{label}:</span> '
            f'<span style="font-size:12px; font-weight:{peso}; color:{color};">{val}</span>')

st.markdown(
    f'<div style="margin-bottom:8px; padding:8px 0; display:flex; flex-wrap:wrap; gap:16px; border-bottom:1px solid #1e3048;">'
    f'{chip("Jugador", jug_txt)}'
    f'{chip("Puesto", pue_txt)}'
    f'{chip("MD", md_txt)}'
    f'{chip("Fecha", fec_txt)}'
    f'{chip("Equipo", equ_txt)}'
    f'</div>',
    unsafe_allow_html=True
)

# ── Benchmarks históricos ─────────────────────────────────────────────────────
# Se excluyen las fechas seleccionadas para no contaminar el histórico
# df_hist para benchmark vs partido — respeta filtros de jugador/puesto activos
df_hist = df_raw_full[~df_raw_full["Fecha"].isin(fecha_activa)]

# Benchmark vs partido (MD puro)
# El DAX mantiene el contexto de jugador/puesto si está filtrado
bench_partido = {
    col: calc_bench(df_hist[df_hist["MD"] == "MD"], col)
    for col in COLS
}

# Benchmark vs mismo tipo de sesión (igual MD)
# El DAX hace REMOVEFILTERS de jugador y puesto — usa TODOS los jugadores históricos
# solo filtrando por el tipo de MD. Por eso usamos df_raw_full sin filtros de jugador/puesto.
df_hist_md = df_raw_full[~df_raw_full["Fecha"].isin(fecha_activa)]
bench_md_val = {
    col: calc_bench(df_hist_md[df_hist_md["MD"].isin(md_activo)], col)
    for col in COLS
}

# ── Sección 1: Datos promedio sesión ─────────────────────────────────────────
st.markdown('<div class="seccion-header">📊 Datos promedio sesión</div>', unsafe_allow_html=True)

cols1 = st.columns(8)
for i, col in enumerate(COLS):
    label, unidad, icono = METRICAS[col]
    val = avg_sesion[col]
    with cols1[i]:
        st.markdown(f"""
        <div class="tarjeta-cruda">
            <div class="label">{icono} {label}</div>
            <div class="valor">{fmt(val)}</div>
            <div class="unidad">{unidad}</div>
        </div>""", unsafe_allow_html=True)

# ── Sección 2: Comparativa vs Partido (MD) ───────────────────────────────────
st.markdown('<div class="seccion-header">⚔️ Comparativa vs. Partido (MD)</div>', unsafe_allow_html=True)

cols2 = st.columns(8)
for i, col in enumerate(COLS):
    label, unidad, icono = METRICAS[col]
    val   = avg_sesion[col]
    bench = bench_partido[col]
    pct   = val / bench if bench and not np.isnan(bench) else None
    color = color_pct(pct)
    fondo, borde = fondo_tarjeta(pct)
    pct_num = pct * 100 if pct is not None else None
    # Ícono de advertencia según nivel
    if pct_num is not None and pct_num > 130:
        alerta = ' 🚩'
    elif pct_num is not None and pct_num > 115:
        alerta = ' ⚠️'
    else:
        alerta = ''
    pct_str = f"{pct_num:.0f}%" if pct_num is not None else "—"
    with cols2[i]:
        st.markdown(f"""
        <div class="tarjeta-comp" style="background:{fondo}; border:2px solid {borde};">
            <div class="metrica-label" style="color:{color};">{icono} {label}</div>
            <div class="sub-label">{unidad}</div>
            <div class="pct" style="color:{color};">{pct_str}</div>
            <div class="valores">{fmt(val)} / {fmt(bench)}</div>
            {barra_html(pct, color)}
        </div>""", unsafe_allow_html=True)

# ── Sección 3: Comparativa vs mismo tipo de sesión ───────────────────────────
st.markdown(f'<div class="seccion-header">📅 Comparativa vs. Igual tipo de sesión ({md_label})</div>', unsafe_allow_html=True)

cols3 = st.columns(8)
for i, col in enumerate(COLS):
    label, unidad, icono = METRICAS[col]
    val   = avg_sesion[col]
    bench = bench_md_val[col]
    pct   = val / bench if bench and not np.isnan(bench) else None
    color = color_pct(pct)
    fondo, borde = fondo_tarjeta(pct)
    pct_num = pct * 100 if pct is not None else None
    if pct_num is not None and pct_num > 130:
        alerta = ' 🚩'
    elif pct_num is not None and pct_num > 115:
        alerta = ' ⚠️'
    else:
        alerta = ''
    pct_str = f"{pct_num:.0f}%" if pct_num is not None else "—"
    with cols3[i]:
        st.markdown(f"""
        <div class="tarjeta-comp" style="background:{fondo}; border:2px solid {borde};">
            <div class="metrica-label" style="color:{color};">{icono} {label}</div>
            <div class="sub-label">{unidad}</div>
            <div class="pct" style="color:{color};">{pct_str}</div>
            <div class="valores">{fmt(val)} / {fmt(bench)}</div>
            {barra_html(pct, color)}
        </div>""", unsafe_allow_html=True)

st.divider()

# ── Sección 4: Tabla detalle por jugador ─────────────────────────────────────
st.markdown('<div class="seccion-header">📋 Detalle por jugador</div>', unsafe_allow_html=True)

# Columnas a mostrar en la tabla (igual que Power BI)
COLS_TABLA_INFO = ["Player Name", "Position Name", "Fecha", "Rival", "Equipo", "MD"]
COLS_TABLA_MET  = ["Minutos", "Distancia Total", "AI 18 Km/h", "DT + 25 Km/h",
                   "+25 Km/h #", "Acel 2,5 m/ss #", "Desacel -2,5 m/ss #",
                   "Contact Involvement Total Count Avg"]
NOMBRES_TABLA   = ["Jugador", "Puesto", "Fecha", "Rival", "Equipo", "MD",
                   "Minutos", "Dist Tot (m)", "HSR (m)", "Sprints (m)",
                   "N° Sprints", "N° Acel", "N° Decel", "N° Contactos"]

# Tomar filas reales de la sesión (sin promediar — una fila por jugador por fecha)
cols_disponibles = [c for c in COLS_TABLA_INFO + COLS_TABLA_MET if c in df_sesion.columns]
df_tabla = df_sesion[cols_disponibles].copy()

# Renombrar columnas
rename_map = dict(zip(COLS_TABLA_INFO + COLS_TABLA_MET, NOMBRES_TABLA))
df_tabla = df_tabla.rename(columns=rename_map)

# Redondear métricas numéricas
for c in ["Minutos", "Dist Tot (m)", "HSR (m)", "Sprints (m)", "N° Sprints", "N° Acel", "N° Decel", "N° Contactos"]:
    if c in df_tabla.columns:
        df_tabla[c] = df_tabla[c].round(2)

# Ordenar por Dist Tot descendente
if "Dist Tot (m)" in df_tabla.columns:
    df_tabla = df_tabla.sort_values("Dist Tot (m)", ascending=False)

st.dataframe(
    df_tabla,
    use_container_width=True,
    hide_index=True,
    height=400,
)

st.divider()

# ── Sección 5: Gráficos por métrica ──────────────────────────────────────────
st.markdown('<div class="seccion-header">📊 Detalle por jugador en la sesión</div>', unsafe_allow_html=True)

# Si hay varias fechas elegidas, promediar por jugador
df_det = (
    df_sesion
    .groupby("Player Name")[COLS]
    .mean()
    .reset_index()
    .sort_values("Distancia Total", ascending=True)
)

metricas_items = list(METRICAS.items())
for fila_i in range(0, len(metricas_items), 2):
    cols_graf = st.columns(2)
    for j in range(2):
        idx = fila_i + j
        if idx >= len(metricas_items): break
        col, (label, unidad, icono) = metricas_items[idx]
        with cols_graf[j]:
            nombres   = df_det["Player Name"].tolist()
            valores   = df_det[col].tolist()
            bench_p   = bench_partido[col]
            barcolors = [
                color_pct(v / bench_p if bench_p and not np.isnan(bench_p) else None)
                for v in valores
            ]
            fig = go.Figure(go.Bar(
                x=valores, y=nombres, orientation="h",
                marker_color=barcolors, marker_line_width=0,
                text=[fmt(v) for v in valores],
                textposition="outside",
                textfont=dict(size=9, color="white"),
                cliponaxis=False,
            ))
            if bench_p and not np.isnan(bench_p):
                fig.add_vline(
                    x=bench_p, line_dash="dash",
                    line_color="#00A8CC", line_width=1.5,
                    annotation_text=f"MD: {fmt(bench_p)}",
                    annotation_font_color="#00A8CC",
                    annotation_font_size=9,
                    annotation_position="top",
                )
            fig.update_layout(
                title=dict(text=f"{icono} {label}", font=dict(size=12, color="white"), x=0),
                paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
                height=max(300, len(nombres) * 26),
                margin=dict(t=35, b=10, l=10, r=80),
                xaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=9), zeroline=False),
                yaxis=dict(tickfont=dict(size=9, color="#cce0f0"), showgrid=False),
                showlegend=False, bargap=0.3,
            )
            st.plotly_chart(fig, use_container_width=True)