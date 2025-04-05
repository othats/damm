import streamlit as st  # type: ignore
from PIL import Image, ImageDraw  # type: ignore
import random

# Inicializamos las variables en session_state si no existen
if "worker_id" not in st.session_state:
    st.session_state.worker_id = None
if "pasillo" not in st.session_state:
    st.session_state.pasillo = None

zonas = {
    "400": {"coordinates": (180, 470, 87, 44), "theoretical_count": 10},
    "410": {"coordinates": (283, 470, 582, 44), "theoretical_count": 2977},
    "420": {"coordinates": (255, 300, 804, 128), "theoretical_count": 15912},
    "430": {"coordinates": (950, 75, 290, 204), "theoretical_count": 1748},
    "440": {"coordinates": (255, 210, 804, 112), "theoretical_count": 10904},
    "450": {"coordinates": (255, 105, 720, 58), "theoretical_count": 3761},
    "460": {"coordinates": (255, 75, 718, 44), "theoretical_count": 9643},
    "600": {"coordinates": (1045, 430, 995, 510), "theoretical_count": 22904},
    "620": {"coordinates": (1130, 370, 367, 72), "theoretical_count": 7185},
    "630": {"coordinates": (1525, 370, 450, 72), "theoretical_count": 11458},
    "660": {"coordinates": (1130, 312, 377, 72), "theoretical_count": 21958},
    "680": {"coordinates": (1130, 250, 377, 67), "theoretical_count": 32999},
    "690": {"coordinates": (1520, 255, 461, 67), "theoretical_count": 95508},
    "700": {"coordinates": (1222, 175, 711, 84), "theoretical_count": 11877},
}

labels = ["label.jpg", "label2.jpg", "label3.jpg", "label4.jpg", "label5.jpg", "label6.jpg", "label7.jpg"]

# Función para la pantalla de Login
def login_page():
    st.title("Inicio de Sesión")
    worker_id = st.text_input("Ingresa tu ID de trabajador:")
    if st.button("Iniciar sesión"):
        if worker_id.strip() != "":
            st.session_state.worker_id = worker_id.strip()
        else:
            st.error("Debes ingresar un ID válido.")

# Función para la pantalla de Asignación de Pasillo
def asignacion_pasillo_page():
    st.title("Asignación de Pasillo")
    st.write(f"Bienvenido, {st.session_state.worker_id}!")
    pasillos = ["400", "410", "420", "430", "440", "450", "460", 
                "600", "620", "630", "660", "680", "690", "700"]
    seleccion_manual = st.checkbox("Seleccionar pasillo manualmente")
    if seleccion_manual:
        pasillo_asignado = st.selectbox("Seleccione su pasillo", pasillos)
    else:
        pasillo_asignado = random.choice(pasillos)
        st.info(f"Se te ha asignado automáticamente el pasillo: {pasillo_asignado}")

    layout_image = Image.open("images/layout.png")

    overlay = Image.new("RGBA", layout_image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    x, y, w, h = zonas[pasillo_asignado]["coordinates"]
    draw.rectangle([x, y, x + w, y + h], fill=(255, 182, 193, 100))
    zona_con_estado = Image.alpha_composite(layout_image, overlay)
    st.image(zona_con_estado, caption=f"Estado del pasillo {pasillo_asignado}", use_container_width=True)
    
    if st.button("Confirmar asignación"):
        st.session_state.pasillo = pasillo_asignado
        

# Función para el Menú Principal
def main_menu():
    st.sidebar.title("Menú")
    opcion = st.sidebar.radio("Elige una opción", ["Modo Almacenaje", "Modo Picking", "Dashboard Final"])
    st.write(f"Trabajador: {st.session_state.worker_id} | Pasillo asignado: {st.session_state.pasillo}")
    if opcion == "Modo Almacenaje":
        modo_almacenaje()
    elif opcion == "Modo Picking":
        modo_picking()
    elif opcion == "Dashboard Final":
        dashboard_final()

# Función para Modo Almacenaje (inventario de pallets)
def modo_almacenaje():
    st.title("Inventario de Pallets")

    pasillo_asignado = st.session_state.pasillo
    info_zona = zonas[pasillo_asignado]
    theoretical_stock = info_zona["theoretical_count"]

    if "scanned_total" not in st.session_state:
        st.session_state.scanned_total = 0
    if "scan_count" not in st.session_state:
        st.session_state.scan_count = 0

    
    # Cargar el layout completo y extraer la zona correspondiente
    try:
        layout_image = Image.open("images/layout.png")
    except Exception:
        layout_image = Image.new("RGB", (1600, 800), color="lightgray")
    
    # Extraer el área de interés según las coordenadas de la zona
    x, y, w, h = info_zona["coordinates"]
    zona_zoom = layout_image.crop((x, y, x+w, y+h))
    
    #if st.button("Capturar Etiqueta"):
    if st.button("Escanear etiqueta"):

        lab = random.choice(labels)

        label_image = Image.open(f"labels/{lab}")

        

        if st.session_state.scan_count < 3:
            scanned_value = theoretical_stock // 4  # División entera para evitar decimales
        else:
            # En el séptimo escaneo, se suma la diferencia restante
            scanned_value = theoretical_stock - st.session_state.scanned_total
            
        st.write(f"**Valor leído:** {scanned_value} unidades")
            
        st.session_state.scanned_total += scanned_value
        st.session_state.scan_count += 1

        if st.session_state.scanned_total == theoretical_stock:
            st.success("¡Stock total verificado correctamente!")
        elif st.session_state.scanned_total > theoretical_stock:
            st.error("El total escaneado supera el stock teórico. Revisión necesaria.")
        else:
            st.info("Aún falta escanear más etiquetas para alcanzar el stock teórico.")
            
        # Decisión sobre el color del overlay y mensaje según la comparación
        if st.session_state.scanned_total == theoretical_stock:
            overlay_color = (0, 255, 0, 100)  # Verde
        else: #st.session_state.scanned_total > theoretical_stock:
            overlay_color = (255, 0, 0, 100)  # Rojo
        

    
        zona_zoom_rgba = zona_zoom.convert("RGBA")
        overlay = Image.new("RGBA", zona_zoom_rgba.size, overlay_color)
        zona_con_estado = Image.alpha_composite(zona_zoom_rgba, overlay)
        #st.image(zona_con_estado, caption=f"Estado del pasillo {pasillo_asignado}", use_container_width=True)
        
        col1, col2 = st.columns([3, 7])
        with col1:
            layout_vertical = label_image.rotate(270, expand=True)
            st.image(layout_vertical, use_container_width=True)
        with col2:
            st.image(zona_con_estado, caption=f"Estado de escaneo en el pasillo {pasillo_asignado}", use_container_width=True)

        # Mostrar la barra de progreso
        progress_percentage = st.session_state.scanned_total / theoretical_stock
        progress_value = min(int(progress_percentage * 100), 100)
        st.progress(progress_value)
        st.write(f"Avance: {st.session_state.scanned_total} / {theoretical_stock} unidades")



# Función para Modo Picking (detección con ML)
def modo_picking():
    st.title("Detección automática")

    pasillo_asignado = st.session_state.pasillo

    info_zona = zonas[pasillo_asignado]

    theoretical_stock = info_zona["theoretical_count"]
    
    captured_image = st.camera_input("")
    if captured_image is None:
       
        image1 = Image.open("images/picking.jpg")
        image2 = Image.open("images/picking2.jpg")

        col1, col2 = st.columns(2)

        with col1:
            layout_vertical = image1.rotate(270, expand=True)
            st.image(layout_vertical, caption="Original", use_container_width=True)
        with col2:
            st.image(image2, caption="Detección cantidades", use_container_width=True)

        if st.session_state.scan_count < 3:
            scanned_value = theoretical_stock // 4  # División entera para evitar decimales
        else:
            # En el séptimo escaneo, se suma la diferencia restante
            scanned_value = theoretical_stock - st.session_state.scanned_total
            
        st.write(f"**Valor leído:** {scanned_value} unidades")
            
        st.session_state.scanned_total += scanned_value
        st.session_state.scan_count += 1

        if st.session_state.scanned_total == theoretical_stock:
            st.success("¡Stock total verificado correctamente!")
        elif st.session_state.scanned_total > theoretical_stock:
            st.error("El total escaneado supera el stock teórico. Revisión necesaria.")
        else:
            st.info("Aún falta escanear más etiquetas para alcanzar el stock teórico.")

        # Mostrar la barra de progreso
        progress_percentage = st.session_state.scanned_total / theoretical_stock
        progress_value = min(int(progress_percentage * 100), 100)
        st.progress(progress_value)
        st.write(f"Avance: {st.session_state.scanned_total} / {theoretical_stock} unidades")

# Función para el Dashboard Final
def dashboard_final():
    st.title("Dashboard Final")
    st.write("Resumen consolidado del inventario:")
    st.write("- Modo Almacenaje: Recuento correcto (etiquetas escaneadas).")
    st.write("- Modo Picking: Recuento verificado por ML (con posibilidad de revisión manual).")
    st.info("Aquí se mostrarían gráficos y alertas basados en los recuentos.")

# Lógica principal: Se muestra cada pantalla según el estado almacenado
if st.session_state.worker_id is None:
    login_page()
elif st.session_state.pasillo is None:
    asignacion_pasillo_page()
else:
    main_menu()
