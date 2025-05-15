import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import pandas as pd
from datetime import datetime

# 1) Inicializa events como LISTA (solo la primera vez)
if 'events' not in st.session_state:
    st.session_state.events = []  # <-- aquí debe ser lista, nunca DataFrame

# Placas autorizadas
AUTHORIZED = {"CKN364", "MXL931"}

def process_plate(img):
    """
    Reconoce placa y devuelve (placa, allowed:bool).
    Además agrega el evento a la lista de la sesión.
    """
    plate = recognize_plate(img)
    allowed = (plate in AUTHORIZED)

    # 2) Append en la LISTA; muta la propia lista
    st.session_state.events.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'placa': plate or 'N/A',
        'allowed': '✅' if allowed else '⛔'
    })

    return plate, allowed

# Sidebar de navegación
st.sidebar.title("🔎 Navegación")
page = st.sidebar.selectbox("", ["Control de Acceso", "Dashboard"])

if page == "Control de Acceso":
    st.title("🔒 Control de Acceso Vehicular")

    uploaded_file = st.file_uploader("Sube la foto de la placa...", type=["jpg","jpeg","png"])
    use_camera = st.checkbox("Usar cámara")

    def run_check(img):
        st.image(img, use_container_width=True)
        placa, allowed = process_plate(img)
        if not placa or placa == 'N/A':
            st.error("❌ No se detectó ninguna placa.")
        else:
            st.write(f"**Placa reconocida:** `{placa}`")
            if allowed:
                st.success("✅ Acceso autorizado.")
            else:
                st.error("⛔ Acceso denegado.")

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

elif page == "Dashboard":
    st.title("📊 Dashboard de Eventos")

    if not st.session_state.events:
        st.info("Aún no se ha procesado ninguna placa.")
    else:
        # 3) Convertimos la LISTA en DataFrame solo para mostrar
        df = pd.DataFrame(st.session_state.events)

        total = len(df)
        ok = (df['allowed'] == '✅').sum()
        no = total - ok

        col1, col2, col3 = st.columns(3)
        col1.metric("Total lecturas", total)
        col2.metric("Autorizados", ok)
        col3.metric("Denegados", no)

        st.markdown("---")
        st.subheader("🔍 Log de intentos")
        st.dataframe(df, use_container_width=True)
