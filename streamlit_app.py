import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image

st.set_page_config(page_title="Control de Acceso – Unidad Residencial", layout="centered")
st.title("🔒 Control de Acceso Vehicular")

st.markdown("""
_En esta simulación sólo se permitirá el paso a dos placas autorizadas._  
> **Autorizadas:** `CKN364`, `MXL931`
""")

# Lista de placas permitidas
AUTHORIZED = {"CKN364", "MXL931"}

uploaded_file = st.file_uploader("Sube la foto de la placa...", type=["jpg", "jpeg", "png"])
use_camera = st.checkbox("Usar cámara")

def process_and_display(img):
    st.image(img, caption="Procesando imagen...", use_column_width=True)
    plate = recognize_plate(img)
    if not plate:
        st.error("❌ No se detectó ninguna placa.")
        return

    st.write(f"**Placa reconocida:** `{plate}`")
    if plate in AUTHORIZED:
        st.success("✅ Acceso autorizado. ¡Bienvenido!")
    else:
        st.error("⛔ Acceso denegado.")

if use_camera:
    pic = st.camera_input("Toma una foto")
    if pic:
        data = np.asarray(bytearray(pic.read()), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        process_and_display(img)
elif uploaded_file:
    img_pil = Image.open(uploaded_file).convert("RGB")
    img = np.array(img_pil)[:, :, ::-1]  # RGB → BGR
    process_and_display(img)
