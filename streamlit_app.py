import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import paho.mqtt.client as mqtt

# Configuración MQTT
BROKER = "157.230.214.127"
PORT = 1883
TOPIC = "residencial/acceso"

client = mqtt.Client()
client.connect(BROKER, PORT, keepalive=60)
# client.loop_start()  # opcional si quieres callbacks

st.set_page_config(page_title="Control de Acceso – Unidad Residencial", layout="centered")
st.title("🔒 Control de Acceso Vehicular")
st.markdown("_En esta simulación enviarás la autorización vía MQTT al hardware._")

AUTHORIZED = {"CKN364", "MXL931"}

def publish_access(allowed: bool):
    """Publica '1' si allowed=True, '0' si False."""
    payload = "1" if allowed else "0"
    client.publish(TOPIC, payload)

def process_and_display(img):
    st.image(img, caption="Procesando imagen...", use_container_width=True)
    plate = recognize_plate(img)
    if not plate:
        st.error("❌ No se detectó ninguna placa.")
        return

    st.write(f"**Placa reconocida:** `{plate}`")
    allowed = plate in AUTHORIZED
    if allowed:
        st.success("✅ Acceso autorizado. ¡Bienvenido!")
    else:
        st.error("⛔ Acceso denegado.")
    # aquí enviamos al broker
    publish_access(allowed)

uploaded_file = st.file_uploader("Sube la foto de la placa...", type=["jpg","jpeg","png"])
use_camera = st.checkbox("Usar cámara")

if use_camera:
    pic = st.camera_input("Toma una foto")
    if pic:
        data = np.asarray(bytearray(pic.read()), dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        process_and_display(img)
elif uploaded_file:
    img_pil = Image.open(uploaded_file).convert("RGB")
    img = np.array(img_pil)[:, :, ::-1]
    process_and_display(img)
