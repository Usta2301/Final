import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import paho.mqtt.client as mqtt
import json
from datetime import datetime

st.set_page_config(page_title="Control de Acceso – Unidad Residencial", layout="centered")
st.title("🔒 Control de Acceso Vehicular")
st.markdown("""
En esta simulación sólo se permitirá el paso a dos placas autorizadas.  
> *Autorizadas:* CKN364, MXL931
""")

# Lista de placas permitidas
AUTHORIZED = {"CKN364", "MXL931"}

# Configuración MQTT
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_PORT = 1883
MQTT_TOPIC = "Usta"

def publish_to_mqtt(plate, authorized):
    """Envía información de la placa al broker MQTT"""
    try:
        # Crear cliente MQTT
        client = mqtt.Client()
        
        # Conectar al broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Preparar mensaje
        message = {
            "timestamp": datetime.now().isoformat(),
            "plate": plate,
            "authorized": authorized,
            "status": "Acceso autorizado" if authorized else "Acceso denegado"
        }
        
        # Publicar mensaje
        client.publish(MQTT_TOPIC, json.dumps(message))
        client.disconnect()
        
        st.info(f"📡 Datos enviados al broker MQTT: {MQTT_BROKER}")
        return True
    except Exception as e:
        st.warning(f"⚠ Error al enviar datos MQTT: {str(e)}")
        return False

uploaded_file = st.file_uploader("Sube la foto de la placa...", type=["jpg", "jpeg", "png"])
use_camera = st.checkbox("Usar cámara")

def process_and_display(img):
    st.image(img, caption="Procesando imagen...", use_column_width=True)
    plate = recognize_plate(img)
    
    if not plate:
        st.error("❌ No se detectó ninguna placa.")
        return
    
    st.write(f"*Placa reconocida:* {plate}")
    
    if plate in AUTHORIZED:
        st.success("✅ Acceso autorizado. ¡Bienvenido!")
        # Enviar datos al broker MQTT para placa autorizada
        publish_to_mqtt(plate, True)
    else:
        st.error("⛔ Acceso denegado.")
        # Enviar datos al broker MQTT para placa no autorizada
        publish_to_mqtt(plate, False)

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

# Información MQTT
st.markdown("---")
st.markdown("### 📡 Configuración MQTT")
st.info(f"""
*Broker:* {MQTT_BROKER}  
*Puerto:* {MQTT_PORT}  
*Tópico:* {MQTT_TOPIC}  

Los datos se envían en formato JSON con la siguiente estructura:
json
{
  "timestamp": "2025-05-27T10:30:00",
  "plate": "CKN364",
  "authorized": true,
  "status": "Acceso autorizado"
}

""")

# Enlace al tablero en línea
st.markdown("---")
st.markdown("🌐 También puedes acceder a esta app desde el siguiente enlace desplegado:")
st.link_button("Ir a la app desplegada", "https://tablero-de-dibujo-original-jo2wvrmuypfgyuauc9hepa.streamlit.app")
