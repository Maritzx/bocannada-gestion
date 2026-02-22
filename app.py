import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- BLOQUE DE IMPORTACIÓN ANTI-ERROR ---
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    try:
        from st_gsheets_connection import GSheetsConnection
    except ImportError:
        st.error("⚠️ Error: No se encuentra la librería 'st-gsheets-connection'.")
        st.info("Asegúrate de que aparezca en tu archivo requirements.txt en GitHub.")
        st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BOCANNADA CLUB", layout="wide")

# --- ENLACE A TU PLANILLA ---
# Reemplaza con tu link real de Google Sheets
URL_SHEET = "TU_LINK_DE_GOOGLE_SHEETS_AQUI"

st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🍃 BOCANNADA CLUB SOCIAL 🍃</h1>", unsafe_allow_html=True)

# --- CONEXIÓN ---
try:
    # Usamos st.cache_resource para que la conexión no se reinicie a cada rato
    @st.cache_resource
    def get_connection():
        return st.connection("gsheets", type=GSheetsConnection)

    conn = get_connection()
    st.success("✅ Sistema conectado a la Nube")
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# --- FORMULARIO DE PRUEBA ---
with st.form("test_registro"):
    st.subheader("🚀 Prueba de envío")
    ph = st.number_input("PH", value=6.5)
    notas = st.text_input("Nota de prueba", value="Test Bocannada")
    enviar = st.form_submit_button("GUARDAR DATOS")

if enviar:
    try:
        # Intentar leer primero
        df_previo = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
        
        # Crear nueva fila
        nuevo_df = pd.DataFrame([{
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "ph": ph,
            "notas": notas
        }])
        
        # Unir y actualizar
        df_final = pd.concat([df_previo, nuevo_df], ignore_index=True)
        conn.update(spreadsheet=URL_SHEET, worksheet="historial", data=df_final)
        
        st.balloons()
        st.success("¡Datos guardados con éxito en Google Sheets!")
    except Exception as e:
        st.error(f"Error al escribir en la planilla: {e}")

