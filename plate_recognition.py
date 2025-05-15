import cv2
import numpy as np
import easyocr

# Inicializa el lector de EasyOCR (idioma español e inglés)
reader = easyocr.Reader(['es', 'en'])

def recognize_plate(image: np.ndarray) -> str:
    """
    Detecta y reconoce la matrícula en una imagen.
    Devuelve el texto de la placa (u '' si no se detecta nada).
    """
    # Conversión a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Filtro bilateral para reducir ruido pero conservar bordes
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    # Detección de bordes
    edged = cv2.Canny(filtered, 30, 200)

    # Encuentra contornos y los ordena de mayor a menor área
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

    plate_img = None
    for cnt in cnts:
        # Aproximación poligonal
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.018 * peri, True)
        # Buscamos un cuadrilátero
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            plate_img = image[y:y + h, x:x + w]
            break

    if plate_img is None:
        return ""

    # Reconocimiento OCR con EasyOCR
    result = reader.readtext(plate_img, detail=0)
    # Unimos en string limpio
    plate_text = "".join(result).replace(" ", "")
    return plate_text
