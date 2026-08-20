import streamlit as st
import base64, os
import pandas as pd

st.set_page_config(
    page_title="CASI - Análisis de rendimiento",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from simular_contactos import simular_contactos

@st.cache_data
def cargar_excel():
    df = pd.read_excel("TOTALES GPS.xlsx")
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
.block-container {{ padding-top: 90px !important; padding-left: 2rem !important; padding-right: 2rem !important; }}
section[data-testid="stSidebar"] {{ background-color: #0f1a28 !important; margin-top: 72px !important; }}
section[data-testid="stSidebar"] span {{ color: white !important; }}
section[data-testid="stSidebar"] p    {{ color: white !important; }}
div[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
section[data-testid="collapsedControl"] {{ display: none !important; }}listo
section[data-testid="collapsedControl"] svg {{ stroke: white !important; }}
</style>

<div class="topbar">
    <div class="topbar-logo">{logo_html}</div>
    <div class="topbar-divider"></div>
    <span class="topbar-club">Club Atlético de San Isidro</span>
    <div class="topbar-divider"></div>
    <span class="topbar-sub">Análisis de rendimiento</span>
    <div class="topbar-divider"></div>
    <span class="topbar-page">Dashboard</span>
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


st.markdown("""
<h1 style="color:white; font-size:26px; font-weight:900; margin-bottom:8px;">
    Bienvenido al sistema de análisis GPS
</h1>
<p style="color:#7a9ab5; font-size:14px;">
    Seleccioná una sección en el menú de la izquierda para comenzar.
</p>
""", unsafe_allow_html=True)