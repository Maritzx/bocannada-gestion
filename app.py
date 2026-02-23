import streamlit as st
import pandas as pd
from datetime import datetime

# Usamos la conexión estándar de Streamlit
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="BOCANNADA DB", layout="wide")
URL_SHEET = "https://docs.google.com/spreadsheets/d/1ZSGn2uPcSrbaCGVIbfYK-GTZX_HtUzWagpLjq7jxfO8/edit"

st.title("🍃 BOCANNADA CLUB SOCIAL")

# Inicializamos la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULARIO ---
with st.form("registro"):
    ph = st.number_input("PH", value=6.0)
    ec = st.number_input("EC", value=1.4)
    notas = st.text_input("Notas", value="Prueba")
    
    if st.form_submit_button("GUARDAR EN NUBE"):
        try:
            # LEER
            df_actual = conn.read(spreadsheet=URL_SHEET, worksheet="historial")
            
            # AGREGAR
            nuevo = pd.DataFrame([{
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "ph": ph, 
                "ec": ec, 
                "notas": notas
            }])
            df_final = pd.concat([df_actual, nuevo], ignore_index=True)
            
            # ESCRIBIR (Aquí es donde Google pide la cuenta de servicio)
            # Si sigue fallando, es porque necesitamos habilitar la cuenta de servicio sí o sí.
            conn.update(spreadsheet=URL_SHEET, worksheet="historial", data=df_final)
            
            st.balloons()
            st.success("¡Datos guardados!")
        except Exception as e:
            st.error("Google requiere una 'Cuenta de Servicio' para escribir.")
            st.info("Para solucionar esto sin código, ve a Google Cloud y desactiva la política que vimos antes.")

