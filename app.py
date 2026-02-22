import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BOCANNADA CLUB", layout="wide", page_icon="🌿")

# --- NOMBRES DE ARCHIVOS ---
DB_HISTORIAL = "historial_completo.csv"
DB_CONFIG = "config_sectores.csv"
DB_ESQUEJERA = "mapa_esquejera_grid.csv"

# --- CONFIGURACIÓN DE SECTORES ---
SECTORES_FLORA = ["FLORA BOCANNADA 1", "FLORA BOCANNADA 2", "FLORA HYDROTEK", "FLORA SUSTRATO"]
SECTORES_VEGE = ["VEGE RDWC 8x1", "CARPA MADRES", "ESQUEJERA"]
TODOS_LOS_SECTORES = SECTORES_FLORA + SECTORES_VEGE
FILAS = ["FILA 1", "FILA 2", "FILA 3", "FILA 4", "FILA 5"]
COLUMNAS = ["A", "B", "C", "D", "E", "F", "G", "H"]

# --- FUNCIÓN DE INICIALIZACIÓN SEGURA ---
# Esto evita el error "File does not exist" creando archivos si no los encuentra
def inicializar_archivos():
    if not os.path.exists(DB_CONFIG):
        df = pd.DataFrame({"sector": TODOS_LOS_SECTORES, "fecha_inicio": [str(date.today())] * len(TODOS_LOS_SECTORES)})
        df.to_csv(DB_CONFIG, index=False)
    
    if not os.path.exists(DB_ESQUEJERA):
        data = [{"Fila": f, "Col": c, "Genetica": ""} for f in FILAS for c in COLUMNAS]
        pd.DataFrame(data).to_csv(DB_ESQUEJERA, index=False)
        
    if not os.path.exists(DB_HISTORIAL):
        columnas = ["fecha", "usuario", "sector", "ph", "ec", "vpd", "notas"]
        pd.DataFrame(columns=columnas).to_csv(DB_HISTORIAL, index=False)

inicializar_archivos()

# --- CARGA DE DATOS ---
df_config = pd.read_csv(DB_CONFIG)
df_config['fecha_inicio'] = pd.to_datetime(df_config['fecha_inicio']).dt.date

# --- ESTILOS Y LOGO ---
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🍃 BOCANNADA CLUB SOCIAL 🍃</h1>", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏠 Panel de Control")
    usuario = st.text_input("Operador:", value="Mauricio")
    sala_sel = st.radio("SALA ACTUAL:", ["Floración", "Vegetación"])

# --- CONTENIDO PRINCIPAL ---
tab1, tab2, tab3 = st.tabs(["📊 Panel de Control", "📜 Historial", "⚙️ Configuración"])

with tab1:
    col_izq, col_der = st.columns([1.3, 2])
    with col_izq:
        lista_sectores = SECTORES_FLORA if sala_sel == "Floración" else SECTORES_VEGE
        sector_sel = st.selectbox("Sector:", lista_sectores)
        
        fila_s = df_config[df_config['sector'] == sector_sel]
        if not fila_s.empty:
            sem = ((date.today() - fila_s['fecha_inicio'].values[0]).days // 7) + 1
        else:
            sem = 1
            
        st.metric(f"Semana {sem}", sector_sel)

        with st.form("registro"):
            ph = st.number_input("PH", value=6.0, step=0.1)
            ec = st.number_input("EC", value=1.4, step=0.1)
            notas = st.text_area("Notas")
            if st.form_submit_button("GUARDAR REGISTRO"):
                nuevo = pd.DataFrame([{"fecha": datetime.now().strftime("%Y-%m-%d %H:%M"), "usuario": usuario, "sector": sector_sel, "ph": ph, "ec": ec, "notas": notas}])
                nuevo.to_csv(DB_HISTORIAL, mode='a', header=not os.path.exists(DB_HISTORIAL), index=False)
                st.success("Guardado en la nube temporal")

    with col_der:
        if sector_sel == "ESQUEJERA":
            st.header("📍 Mapa de Esquejera")
            df_esq = pd.read_csv(DB_ESQUEJERA).fillna("")
            grid = df_esq.pivot(index='Fila', columns='Col', values='Genetica').reindex(index=FILAS, columns=COLUMNAS).fillna("")
            st.table(grid.style.applymap(lambda v: 'background-color: #1b5e20; color: white' if v != "" else ''))
        else:
            st.info("💡 Modo de gestión activa.")

with tab2:
    if os.path.exists(DB_HISTORIAL):
        st.dataframe(pd.read_csv(DB_HISTORIAL).sort_values("fecha", ascending=False))

with tab3:
    st.write("Configuración de ciclos y reseteos.")
    