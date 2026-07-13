import streamlit as st
import math
st.set_page_config(page_title="Control de Acarreo", layout="wide")
st.title("Sistema de Control de Acarreo por Andarivel ")
st.markdown("Simulador web para estimación de ciclos operativos y seguridad.")
if 'viajes' not in st.session_state:
    st.session_state.viajes = 0
if 'toneladas' not in st.session_state:
    st.session_state.toneladas = 0.0
if 'tiempo_total' not in st.session_state:
    st.session_state.tiempo_total = 0.0
LIMITE_CARGA_KG = 1500
PESO_TARA_KG = 250
G = 9.81
FRICCION = 0.05
EFICIENCIA_MOTOR = 0.85
with st.sidebar:
    st.header(" Configuración de Mina")
    distancia = st.number_input("Longitud del cable (m)", min_value=50.0, value=400.0, step=10.0)
    angulo_grados = st.slider("Pendiente (grados)", min_value=5.0, max_value=45.0, value=20.0)
    potencia_hp = st.number_input("Potencia del motor (HP)", min_value=10.0, value=25.0, step=5.0)
    st.markdown("---")
    if st.button(" Reiniciar Guardia (Borrar Datos)"):
        st.session_state.viajes = 0
        st.session_state.toneladas = 0.0
        st.session_state.tiempo_total = 0.0
        st.rerun()
st.subheader("Registrar Nuevo Viaje")
col1, col2 = st.columns([2, 1])
with col1:
    carga_mineral = st.number_input("Peso del mineral a cargar (kg)", min_value=0.0, value=1000.0, step=50.0)
with col2:
    ejecutar_viaje = st.button(" Iniciar Ciclo de Acarreo", use_container_width=True)
if ejecutar_viaje:
    carga_total = carga_mineral + PESO_TARA_KG
    if carga_total > LIMITE_CARGA_KG:
        st.error(f" **ALERTA CRÍTICA:** Carga total ({carga_total} kg) supera el límite estructural ({LIMITE_CARGA_KG} kg). **VIAJE BLOQUEADO.**")
    elif carga_mineral == 0:
        st.warning(" El vagón no puede bajar vacío.")
    else:
        angulo_rad = math.radians(angulo_grados)
        potencia_watts = potencia_hp * 745.7 * EFICIENCIA_MOTOR
        aceleracion = G * (math.sin(angulo_rad) - FRICCION * math.cos(angulo_rad))
        if aceleracion <= 0:
            st.error(" La pendiente es muy plana para vencer la fricción de las poleas. El vagón no se mueve.")
        else:
            tiempo_bajada_seg = math.sqrt((2 * distancia) / aceleracion)
            fuerza_traccion = PESO_TARA_KG * G * (math.sin(angulo_rad) + FRICCION * math.cos(angulo_rad))
            velocidad_subida = potencia_watts / fuerza_traccion
            tiempo_subida_seg = distancia / velocidad_subida
            tiempos_muertos = 1.5
            tiempo_ciclo_min = (tiempo_bajada_seg / 60) + (tiempo_subida_seg / 60) + tiempos_muertos
            toneladas_movidas = carga_mineral / 1000
            st.session_state.viajes += 1
            st.session_state.toneladas += toneladas_movidas
            st.session_state.tiempo_total += tiempo_ciclo_min
            st.success(f" **Viaje N° {st.session_state.viajes} completado con éxito.**")
st.markdown("---")
st.subheader(" Reporte de Guardia Acumulado")
rendimiento_hora = 0.0
if st.session_state.tiempo_total > 0:
    rendimiento_hora = (st.session_state.toneladas / st.session_state.tiempo_total) * 60
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Viajes Completados", value=st.session_state.viajes)
m2.metric(label="Mineral Acumulado", value=f"{st.session_state.toneladas:.2f} Ton")
m3.metric(label="Tiempo Operativo", value=f"{st.session_state.tiempo_total:.2f} min")
m4.metric(label="Productividad", value=f"{rendimiento_hora:.2f} Ton/h")

