import streamlit as st #type: ignore
from PIL import Image, ImageDraw #type: ignore
import random

# ------------------ CONFIGURACIÓN INICIAL ------------------
st.title("Recuento de Inventario")
st.write("Por favor, identifícate para comenzar.")


# Paso 1: Identificación del trabajador
worker_id = st.text_input("Ingrese su ID de trabajador:")

if worker_id:
    st.success(f"Bienvenido {worker_id}!")
    
    # Paso 2: Asignación del pasillo
    # Lista de pasillos disponibles
    pasillos = ["400", "410", "420", "430", "440", "450", "460", 
                "600", "620", "630", "660", "680", "690", "700"]
    
    # Diccionario con datos de cada pasillo (coordenadas y recuento teórico)
    # Las coordenadas son de ejemplo: (x, y, ancho, alto)
    zonas = {
        "400": {"coordinates": (180, 470, 87, 44), "theoretical_count": 10},
        "410": {"coordinates": (283, 470, 582, 44), "theoretical_count": 2977},
        "420": {"coordinates": (255, 300, 804, 128), "theoretical_count": 90},
        "430": {"coordinates": (950, 75, 290, 204), "theoretical_count": 80},
        "440": {"coordinates": (255, 210, 804, 112), "theoretical_count": 110},
        "450": {"coordinates": (255, 105, 720, 58), "theoretical_count": 95},
        "460": {"coordinates": (255, 75, 718, 44), "theoretical_count": 105},
        "600": {"coordinates": (1045, 430, 995, 510), "theoretical_count": 115},
        "620": {"coordinates": (1130, 370, 367, 72), "theoretical_count": 85},
        "630": {"coordinates": (1525, 370, 450, 72), "theoretical_count": 90},
        "660": {"coordinates": (1130, 312, 377, 72), "theoretical_count": 100},
        "680": {"coordinates": (1130, 250, 377, 67), "theoretical_count": 130},
        "690": {"coordinates": (1520, 255, 461, 67), "theoretical_count": 75},
        "700": {"coordinates": (1222, 175, 711, 84), "theoretical_count": 100},
    }
    
    # Permitir selección manual o asignación automática del pasillo
    asignacion_manual = st.checkbox("Seleccionar pasillo manualmente")
    if asignacion_manual:
        pasillo_asignado = st.selectbox("Seleccione su pasillo", pasillos)
    else:
        pasillo_asignado = "620"
        st.info(f"Se te ha asignado automáticamente el pasillo: **{pasillo_asignado}**")
    
    info_zona = zonas[pasillo_asignado]
    
    # Paso 3: Visualización del layout con zoom sobre la zona asignada
    st.subheader("Layout del almacén")
    try:
        # Cargar imagen del layout (ajusta la ruta y nombre según corresponda)
        layout_image = Image.open("layout.png")
        st.image(layout_image, caption="Layout completo del almacén", use_container_width=True)
        
        # Extraer zona: (x, y, ancho, alto) según el pasillo asignado
        x, y, w, h = info_zona["coordinates"]
        zona_zoom = layout_image.crop((x, y, x+w, y+h))
        
        st.image(zona_zoom, caption=f"Zoom: Pasillo {pasillo_asignado}", use_container_width=True)
    except Exception as e:
        st.error("No se encontró la imagen del layout. Asegúrate de tener 'layout.png' en la carpeta.")
    
    # Paso 4: Recuento y estado visual con overlay semitransparente
    st.subheader("Recuento de productos")
    st.write(f"La cantidad teórica para el pasillo {pasillo_asignado} es: **{info_zona['theoretical_count']}**")
    
    # Entrada para el recuento manual (se simula el conteo)
    actual_count = st.number_input("Ingrese la cantidad contada en el pasillo:", min_value=0, step=1)
    
    # Entrada para simular la confianza de la detección de la foto (0-100%)
    confidence = st.slider("Confianza en la detección de la foto (%)", min_value=0, max_value=100, value=100)
    
    # Umbral de confianza para considerar la foto concluyente
    confidence_threshold = 70
    
    # Decisión sobre el color del overlay y el mensaje:
    if actual_count > 0:
        if actual_count != info_zona["theoretical_count"]:
            overlay_color = (255, 0, 0, 100)  # Rojo con transparencia
            status_msg = "La cantidad no coincide. Revisión manual sugerida."
        else:
            if confidence < confidence_threshold:
                overlay_color = (255, 255, 0, 100)  # Amarillo con transparencia
                status_msg = "La foto no es concluyente, verifique manualmente."
            else:
                overlay_color = (0, 255, 0, 100)  # Verde con transparencia
                status_msg = "La cantidad es correcta."
    else:
        overlay_color = (128, 128, 128, 100)  # Gris, esperando recuento
        status_msg = "Esperando recuento..."
    
    st.write(status_msg)
    
    # Crear overlay semitransparente sobre la zona del zoom
    try:
        zona_zoom_rgba = zona_zoom.convert("RGBA")
        overlay = Image.new("RGBA", zona_zoom_rgba.size, overlay_color)
        zona_con_estado = Image.alpha_composite(zona_zoom_rgba, overlay)
        
        # Se muestra la imagen con overlay en lugar de la imagen original de la zona
        st.image(zona_con_estado, caption=f"Estado del pasillo {pasillo_asignado}", use_container_width=True)
    except Exception as e:
        st.error("Error al aplicar el indicador visual en la imagen.")