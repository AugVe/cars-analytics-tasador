import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Cars Analytics", page_icon="🚗")

st.title("🚗 Cars Analytics: Panel de Inteligencia")

# 1. Función con un prefijo para que los IDs sean únicos
def formulario_datos(key_prefix):
    col1, col2 = st.columns(2)
    with col1:
        hp = st.number_input("Caballos de Fuerza (HP)", min_value=50, max_value=500, value=120, key=f"{key_prefix}_hp")
        peso = st.number_input("Peso del auto (lbs)", min_value=1500, max_value=5000, value=2800, key=f"{key_prefix}_peso")
    with col2:
        mpg = st.number_input("Consumo en ruta (MPG)", min_value=10, max_value=60, value=26, key=f"{key_prefix}_mpg")
        size = st.number_input("Tamaño del motor (CC)", min_value=500, max_value=6000, value=1500, key=f"{key_prefix}_size")
    return {"horsepower": hp, "curbweight": peso, "highwaympg": mpg, "enginesize": size}

tab_tasacion, tab_gangas = st.tabs(["📊 Tasar Vehículo", "🕵️ Detectar Gangas"])

# --- PESTAÑA 1: TASAR ---
with tab_tasacion:
    st.header("Tasación Automática")
    datos_tasa = formulario_datos("tasa") # Prefijo único para esta pestaña
    if st.button("Tasar ahora", key="btn_tasa"):
        resp = requests.post(f"{API_URL}/analizar_vehiculo", json={"caracteristicas": datos_tasa})
        
        # --- DEPURACIÓN ---
        st.write("Estado de la respuesta:", resp.status_code)
        st.write("Contenido de la respuesta:", resp.json()) 
        # ------------------
        
        res = resp.json()["diagnostico"]
        st.metric("Precio Sugerido", f"${res['precio_sugerido_usd']:,}")

# --- PESTAÑA 2: GANGAS ---
with tab_gangas:
    st.header("Detector de Oportunidades")
    datos_ganga = formulario_datos("ganga")
    precio_pub = st.number_input("Precio publicado del vendedor", min_value=0, value=25000, key="ganga_precio")
    
    if st.button("Analizar Inversión", key="btn_ganga"):
        datos = {"caracteristicas": datos_ganga, "precio_publicado": precio_pub}
        resp = requests.post(f"{API_URL}/detectar_ganga", json=datos)
        res = resp.json()["analisis_financiero"]
        
        st.divider()
        st.subheader("Análisis de Valor")
        
        # Nueva distribución: tres métricas en una fila
        col1, col2, col3 = st.columns(3)
        col1.metric("Publicado", f"${res['precio_vendedor_usd']:,}")
        col2.metric("Estimado", f"${res['tasacion_usd']:,}")
        col3.metric("Margen", f"${res['margen_diferencia_usd']:,}")
        
        # Mensaje de decisión al final
        st.success(res['recomendacion_comercial'])