import streamlit as st  # type: ignore
from PIL import Image, ImageDraw  # type: ignore
import random
import pandas as pd # type: ignore
import altair as alt # type: ignore

# Inicializamos las variables en session_state si no existen
if "worker_id" not in st.session_state:
    st.session_state.worker_id = None
if "pasillo" not in st.session_state:
    st.session_state.pasillo = None

zonas = {
    "400": {"coordinates": (180, 470, 87, 44), "value": 10},
    "410": {"coordinates": (283, 470, 582, 44), "value": 2977},
    "420": {"coordinates": (255, 300, 804, 128), "value": 15912},
    "430": {"coordinates": (950, 75, 290, 204), "value": 1748},
    "440": {"coordinates": (255, 210, 804, 112), "value": 10904},
    "450": {"coordinates": (255, 105, 720, 58), "value": 3761},
    "460": {"coordinates": (255, 75, 718, 44), "value": 9643},
    "600": {"coordinates": (1045, 430, 995, 510), "value": 22904},
    "620": {"coordinates": (1130, 370, 367, 72), "value": 7185},
    "630": {"coordinates": (1525, 370, 450, 72), "value": 11458},
    "660": {"coordinates": (1130, 312, 377, 72), "value": 21958},
    "680": {"coordinates": (1130, 250, 377, 67), "value": 32999},
    "690": {"coordinates": (1520, 255, 461, 67), "value": 95508},
    "700": {"coordinates": (1222, 175, 711, 84), "value": 11877},
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
    opcion = st.sidebar.radio("Elige una opción", ["Modo Almacenaje", "Modo Picking", "Dashboard"])
    st.write(f"Trabajador: {st.session_state.worker_id} | Pasillo asignado: {st.session_state.pasillo}")
    if opcion == "Modo Almacenaje":
        modo_almacenaje()
    elif opcion == "Modo Picking":
        modo_picking()
    elif opcion == "Dashboard":
        dashboard()

# Función para Modo Almacenaje (inventario de pallets)
def modo_almacenaje():
    st.title("Inventario de Pallets")

    pasillo_asignado = st.session_state.pasillo
    info_zona = zonas[pasillo_asignado]
    theoretical_stock = info_zona["value"]

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

    theoretical_stock = info_zona["value"]
    
    captured_image = st.camera_input("")
    if captured_image is None:
       
        image1 = Image.open("images/picking.jpg")
        image2 = Image.open("images/picking2.jpg")

        if st.button("Tomar foto"):

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
def dashboard():
    st.title("Dashboard")
    st.subheader("Stock total por pasillo")
    
    # Intentar leer el Excel
    try:
        df = pd.read_excel("Lx02.XLSX")
    except Exception as e:
        st.error("Error al leer Lx02.XLSX: " + str(e))
        return

    # Extraer el pasillo de la columna "Ubicación"
    # Por ejemplo, "400-001-10" se convierte en "400"
    df["Pasillo"] = df["Ubicación"].astype(str).str.split("-").str[0]

    # Agrupar por pasillo y sumar el stock disponible
    stock_by_pasillo = df.groupby("Pasillo")["Stock disponible"].sum().reset_index()
    stock_by_pasillo = stock_by_pasillo[stock_by_pasillo["Stock disponible"] >= 0]
    stock_by_pasillo = stock_by_pasillo[stock_by_pasillo["Pasillo"].str.isdigit()]


    st.write("Stock total por pasillo:")
    st.dataframe(stock_by_pasillo)


    

    # Crear gráfico de barras con Altair
    chart = alt.Chart(stock_by_pasillo).mark_bar().encode(
        x=alt.X("Pasillo:O", title="Pasillo"),
        y=alt.Y("Stock disponible:Q", title="Stock total"),
        tooltip=["Pasillo", "Stock disponible"]
    ).properties(
        width=400,
        height=300,
        title="Stock total por pasillo"
    )

    st.altair_chart(chart, use_container_width=True)


    heatmap_layout()

    st.subheader("Detalles por Pasillo")
    pasillo_list = sorted(stock_by_pasillo["Pasillo"].unique())
    selected_pasillo = st.selectbox("Selecciona un pasillo para ver detalles:", pasillo_list)
    
    # Filtrar el DataFrame original para el pasillo seleccionado
    df_detail = df[df["Pasillo"] == selected_pasillo][["Material", "Texto breve de material", "Stock disponible", "Ubicación", "Almacén", "Tipo almacén", "Área almacenamiento"]]
    
    # Agrupar por Material y Texto breve de material para evitar repeticiones
    df_detail_grouped = df_detail.groupby(["Material", "Texto breve de material"]).agg({
        "Stock disponible": "sum",
        "Ubicación": lambda x: ", ".join(x.astype(str)),
        "Almacén": "first",
        "Tipo almacén": "first",
        "Área almacenamiento": "first"
    }).reset_index()
    
    st.write(f"Detalle de materiales en el pasillo {selected_pasillo}:")
    st.dataframe(df_detail_grouped)


def heatmap_layout():
    st.write("Mapa de Calor del Almacén")
    
    # Cargar el layout (asegúrate de que layout.png esté en la carpeta)
    try:
        layout_img = Image.open("images/layout.png").convert("RGBA")
    except Exception as e:
        layout_img = Image.new("RGBA", (1600, 800), color="white")
    
    # Crear un overlay transparente del mismo tamaño
    overlay = Image.new("RGBA", layout_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Determinar el máximo y mínimo valor para normalizar la escala
    max_value = max(zona["value"] for zona in zonas.values())
    min_value = min(zona["value"] for zona in zonas.values())
    
    # Recorrer cada zona y dibujar un rectángulo con un color interpolado
    for zona in zonas.values():
        x, y, w, h = zona["coordinates"]
        val = zona["value"]
        # Normalización: ratio entre 0 y 1
        ratio = (val - min_value) / (max_value - min_value) if max_value != min_value else 0.5
        # Interpolación: azul para ratio=0 y rojo para ratio=1
        r = int(255 * ratio)
        g = 0
        b = int(255 * (1 - ratio))
        # Usamos un valor alfa menor (por ejemplo, 50) para mayor transparencia
        fill_color = (r, g, b, 50)
        draw.rectangle([x, y, x+w, y+h], fill=fill_color)
    
    # Combinar overlay con el layout
    heatmap_img = Image.alpha_composite(layout_img, overlay)
    
    st.image(heatmap_img, caption="Mapa de Calor del Almacén", use_container_width=True)




# Lógica principal: Se muestra cada pantalla según el estado almacenado
if st.session_state.worker_id is None:
    login_page()
elif st.session_state.pasillo is None:
    asignacion_pasillo_page()
else:
    main_menu()
