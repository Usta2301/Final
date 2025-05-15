import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import pandas as pd
from datetime import datetime

# ------------------------------------------------
# Aseguramos que events sea siempre una LISTA
if 'events' not in st.session_state or not isinstance(st.session_state.events, list):
    st.session_state.events = []
# ------------------------------------------------

AUTHORIZED = {"CKN364", "MXL931"}

def process_plate(img):
    plate = recognize_plate(img)
    allowed = (plate in AUTHORIZED)
    st.session_state.events.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'placa': plate or 'N/A',
        'allowed': '✅' if allowed else '⛔'
    })
    return plate, allowed

st.sidebar.title("🔎 Navegación")
page = st.sidebar.selectbox("", ["Control de Acceso", "Dashboard"])

if page == "Control de Acceso":
    st.title("🔒 Control de Acceso Vehicular")
    uploaded_file = st.file_uploader("Sube la foto de la placa...", type=["jpg","jpeg","png"])
    use_camera = st.checkbox("Usar cámara")
    def run_check(img):
        st.image(img, use_container_width=True)
        placa, allowed = process_plate(img)
        if placa in (None, '', 'N/A'):
            st.error("❌ No se detectó ninguna placa.")
        else:
            st.write(f"**Placa reconocida:** `{placa}`")
            st.success("✅ Acceso autorizado.") if allowed else st.error("⛔ Acceso denegado.")
    if use_camera:
        pic = st.camera_input("Toma una foto")
        if pic:
            data = np.asarray(bytearray(pic.read()), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            run_check(img)
    elif uploaded_file:
        img_pil = Image.open(uploaded_file).convert("RGB")
        img = np.array(img_pil)[:, :, ::-1]
        run_check(img)

else:  # Dashboard
    st.title("📊 Dashboard de Eventos")
    if not st.session_state.events:
        st.info("Aún no se ha procesado ninguna placa.")
    else:
        df = pd.DataFrame(st.session_state.events)
        total = len(df)
        ok = (df['allowed']=='✅').sum()
        no = total - ok
        c1, c2, c3 = st.columns(3)
        c1.metric("Total lecturas", total)
        c2.metric("Autorizados", ok)
        c3.metric("Denegados", no)
        st.markdown("---")
        st.subheader("🔍 Log de intentos")
        st.dataframe(df, use_container_width=True)
