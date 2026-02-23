import streamlit as st
import pandas as pd
from datetime import datetime

# Importación básica
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="BOCANNADA DB", layout="wide")

st.title("🍃 BOCANNADA CLUB SOCIAL")

# URL de tu planilla
URL_SHEET = "https://docs.google.com/spreadsheets/d/1ZSGn2uPcSrbaCGVIbfYK-GTZX_HtUzWagpLjq7jxfO8/edit"

# Conexión SIN pasarle secretos de cuenta de servicio para que no se maree
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("registro"):
    ph = st.number_input("PH", value=6.0, step=0.1)
    ec = st.number_input("EC", value=1.4, step=0.1)
    notas = st.text_input("Notas", value="Prueba")
    
    if st.form_submit_button("🚀 GUARDAR DATOS"):
        try:
            # 1. Leer datos existentes
            df_actual = conn.read(spreadsheet=URL_SHEET, worksheet="historial", ttl=0)
            
            # 2. Crear nueva fila
            nuevo = pd.DataFrame([{
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "ph": ph, 
                "ec": ec, 
                "notas": notas
            }])
            
            # 3. Combinar
            df_final = pd.concat([df_actual, nuevo], ignore_index=True)
            
            # 4. Intentar actualizar
            conn.update(spreadsheet=URL_SHEET, worksheet="historial", data=df_final)
            st.success("¡Datos guardados!")
            st.balloons()
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Si el error dice 'Service Account', es que Google bloqueó el acceso público para escribir.")

# Mostrar tabla
try:
    df_ver = conn.read(spreadsheet=URL_SHEET, worksheet="historial", ttl=0)
    st.dataframe(df_ver, use_container_width=True)
except:
    st.write("Conectando con la planilla...")
