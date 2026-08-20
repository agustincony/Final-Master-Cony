import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64, os

st.set_page_config(page_title="Carga acumulada", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════════════
# ESTILOS
# ══════════════════════════════════════════════════════════════════════════════
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
div[data-testid="stPopoverBody"] {
    background-color: #0f1a28 !important;
    border: 1px solid #1e3048 !important;
    border-radius: 8px !important;
}
div[data-testid="stPopoverBody"] label { color: #cce0f0 !important; font-size: 13px !important; }
div[data-testid="stPopoverBody"] p     { color: #7a9ab5 !important; font-size: 11px !important; }

/* ── Radio buttons estilo segmented control ── */
/* Ocultar el círculo nativo del radio */
div[data-testid="stRadio"] input[type="radio"] {
    display: none !important;
}
div[data-testid="stRadio"] label svg { display: none !important; }
div[data-testid="stRadio"] label > div:first-child { display: none !important; }
div[data-testid="stRadio"] span { display: none !important; }

/* Contenedor horizontal */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 4px !important;
    background-color: #1e3048 !important;
    border: 1px solid #2a4060 !important;
    border-radius: 8px !important;
    padding: 3px !important;
}
/* Cada opción (label) */
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
    transition: background 0.15s ease !important;
}
/* Opción seleccionada: celeste CASI */
div[data-testid="stRadio"] label:has(input:checked) {
    background-color: #00A8CC !important;
    color: #ffffff !important;
}
/* El texto real está dentro de un <p> dentro del label — hay que apuntarlo */
div[data-testid="stRadio"] label p {
    color: #ffffff !important;
}
/* Hover en inactivos */
div[data-testid="stRadio"] label:not(:has(input:checked)):hover {
    color: #00A8CC !important;
}
div[data-testid="stRadio"] label:not(:has(input:checked)):hover p {
    color: #00A8CC !important;
}
/* Ocultar el texto "Semana" que genera st.radio por defecto */
div[data-testid="stRadio"] > label:first-child {
    display: none !important;
}

.seccion-header {
    font-size: 11px; font-weight: 800; letter-spacing: 2px;
    color: #ffffff; background: #0f1a28;
    border-left: 4px solid #00A8CC;
    padding: 8px 14px; margin: 20px 0 10px 0;
    text-transform: uppercase; border-radius: 0 4px 4px 0;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COLUMNAS CALCULADAS (métricas compuestas de Set 2)
# Las tres nuevas métricas se calculan sumando columnas del Excel.
# Las columnas base no se agregan a METRICAS — sí la columna calculada.
# ══════════════════════════════════════════════════════════════════════════════
# Columnas de velocidad Set 2 que componen ">80% vel max"
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

# Nombre de las columnas calculadas que se agregarán al DataFrame
COL_DIST_80 = "Dist >80% Vel Max"
COL_EFF_80  = "# >80% Vel Max"

# ══════════════════════════════════════════════════════════════════════════════
# MÉTRICAS A MOSTRAR  (en el orden visual deseado)
# ══════════════════════════════════════════════════════════════════════════════
# clave            → (etiqueta, unidad, formato, color pastel)
METRICAS = {
    "Distancia Total":                       ("Dist Tot (m)",      "mts",      "int", "#86DC93"),
    "AI 18 Km/h":                            ("HSR (m)",           "mts",      "int", "#F2A8C0"),
    "DT + 25 Km/h":                          ("Sprint (m)",        "mts",      "int", "#C4A8E0"),
    "+25 Km/h #":                            ("N° Sprints",        "cantidad", "int", "#F5C09A"),
    COL_DIST_80:                             ("Dist >80% (m)",     "mts",      "int", "#FFB347"),
    COL_EFF_80:                              ("# >80% vel max",    "cantidad", "int", "#FF8C69"),
    "Acel 2,5 m/ss #":                       ("N° Acel",           "cantidad", "int", "#A8DDB5"),
    "Desacel -2,5 m/ss #":                   ("N° Decel",          "cantidad", "int", "#F0DC96"),
    "Contact Involvement Total Count Avg":   ("N° Contactos",      "cantidad", "int", "#A8E0DC"),
    "Total Player Load":                     ("Player Load",       "u.a.",     "dec", "#B8A8E0"),
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

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def img_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def fmt(val, tipo="int"):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "—"
    if tipo == "int":
        return f"{val:,.0f}"
    return f"{val:.1f}"

# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
def cargar_datos():
    if "df_excel" not in st.session_state:
        st.session_state["df_excel"] = pd.read_excel("TOTALES GPS.xlsx")
    df = st.session_state["df_excel"].copy()
    df = df[
        (df["Period Name"] == "Session") &
        (df["Period Tags"] != "Diferenciado") 
    ].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Position Name"] = df["Position Name"].str.replace(
        "Pilar izquiero", "Pilar izquierdo", regex=False
    )
    df["SemanaInicio"] = df["Fecha"] - pd.to_timedelta(df["Fecha"].dt.weekday, unit="D")
    df[COL_DIST_80] = df[COLS_DIST_80].fillna(0).sum(axis=1)
    df[COL_EFF_80]  = df[COLS_EFF_80].fillna(0).sum(axis=1)
    return df

df_raw = cargar_datos()

# ══════════════════════════════════════════════════════════════════════════════
# CATÁLOGO DE SEMANAS
# ══════════════════════════════════════════════════════════════════════════════
def rival_semana(sem_df):
    md = sem_df[sem_df["MD"] == "MD"]
    rival = None
    if len(md) and pd.notna(md["Rival"].iloc[0]):
        rival = md["Rival"].iloc[0]
    else:
        modos = sem_df["Rival"].dropna().mode()
        if len(modos):
            rival = modos.iloc[0]
    if rival is None or (isinstance(rival, float) and np.isnan(rival)):
        return ""
    return str(rival).replace("Hindú", "Hindu")

@st.cache_data
def tabla_semanas(df):
    semanas_con_datos = sorted(df["SemanaInicio"].unique())
    inicio = pd.Timestamp(semanas_con_datos[0])
    fin    = pd.Timestamp(semanas_con_datos[-1])
    todas_cal      = pd.date_range(inicio, fin, freq="7D")
    num_por_semana = {pd.Timestamp(s): i for i, s in enumerate(todas_cal, start=1)}

    filas = []
    for sem, g in df.groupby("SemanaInicio"):
        sem     = pd.Timestamp(sem)
        n       = num_por_semana.get(sem, 0)
        fin_sem = sem + pd.Timedelta(days=6)
        rival   = rival_semana(g)
        etq = f"S{n} {sem.day:02d}/{sem.month:02d} - {fin_sem.day:02d}/{fin_sem.month:02d}"
        if rival:
            etq += f" {rival}"
        # Etiqueta corta para el eje X del acumulado: número de semana + rival (o fecha)
        etq_corta = f"S{n} {rival}" if rival else f"S{n} {sem.day:02d}/{sem.month:02d}"
        filas.append({
            "SemanaInicio": sem,
            "NumSemana":    n,
            "Etiqueta":     etq,       # etiqueta completa (filtro y hover)
            "EtqCorta":     etq_corta, # etiqueta corta (eje X del acumulado)
            "Rival":        rival,
        })

    return pd.DataFrame(filas).sort_values("SemanaInicio").reset_index(drop=True)

# ══════════════════════════════════════════════════════════════════════════════
# TOPBAR FIJA
# ══════════════════════════════════════════════════════════════════════════════
logo_b64  = img_base64("LOGO_CASI_SIN_FONDO.png")
logo_html = (f'<img src="data:image/png;base64,{logo_b64}" style="height:62px; width:auto;">'
             if logo_b64 else "⚡")

st.markdown(f"""
<style>
.topbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 99999;
    background: #0f1a28; border-bottom: 3px solid #00A8CC; height: 72px;
    display: flex; align-items: center; padding: 0 24px; gap: 16px;
}}
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
    <span class="topbar-page">Carga acumulada</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding-top:6px; padding-bottom:4px;">
    <span style="font-size:22px; font-weight:900; color:white;">CARGA ACUMULADA</span>
    <span style="font-size:22px; font-weight:900; color:#00A8CC;"> · CASI</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FILTROS
# ══════════════════════════════════════════════════════════════════════════════
def borrar_keys(prefix):
    for k in list(st.session_state.keys()):
        if k.startswith(prefix) and not k.endswith(("_todos", "_borrar")):
            if isinstance(st.session_state[k], bool):
                st.session_state[k] = False

def get_sel(prefix, opciones_todas):
    return [op for op in opciones_todas if st.session_state.get(f"{prefix}{op}", False)]

def render_filtro(col_ctx, label, prefix, opciones):
    sel = [op for op in opciones if st.session_state.get(f"{prefix}{op}", False)]
    btn_txt = "Todos ▾" if not sel else (f"{sel[0]} ▾" if len(sel) == 1 else f"{len(sel)} selec. ▾")
    with col_ctx:
        st.markdown(f'<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">{label}</span>', unsafe_allow_html=True)
        with st.popover(btn_txt, use_container_width=True):
            st.button("✓ Todos", key=f"{prefix}todos", use_container_width=True,
                      on_click=borrar_keys, args=(prefix,))
            for op in opciones:
                st.checkbox(str(op), key=f"{prefix}{op}")

def render_filtro_puesto(col_ctx, grupos, prefix, opciones_validas):
    sel = [op for op in sum(grupos.values(), []) if st.session_state.get(f"{prefix}{op}", False)]
    btn_txt = "Todos ▾" if not sel else (f"{sel[0]} ▾" if len(sel) == 1 else f"{len(sel)} selec. ▾")
    with col_ctx:
        st.markdown('<span style="font-size:12px; font-weight:700; color:white; text-transform:uppercase; letter-spacing:1px;">Puesto</span>', unsafe_allow_html=True)
        with st.popover(btn_txt, use_container_width=True):
            st.button("✓ Todos", key=f"{prefix}todos", use_container_width=True,
                      on_click=borrar_keys, args=(prefix,))
            for grupo, puestos in grupos.items():
                puestos_validos = [p for p in puestos if p in opciones_validas]
                if not puestos_validos:
                    continue
                todos_grupo_sel = all(st.session_state.get(f"{prefix}{p}", False) for p in puestos_validos)
                grupo_check = st.checkbox(grupo.upper(), value=todos_grupo_sel, key=f"{prefix}grupo_{grupo}")
                if grupo_check != todos_grupo_sel:
                    for p in puestos_validos:
                        st.session_state[f"{prefix}{p}"] = grupo_check
                    st.rerun()
                for p in puestos_validos:
                    _, col_chk = st.columns([0.15, 0.85])
                    with col_chk:
                        st.checkbox(p, key=f"{prefix}{p}")

# Opciones base
todos_jugadores = sorted(df_raw["Player Name"].dropna().unique().tolist())
todos_puestos   = sorted(df_raw["Position Name"].dropna().unique().tolist())
cat_semanas     = tabla_semanas(df_raw)
todas_etiquetas = cat_semanas["Etiqueta"].tolist()[::-1]

jug_sel = get_sel("jug_", todos_jugadores)
pue_sel = get_sel("pue_", todos_puestos)
sem_sel = get_sel("sem_", todas_etiquetas)

# Inicializar flag de primera visita
if "sem_iniciado" not in st.session_state:
    st.session_state["sem_iniciado"] = False

if not st.session_state["sem_iniciado"] and not sem_sel:
    # Primera vez: seleccionar últimas 5
    ultimas_5 = todas_etiquetas[:5]
    for etq in ultimas_5:
        st.session_state[f"sem_{etq}"] = True
    st.session_state["sem_iniciado"] = True
    st.rerun()

jug_activo = jug_sel if jug_sel else todos_jugadores
pue_activo = pue_sel if pue_sel else todos_puestos
sem_activa = sem_sel if sem_sel else todas_etiquetas

# ── Calcular jugadores válidos por equipo (por semana) ────────────────────────
todos_equipos_ca = [e for e in ["Primera", "Intermedia", "Pre A"] if e in df_raw["Equipo"].dropna().unique()] if "Equipo" in df_raw.columns else []
equ_sel_ca = [e for e in todos_equipos_ca if st.session_state.get(f"equ_ca_{e}", False)]
equ_act_ca = equ_sel_ca if equ_sel_ca else None

def jugadores_validos_por_equipo_ca(equ_sel):
    if not equ_sel:
        return None
    md_equipo = df_raw[
        (df_raw["MD"] == "MD") &
        (df_raw["Equipo"].isin(equ_sel))
    ][["Player Name", "SemanaInicio"]].drop_duplicates()
    return md_equipo

df_base_ca = df_raw.copy()
jug_val_ca = jugadores_validos_por_equipo_ca(equ_act_ca)
if jug_val_ca is not None:
    df_base_ca = df_base_ca.merge(jug_val_ca, on=["Player Name", "SemanaInicio"], how="inner")

def filtrar_cruzado(excluir):
    d = df_base_ca.copy()
    if excluir != "jug" and jug_activo: d = d[d["Player Name"].isin(jug_activo)]
    if excluir != "pue" and pue_activo: d = d[d["Position Name"].isin(pue_activo)]
    return d

opciones_jugador = sorted(filtrar_cruzado("jug")["Player Name"].dropna().unique().tolist())
opciones_puesto  = sorted(filtrar_cruzado("pue")["Position Name"].dropna().unique().tolist())

def opciones_equipo_ca():
    d = df_raw.copy()
    if jug_activo: d = d[d["Player Name"].isin(jug_activo)]
    if pue_activo: d = d[d["Position Name"].isin(pue_activo)]
    return [e for e in ["Primera", "Intermedia", "Pre A"] if e in d["Equipo"].dropna().unique()] if "Equipo" in d.columns else []

f1, f2, f3, f4 = st.columns(4)
render_filtro(f1, "Jugador", "jug_", opciones_jugador)
render_filtro_puesto(f2, GRUPOS_PUESTO, "pue_", opciones_puesto)
render_filtro(f3, "Equipo", "equ_ca_", opciones_equipo_ca())
render_filtro(f4, "Semana", "sem_", todas_etiquetas)

def fmt_lista(sel, todas):
    if not sel or set(sel) == set(todas): return "Todos"
    return ", ".join(str(s) for s in sel)

def chip(label, val):
    color = "#00A8CC" if val != "Todos" else "#5a7a90"
    peso  = "700"    if val != "Todos" else "400"
    return (f'<span style="font-size:11px; color:#5a7a90;">{label}:</span> '
            f'<span style="font-size:12px; font-weight:{peso}; color:{color};">{val}</span>')

st.markdown(
    f'<div style="margin-bottom:8px; padding:8px 0; display:flex; flex-wrap:wrap; gap:16px; border-bottom:1px solid #1e3048;">'
    f'{chip("Jugador", fmt_lista(jug_sel, todos_jugadores))}'
    f'{chip("Puesto",  fmt_lista(pue_sel, todos_puestos))}'
    f'{chip("Equipo",  fmt_lista(equ_sel_ca, todos_equipos_ca))}'
    f'</div>', unsafe_allow_html=True
)
col_lbl, col_radio, col_lbl2, col_radio2, _ = st.columns([0.07, 0.36, 0.07, 0.36, 0.14])

with col_lbl:
    st.markdown(
        '<div style="font-size:12px; font-weight:700; color:white; '
        'text-transform:uppercase; letter-spacing:1px; padding-top:10px;">Semana</div>',
        unsafe_allow_html=True
    )

with col_radio:
    modo_semana = st.radio(
        label="Semana",
        options=["Total", "Sin partido", "Solo partido"],
        index=0, key="modo_semana", horizontal=True, label_visibility="collapsed",
    )


with col_radio2:
    if equ_act_ca:
        modo_equipo_ca = st.radio(
            label="Modo equipo",
            options=["Sesión completa", "Solo 1 equipo"],
            index=0, key="modo_equipo_ca", horizontal=True, label_visibility="collapsed",
        )

if not equ_act_ca:
    modo_equipo_ca = "Sesión completa"

# ══════════════════════════════════════════════════════════════════════════════
# APLICAR FILTRO FINAL
# ══════════════════════════════════════════════════════════════════════════════
if modo_equipo_ca == "Solo 1 equipo" and equ_act_ca:
    df = df_raw.copy()
    df["SemanaInicio"] = pd.to_datetime(df["Fecha"]) - pd.to_timedelta(
        pd.to_datetime(df["Fecha"]).dt.weekday, unit="D"
    )
    jug_val_ca2 = jugadores_validos_por_equipo_ca(equ_act_ca)
    if jug_val_ca2 is not None:
        df = df.merge(jug_val_ca2, on=["Player Name", "SemanaInicio"], how="inner")
    df = df[df["Equipo"].isin(equ_act_ca)]
else:
    df = df_base_ca.copy()

df = df[df["Player Name"].isin(jug_activo)]
df = df[df["Position Name"].isin(pue_activo)]

mapa_etq       = dict(zip(cat_semanas["SemanaInicio"], cat_semanas["Etiqueta"]))
mapa_etq_corta = dict(zip(cat_semanas["SemanaInicio"], cat_semanas["EtqCorta"]))
df["Etiqueta"] = df["SemanaInicio"].map(mapa_etq)
df["EtqCorta"] = df["SemanaInicio"].map(mapa_etq_corta)
df = df[df["Etiqueta"].isin(sem_activa)]

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PREPARAR DATOS
# ══════════════════════════════════════════════════════════════════════════════
md_por_fecha = df.groupby("Fecha")["MD"].agg(
    lambda x: x.mode().iloc[0] if len(x.mode()) else x.iloc[0]
)
rival_por_fecha = (
    df[df["MD"] == "MD"]
    .groupby("Fecha")["Rival"]
    .agg(lambda x: x.dropna().mode().iloc[0] if len(x.dropna()) else "")
)

# Una fila por (semana, fecha) — promedio de jugadores con >30 minutos
MIN_MINUTOS = 30

def promediar_sesion(df_input):
    """Promedia métricas por sesión filtrando jugadores con >30 minutos."""
    mins = df_input.groupby(["SemanaInicio", "Etiqueta", "EtqCorta", "Fecha", "Player Name"])["Minutos"].sum().reset_index()
    jugadores_validos = mins[mins["Minutos"] > MIN_MINUTOS][["SemanaInicio", "Etiqueta", "EtqCorta", "Fecha", "Player Name"]]
    df_filtrado = df_input.merge(jugadores_validos, on=["SemanaInicio", "Etiqueta", "EtqCorta", "Fecha", "Player Name"])

    # Promedio por sesión
    base = (
        df_filtrado.groupby(["SemanaInicio", "Etiqueta", "EtqCorta", "Fecha"])[COLS]
        .mean()
        .reset_index()
        .sort_values("Fecha")
        .reset_index(drop=True)
    )

    return base

detalle_base = promediar_sesion(df)
detalle_base["MD"] = detalle_base["Fecha"].map(md_por_fecha)

# Etiqueta del eje X del detalle: rival en MD, tipo de día en entrenamiento
def etiqueta_dia(row):
    if row["MD"] == "MD":
        rival = rival_por_fecha.get(row["Fecha"], "")
        if rival and not (isinstance(rival, float) and np.isnan(rival)):
            return str(rival).replace("Hindú", "Hindu")
        return "MD"
    return str(row["MD"]) if pd.notna(row["MD"]) else "—"

detalle_base["EtqDia"] = detalle_base.apply(etiqueta_dia, axis=1)

COLOR_MD    = "#00A8CC"
COLOR_ENTRE = "#c9d4de"
detalle_base["color"] = np.where(detalle_base["MD"] == "MD", COLOR_MD, COLOR_ENTRE)

# Filtro de modo semana
if modo_semana == "Sin partido":
    detalle = detalle_base[detalle_base["MD"] != "MD"].copy()
elif modo_semana == "Solo partido":
    detalle = detalle_base[detalle_base["MD"] == "MD"].copy()
else:
    detalle = detalle_base.copy()

# Acumulado semanal: índice numérico en el eje X para evitar fusión de rivales repetidos
acum = (
    detalle
    .groupby(["SemanaInicio", "Etiqueta", "EtqCorta"])[COLS]
    .sum()
    .reset_index()
    .sort_values("SemanaInicio")
    .reset_index(drop=True)
)

# ══════════════════════════════════════════════════════════════════════════════
# RENDER: una fila por métrica → [ acumulado semanal | detalle por sesión ]
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="seccion-header">📊 Acumulado semanal y detalle por sesión</div>', unsafe_allow_html=True)

h_izq, h_der = st.columns([0.42, 0.58])
with h_izq:
    st.markdown('<div style="text-align:center; font-size:13px; font-weight:800; color:#cce0f0; letter-spacing:1px; text-transform:uppercase;">Acumulado por semana</div>', unsafe_allow_html=True)
with h_der:
    st.markdown('<div style="text-align:center; font-size:13px; font-weight:800; color:#cce0f0; letter-spacing:1px; text-transform:uppercase;">Detalle sesión por sesión</div>', unsafe_allow_html=True)

for col in COLS:
    label, unidad, tipo, color_met = METRICAS[col]
    c_izq, c_der = st.columns([0.42, 0.58])

    # ── Izquierda: acumulado semanal ──────────────────────────────────────────
    with c_izq:
        vals      = acum[col].tolist()
        etqs_x    = acum["EtqCorta"].tolist()   # eje X: "S1 Champagnat", "S14 Champagnat" → distintas
        etqs_full = acum["Etiqueta"].tolist()   # hover: etiqueta completa
        fig_a = go.Figure(go.Bar(
            x=list(range(len(vals))),  # índice numérico → barras siempre separadas
            y=vals,
            marker_color=color_met, marker_line_width=0,
            text=[fmt(v, tipo) for v in vals],
            textposition="outside",
            textfont=dict(size=9, color="white"),
            cliponaxis=False,
            customdata=etqs_full,
            hovertemplate="<b>%{customdata}</b><br>%{text}<extra></extra>",
        ))
        fig_a.update_layout(
            title=dict(text=label, font=dict(size=12, color="white"), x=0),
            paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
            height=200,
            margin=dict(t=32, b=60, l=10, r=10),
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(len(vals))),
                ticktext=etqs_x,
                tickfont=dict(color="#7a9ab5", size=8),
                tickangle=-45,
                showgrid=False,
            ),
            yaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=8), zeroline=False),
            showlegend=False, bargap=0.25,
        )
        st.plotly_chart(fig_a, use_container_width=True, key=f"acum_{col}")

        # ── Derecha: detalle por sesión ───────────────────────────────────────────
    with c_der:
        vals_d = detalle[col].tolist()
        lbls_d = detalle["EtqDia"].tolist()
        cols_d = detalle["color"].tolist()
        x_idx  = list(range(len(vals_d)))
        cdata  = list(zip(
            detalle["Etiqueta"].tolist(),
            detalle["MD"].tolist(),
            detalle["EtqDia"].tolist()
        ))

        # Detectar cambios de semana para líneas divisorias
        semanas = detalle["SemanaInicio"].tolist()
        shapes = []
        for i in range(1, len(semanas)):
            if semanas[i] != semanas[i - 1]:
                shapes.append(dict(
                    type="line",
                    x0=i - 0.5, x1=i - 0.5,
                    y0=0, y1=1,
                    yref="paper",
                    line=dict(color="rgba(150,170,190,0.3)", width=1, dash="dot"),
                ))

        fig_d = go.Figure(go.Bar(
            x=x_idx, y=vals_d,
            marker_color=cols_d, marker_line_width=0,
            text=[fmt(v, tipo) for v in vals_d],
            textposition="outside",
            textfont=dict(size=8, color="white"),
            cliponaxis=False,
            customdata=cdata,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]} · %{text}<extra></extra>",
        ))
        fig_d.update_layout(
            title=dict(text=label, font=dict(size=12, color="white"), x=0),
            paper_bgcolor="#0f1a28", plot_bgcolor="#0f1a28",
            height=200,
            margin=dict(t=32, b=50, l=10, r=10),
            xaxis=dict(
                tickmode="array", tickvals=x_idx, ticktext=lbls_d,
                tickfont=dict(color="#7a9ab5", size=8), tickangle=-45, showgrid=False,
            ),
            yaxis=dict(showgrid=True, gridcolor="#1e3048", tickfont=dict(color="#7a9ab5", size=8), zeroline=False),
            showlegend=False, bargap=0.15,
            shapes=shapes,
        )
        st.plotly_chart(fig_d, use_container_width=True, key=f"det_{col}")

# ── Leyenda ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="margin-top:8px; padding:10px 0; border-top:1px solid #1e3048;">'
    f'<div style="font-size:10px; color:#7a9ab5; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Color en el detalle por sesión</div>'
    f'<div style="display:flex; flex-wrap:wrap; gap:20px;">'
    f'<span style="display:inline-flex; align-items:center; gap:6px;">'
    f'<span style="width:12px; height:12px; border-radius:2px; background:{COLOR_MD}; display:inline-block;"></span>'
    f'<span style="font-size:12px; color:#cce0f0;">Día de partido (muestra el rival)</span></span>'
    f'<span style="display:inline-flex; align-items:center; gap:6px;">'
    f'<span style="width:12px; height:12px; border-radius:2px; background:{COLOR_ENTRE}; display:inline-block;"></span>'
    f'<span style="font-size:12px; color:#cce0f0;">Entrenamiento (muestra el tipo: MD+2, MD-2, etc.)</span></span>'
    f'</div></div>',
    unsafe_allow_html=True
)