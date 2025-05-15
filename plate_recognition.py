import cv2
import numpy as np
import easyocr
import re

# Inicializa el lector de EasyOCR (idioma español e inglés)
reader = easyocr.Reader(['es', 'en'])

def recognize_plate(image: np.ndarray) -> str:
    """
    Detecta y reconoce la matrícula en una imagen.
    Devuelve sólo el patrón LLLDDD (3 letras + 3 dígitos).
    Si no encuentra nada, devuelve cadena vacía.
    """
    # --- Detección de contorno de placa (igual que antes) ---
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(filtered, 30, 200)

    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

    plate_img = None
    for cnt in cnts:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.018 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            plate_img = image[y:y + h, x:x + w]
            break

    if plate_img is None:
        return ""

    # OCR y limpieza básica
    result = reader.readtext(plate_img, detail=0)
    raw = "".join(result)
    cleaned = re.sub(r'[^A-Za-z0-9]', '', raw).upper()

    # Extraer primer match de 3 letras + 3 dígitos
    m = re.search(r'([A-Z]{3}\d{3})', cleaned)
    return m.group(1) if m else ""
