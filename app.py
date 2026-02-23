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
st.set_page_config(page_title="BOCANNADA CLUB", layout="wide", page_icon="🌿")

# --- ENLACE A TU PLANILLA (Link Limpio) ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1ZSGn2uPcSrbaCGVIbfYK-GTZX_HtUzWagpLjq7jxfO8/edit"

# --- DISEÑO ---
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🍃 BOCANNADA CLUB SOCIAL 🍃</h1>", unsafe_allow_html=True)

# --- CONEXIÓN ---
try:
    @st.cache_resource
    def get_connection():
        return st.connection("gsheets", type=GSheetsConnection)

    conn = get_connection()
    st.sidebar.success("✅ Sincronizado con la Nube")
except Exception as e:
    st.sidebar.error(f"❌ Error de conexión: {e}")
    st.stop()

# --- INTERFAZ DE USUARIO ---
tab1, tab2 = st.tabs(["📝 Registro", "📋 Ver Historial"])

with tab1:
    with st.form("test_registro"):
        st.subheader("🚀 Carga de Datos")
        ph = st.number_input("PH", value=6.0, step=0.1)
        ec = st.number_input("EC", value=1.4, step=0.1)
        notas = st.text_input("Nota", value="Registro de prueba")
        
        enviar = st.form_submit_button("GUARDAR EN GOOGLE SHEETS")

    if enviar:
        try:
            # 1. Intentar leer la pestaña 'historial'
            df_previo = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
            
            # 2. Crear nueva fila
            nuevo_df = pd.DataFrame([{
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "ph": ph,
                "ec": ec,
                "notas": notas
            }])
            
            # 3. Combinar datos
            df_final = pd.concat([df_previo, nuevo_df], ignore_index=True)
            
            # 4. Actualizar en la nube
            conn.update(spreadsheet=URL_SHEET, worksheet="historial", data=df_final)
            
            st.balloons()
            st.success("✅ ¡Datos guardados correctamente en Bocannada-DB!")
            
        except Exception as e:
            st.error(f"Error al guardar: {e}")
            st.warning("Verifica que la pestaña se llame 'historial' y que el link sea correcto.")

with tab2:
    st.subheader("Registros en tiempo real")
    try:
        # Volver a leer para mostrar los datos más recientes
        df_historial = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
        st.dataframe(df_historial.sort_values(by="fecha", ascending=False), use_container_width=True)
    except:
        st.info("No hay datos para mostrar todavía.")
