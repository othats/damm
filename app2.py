import streamlit as st  # type: ignore
from PIL import Image, ImageDraw  # type: ignore
import random

# Inicializamos las variables en session_state si no existen
if "worker_id" not in st.session_state:
    st.session_state.worker_id = None
if "pasillo" not in st.session_state:
    st.session_state.pasillo = None

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
    st.title("Modo Almacenaje - Inventario de Pallets")
    st.write("Esta sección simula la captura de etiquetas en la zona alta de la estantería.")
    if st.button("Capturar Etiqueta"):
        st.success("Etiqueta capturada. Recuento verificado.")
        try:
            layout_image = Image.open("layout.png")
        except Exception:
            layout_image = Image.new("RGB", (600, 400), color="lightgray")
        # Simulación: Dibujamos un rectángulo en la zona de almacenaje (coordenadas de ejemplo)
        overlay = Image.new("RGBA", layout_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        rect_coords = (100, 100, 300, 200)
        draw.rectangle(rect_coords, outline=(0, 255, 0, 255), width=5)  # Borde verde
        combined = Image.alpha_composite(layout_image.convert("RGBA"), overlay)
        st.image(combined, caption="Zona Almacenaje (Pallets completos)", use_container_width=True)

# Función para Modo Picking (detección con ML)
def modo_picking():
    st.title("Modo Picking - Detección con ML")
    st.write("Captura la imagen de la zona picking con la cámara.")
    # Se utiliza st.camera_input para capturar la imagen (disponible en dispositivos móviles)
    captured_image = st.camera_input("Captura una imagen de la zona picking")
    if captured_image is not None:
        st.info("Procesando imagen...")
        # Simulación: resultados aleatorios del modelo ML
        ml_count = random.randint(1, 20)
        accuracy = random.randint(50, 100)
        st.write(f"ML detectó **{ml_count}** bultos con una precisión del **{accuracy}%**.")
        try:
            picking_image = Image.open(captured_image)
        except Exception:
            picking_image = Image.new("RGB", (600, 400), color="lightgray")
        # Definir umbral de confianza
        confidence_threshold = 70
        if accuracy < confidence_threshold:
            overlay_color = (255, 255, 0, 100)  # Amarillo
            st.warning("La foto no es concluyente, revise manualmente.")
        else:
            overlay_color = (0, 255, 0, 100)  # Verde
            st.success("Conteo correcto según ML.")
        overlay = Image.new("RGBA", picking_image.size, overlay_color)
        combined = Image.alpha_composite(picking_image.convert("RGBA"), overlay)
        st.image(combined, caption="Zona Picking", use_container_width=True)
    else:
        st.info("Esperando captura de imagen...")

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
