import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# --- SOLUCIÓN DE LIBRERÍAS ---
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    try:
        from st_gsheets_connection import GSheetsConnection
    except ImportError:
        st.error("Instala la librería: pip install st-gsheets-connection")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BOCANNADA CLUB SOCIAL", layout="wide", page_icon="🌿")

# --- CONFIGURACIÓN DE DATOS ---
# IMPORTANTE: PEGA TU LINK AQUÍ ABAJO
URL_SHEET = "https://docs.google.com/spreadsheets/d/1ZSGn2uPcSrbaCGVIbfYK-GTZX_HtUzWagpLjq7jxfO8/edit?gid=0#gid=0"

SECTORES_FLORA = ["FLORA BOCANNADA 1", "FLORA BOCANNADA 2", "FLORA HYDROTEK", "FLORA SUSTRATO"]
SECTORES_VEGE = ["VEGE RDWC 8x1", "CARPA MADRES", "ESQUEJERA"]
TODOS_LOS_SECTORES = SECTORES_FLORA + SECTORES_VEGE
FILAS = ["FILA 1", "FILA 2", "FILA 3", "FILA 4", "FILA 5"]
COLUMNAS = ["A", "B", "C", "D", "E", "F", "G", "H"]

# --- FUNCIONES ---
def calcular_vpd(t_amb, hum):
    vpsat = 0.61078 * np.exp((17.27 * t_amb) / (t_amb + 237.3))
    vpair = vpsat * (hum / 100)
    return round(vpsat - vpair, 2)

def estilo_esquejera(val):
    if val != "":
        return 'background-color: #1b5e20; color: white; font-weight: bold; text-align: center;'
    return 'background-color: #f1f1f1; color: #9e9e9e; text-align: center;'

# --- CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de conexión: {e}")

# --- DISEÑO DE INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🍃 BOCANNADA CLUB SOCIAL 🍃</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🏠 Panel de Control")
    usuario = st.text_input("Operador:", value="Mauricio")
    sala_sel = st.radio("SALA ACTUAL:", ["Floración", "Vegetación"])
    st.divider()
    st.caption("BOCANNADA v11.0 - Sincronizado")

tab1, tab2, tab3 = st.tabs(["📊 Registro Diario", "📜 Historial en la Nube", "🧬 Mapa de Esquejera"])

# --- TAB 1: REGISTRO ---
with tab1:
    col_izq, col_der = st.columns([1.3, 2])
    
    with col_izq:
        lista_sectores = SECTORES_FLORA if sala_sel == "Floración" else SECTORES_VEGE
        sector_sel = st.selectbox("Seleccionar Sector:", lista_sectores)
        es_sustrato = "SUSTRATO" in sector_sel or "MADRES" in sector_sel
        
        with st.form("registro_bocannada"):
            st.subheader(f"📍 {sector_sel}")
            ph = st.number_input("PH Medido", value=6.2 if es_sustrato else 5.8, step=0.1)
            ec = st.number_input("EC Medida", value=1.4, step=0.1)
            
            if es_sustrato:
                maceta = st.selectbox("Maceta (L)", [3, 7, 10, 15, 20])
                riego = st.number_input("Riego (L/planta)", value=1.0)
                t_agua, orp = 0.0, 0
            else:
                t_agua = st.number_input("T° Agua", value=20.0)
                orp = st.number_input("ORP (mV)", value=250)
                maceta, riego = 0, 0.0
            
            t_amb = st.slider("T° Ambiente", 15.0, 35.0, 24.0)
            hum = st.slider("Humedad %", 30, 90, 55)
            notas = st.text_area("Observaciones")
            
            if st.form_submit_button("🚀 GUARDAR EN LA NUBE"):
                vpd = calcular_vpd(t_amb, hum)
                
                # Leer historial actual
                df_actual = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
                
                # Crear nueva fila
                nueva_fila = pd.DataFrame([{
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "usuario": usuario,
                    "sector": sector_sel,
                    "ph": ph,
                    "ec": ec,
                    "vpd": vpd,
                    "t_amb": t_amb,
                    "hum": hum,
                    "maceta": maceta,
                    "riego": riego,
                    "t_agua": t_agua,
                    "orp": orp,
                    "notas": notas
                }])
                
                # Concatenar y Subir
                df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                conn.update(spreadsheet=URL_SHEET, worksheet="historial", data=df_final)
                
                st.success("✅ ¡Datos guardados en Bocannada-DB!")
                st.balloons()

    with col_der:
        st.info("💡 **Dato del cultivador:** El VPD ideal para floración avanzada es de 1.2 a 1.5 kPa.")
        if not es_sustrato:
            st.warning("⚠️ Mantén la temperatura del agua bajo 22°C para evitar Pythium.")

# --- TAB 2: HISTORIAL ---
with tab2:
    st.subheader("📋 Últimos registros sincronizados")
    try:
        df_h = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
        st.dataframe(df_h.sort_values(by=df_h.columns[0], ascending=False), use_container_width=True)
    except:
        st.error("Asegúrate de que la pestaña 'historial' exista en tu Google Sheet.")

# --- TAB 3: ESQUEJERA ---
with tab3:
    st.subheader("🧬 Mapa de Clones 5x8")
    try:
        df_esq = conn.read(spreadsheet=URL_SHEET, worksheet="esquejera")
        grid = df_esq.pivot(index='Fila', columns='Col', values='Genetica').reindex(index=FILAS, columns=COLUMNAS).fillna("")
        st.table(grid.style.applymap(estilo_esquejera))
    except:
        st.warning("Crea una pestaña llamada 'esquejera' con columnas 'Fila', 'Col' y 'Genetica'.")
