import streamlit as st
import numpy as np
import cv2
from plate_recognition import recognize_plate
from PIL import Image
import pandas as pd
import datetime

st.set_page_config(
    page_title="Control de Acceso + Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Configuración general ---
AUTHORIZED = {"CKN364", "MXL931"}

# Inicializa en session_state el DataFrame de eventos
if "events" not in st.session_state:
    st.session_state.events = pd.DataFrame(
        columns=["timestamp", "placa", "resultado"]
    )

# Función principal de proceso
def process_plate(img: np.ndarray):
    plate = recognize_plate(img)
    if not plate:
        resultado = "no_detectada"
    elif plate in AUTHORIZED:
        resultado = "autorizada"
    else:
        resultado = "denegada"

    # Guardamos evento
    st.session_state.events = st.session_state.events.append({
        "timestamp": datetime.datetime.now(),
        "placa": plate or "N/A",
        "resultado": resultado
    }, ignore_index=True)

    return plate, resultado

# --- Sidebar de navegación ---
page = st.sidebar.selectbox("🔍 Navegación", ["Control de Acceso","Tablero Inteligente"])

# --- Página 1: Control de Acceso ---
if page == "Control de Acceso":
    st.title("🔒 Control de Acceso Vehicular")
    st.markdown("""
    Sube o captura la placa, se reconoce y se decide si entra o no.
    """)
    uploaded_file = st.file_uploader("📷 Imagen de la placa", type=["jpg","jpeg","png"])
    use_camera = st.checkbox("Usar cámara")

    img = None
    if use_camera:
        pic = st.camera_input("Toma la foto")
        if pic:
            data = np.asarray(bytearray(pic.read()), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    elif uploaded_file:
        img_pil = Image.open(uploaded_file).convert("RGB")
        img = np.array(img_pil)[:, :, ::-1]

    if img is not None:
        st.image(img, use_container_width=True, caption="Procesando...")
        placa, resultado = process_plate(img)

        if resultado == "no_detectada":
            st.error("❌ No se detectó ninguna placa.")
        elif resultado == "autorizada":
            st.success(f"✅ Placa **{placa}** autorizada. ¡Bienvenido!")
        else:
            st.error(f"⛔ Placa **{placa}** denegada.")
        
# --- Página 2: Tablero Inteligente ---
else:
    st.title("📊 Tablero Inteligente de Accesos")
    df = st.session_state.events

    if df.empty:
        st.info("Aún no hay registros de escaneos. Ve a 'Control de Acceso' para probar.")
    else:
        # Métricas del día
        hoy = df["timestamp"].dt.date == datetime.datetime.now().date()
        total_hoy = hoy.sum()
        auth_hoy = ((df["resultado"]=="autorizada") & hoy).sum()
        den_hoy  = ((df["resultado"]=="denegada") & hoy).sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("🕒 Escaneos hoy", total_hoy)
        col2.metric("✅ Autorizados", auth_hoy)
        col3.metric("⛔ Denegados", den_hoy)

        st.markdown("---")
        st.subheader("🗒️ Registro completo")
        # Mostrar tabla con paginación
        st.dataframe(
            df.sort_values("timestamp", ascending=False)
              .assign(
                  timestamp=lambda d: d["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
              ),
            use_container_width=True,
            height=400
        )
