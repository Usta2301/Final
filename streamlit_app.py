import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import pandas as pd
from datetime import datetime

# Nuevo import:
from streamlit_drawable_canvas import st_canvas

# Aseguramos que events sea siempre lista
if 'events' not in st.session_state or not isinstance(st.session_state.events, list):
    st.session_state.events = []

AUTHORIZED = {"CKN364", "MXL931"}

def process_plate(img: np.ndarray):
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

    # Creamos dos pestañas: subir imagen vs dibujar placa
    tab1, tab2 = st.tabs(["📷 Subir / Cámara", "✏️ Dibujar Placa"])

    with tab1:
        uploaded_file = st.file_uploader("Sube la foto de la placa...", type=["jpg","jpeg","png"])
        use_camera   = st.checkbox("Usar cámara")
        if use_camera:
            pic = st.camera_input("Toma una foto")
            if pic:
                data = np.asarray(bytearray(pic.read()), dtype=np.uint8)
                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                st.image(img, use_container_width=True)
                placa, allowed = process_plate(img)
                if not placa or placa=='N/A':
                    st.error("❌ No se detectó ninguna placa.")
                else:
                    st.write(f"**Placa reconocida:** `{placa}`")
                    st.success("✅ Acceso autorizado.") if allowed else st.error("⛔ Acceso denegado.")
        elif uploaded_file:
            img_pil = Image.open(uploaded_file).convert("RGB")
            img = np.array(img_pil)[:, :, ::-1]
            st.image(img, use_container_width=True)
            placa, allowed = process_plate(img)
            if not placa or placa=='N/A':
                st.error("❌ No se detectó ninguna placa.")
            else:
                st.write(f"**Placa reconocida:** `{placa}`")
                st.success("✅ Acceso autorizado.") if allowed else st.error("⛔ Acceso denegado.")

    with tab2:
        st.markdown("**Dibuja aquí las 3 letras y 3 números de la placa:**")
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",  # transparente
            stroke_width=10,
            stroke_color="#000",
            background_color="#fff",
            height=200,
            width=600,
            drawing_mode="freedraw",
            key="canvas",
        )
        # Cuando el usuario pulse este botón, procesamos lo pintado
        if st.button("▶️ Procesar dibujo"):
            if canvas_result.image_data is not None:
                # canvas_result.image_data es un ndarray RGBA
                rgba = canvas_result.image_data.astype("uint8")
                # Convertimos a BGR para OpenCV (descartamos el canal alfa)
                bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)
                st.image(bgr, caption="Tu dibujo", use_container_width=True)
                placa, allowed = process_plate(bgr)
                if not placa or placa=='N/A':
                    st.error("❌ No se detectó ninguna placa en el dibujo.")
                else:
                    st.write(f"**Placa reconocida:** `{placa}`")
                    st.success("✅ Acceso autorizado.") if allowed else st.error("⛔ Acceso denegado.")
            else:
                st.warning("No hay nada dibujado en el canvas.")

elif page == "Dashboard":
    st.title("📊 Dashboard de Eventos")
    if not st.session_state.events:
        st.info("Aún no se ha procesado ninguna placa.")
    else:
        df = pd.DataFrame(st.session_state.events)
        total = len(df)
        ok    = (df['allowed']=='✅').sum()
        no    = total - ok
        c1, c2, c3 = st.columns(3)
        c1.metric("Total lecturas", total)
        c2.metric("Autorizados", ok)
        c3.metric("Denegados", no)
        st.markdown("---")
        st.subheader("🔍 Log de intentos")
        st.dataframe(df, use_container_width=True)
