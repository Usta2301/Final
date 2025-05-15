import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import pandas as pd
from datetime import datetime

# 3.1 – Imports para dibujo táctil
from streamlit_drawable_canvas import st_canvas
from tensorflow.keras.models import load_model
from tactil1.model import CLASSES  # lista índice->carácter

# ------------------------------------------------
# Inicialización de sesión
if 'events' not in st.session_state or not isinstance(st.session_state.events, list):
    st.session_state.events = []
# ------------------------------------------------

# 3.2 – Carga el modelo de tactil1 (ajusta ruta/nombre si difiere)
@st.cache_resource
def load_tactil_model():
    return load_model('tactil1/model/my_model.h5')

tactil_model = load_tactil_model()

# Placas autorizadas
AUTHORIZED = {"CKN364", "MXL931"}

def log_event(method, placa, allowed):
    """Añade al log el intento."""
    st.session_state.events.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'método': method,
        'placa': placa or 'N/A',
        'allowed': '✅' if allowed else '⛔'
    })

def infer_tactil(image_bgr):
    """
    Preprocesa el dibujo como en tactil1 y devuelve el caracter predicho.
    Asume image_bgr es un ndarray BGR.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    # En tactil1 usan 28×28, normalize, reshape:
    img28 = cv2.resize(gray, (28,28), interpolation=cv2.INTER_AREA)
    img28 = img28.astype('float32') / 255.0
    x = img28.reshape(1,28,28,1)
    preds = tactil_model.predict(x)
    idx = np.argmax(preds, axis=1)[0]
    return CLASSES[idx]

st.sidebar.title("🔎 Navegación")
page = st.sidebar.selectbox("", ["Control de Acceso", "Dashboard"])

if page == "Control de Acceso":
    st.title("🔒 Control de Acceso Vehicular")

    # Dos métodos: foto/cámara vs dibujo táctil
    tab1, tab2 = st.tabs(["📷 Imagen", "✏️ Dibujo Táctil"])

    # --- MÉTODO 1: OCR fácil con foto/cámara ---
    with tab1:
        uploaded = st.file_uploader("Sube la foto de la placa...", type=["jpg","jpeg","png"])
        use_cam = st.checkbox("Usar cámara")
        img = None
        if use_cam:
            pic = st.camera_input("Toma una foto")
            if pic:
                arr = np.asarray(bytearray(pic.read()), dtype=np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        elif uploaded:
            pil = Image.open(uploaded).convert("RGB")
            img = np.array(pil)[:,:,::-1]

        if img is not None:
            st.image(img, use_container_width=True)
            placa = recognize_plate(img)
            allowed = placa in AUTHORIZED
            log_event("OCR", placa, allowed)
            if not placa:
                st.error("❌ No se detectó placa.")
            else:
                st.write(f"**Placa:** `{placa}`")
                st.success("✅ Autorizado.") if allowed else st.error("⛔ Denegado.")

    # --- MÉTODO 2: DIBUJO TÁCTIL como en tactil1 ---
    with tab2:
        st.markdown("Dibuja las **3 letras + 3 números** de la placa:")
        canvas = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=12,
            stroke_color="#000",
            background_color="#fff",
            width=280, height=280,
            drawing_mode="freedraw",
            key="canvas",
            grid_color="#aaa",
            grid_width=28, grid_height=28
        )
        if st.button("▶️ Procesar Dibujo"):
            if canvas.image_data is not None:
                rgba = canvas.image_data.astype("uint8")
                bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)
                st.image(bgr, width=280)
                # inferencia táctil
                char = infer_tactil(bgr)
                allowed = char in AUTHORIZED
                # formamos placa completa: char aquí será un solo caracter,
                # si quieres permitir dibujar la placa completa, tendrías 
                # que pedir 6 dibujos o una caja de texto adicional.
                log_event("Táctil", char, allowed)
                st.write(f"**Predicción táctil:** `{char}`")
                st.success("✅ Autorizado.") if allowed else st.error("⛔ Denegado.")
            else:
                st.warning("Canvas vacío.")

elif page == "Dashboard":
    st.title("📊 Dashboard de Eventos")
    if not st.session_state.events:
        st.info("Aún no hay eventos.")
    else:
        df = pd.DataFrame(st.session_state.events)
        st.dataframe(df, use_container_width=True)
        total = len(df)
        ok    = (df['allowed']=='✅').sum()
        no    = total - ok
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", total)
        c2.metric("Autorizados", ok)
        c3.metric("Denegados", no)
