import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image

st.set_page_config(page_title="Reconocimiento de Placas", layout="centered")
st.title("📷 Reconocimiento de Placas de Vehículos")

st.markdown(
    """
    Sube una foto de la matrícula o toma una captura desde tu cámara.
    El sistema detectará y extraerá el texto de la placa.
    """
)

uploaded_file = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png"])
use_camera = st.checkbox("Usar cámara (solo navegadores compatibles)")

if use_camera:
    picture = st.camera_input("Toma una foto")
    if picture:
        file_bytes = np.asarray(bytearray(picture.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(img, channels="BGR", caption="Imagen capturada")
        text = recognize_plate(img)
        if text:
            st.success(f"Placa detectada: **{text}**")
        else:
            st.error("No se detectó ninguna placa.")
elif uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)[:, :, ::-1]  # RGB → BGR para OpenCV
    st.image(image, caption="Imagen subida", use_column_width=True)
    text = recognize_plate(img)
    if text:
        st.success(f"Placa detectada: **{text}**")
    else:
        st.error("No se detectó ninguna placa.")
