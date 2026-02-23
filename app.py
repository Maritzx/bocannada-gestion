import streamlit as st
import pandas as pd
from datetime import datetime

# --- IMPORTACIÓN ---
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    from st_gsheets_connection import GSheetsConnection

st.set_page_config(page_title="BOCANNADA DB", layout="wide")

# --- LINK LIMPIO ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1ZSGn2uPcSrbaCGVIbfYK-GTZX_HtUzWagpLjq7jxfO8/edit"

st.title("🍃 BOCANNADA CLUB SOCIAL")

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("registro"):
    ph = st.number_input("PH", value=6.0)
    ec = st.number_input("EC", value=1.4)
    notas = st.text_input("Notas", value="Prueba")
    if st.form_submit_button("GUARDAR EN NUBE"):
        try:
            # Intentar leer; si falla (porque está vacío), crear estructura
            try:
                df_previo = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
            except:
                df_previo = pd.DataFrame(columns=["fecha", "ph", "ec", "notas"])
            
            # Nuevo registro
            nuevo = pd.DataFrame([{"fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "ph": ph, "ec": ec, "notas": notas}])
            
            # Concatenar y subir
            df_final = pd.concat([df_previo, nuevo], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, worksheet="historial", data=df_final)
            
            st.balloons()
            st.success("¡Anclado en Bocannada-DB!")
        except Exception as e:
            st.error(f"Error: {e}")

# Mostrar tabla abajo
try:
    df_ver = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
    st.dataframe(df_ver)
except:
    st.info("Esperando primer registro...")
