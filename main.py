from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

# --- 1. INICIALIZACIÓN DE LA API ---
app = FastAPI(title="API de Inteligencia Automotriz", version="1.0")

# --- 2. CARGA DE MODELOS EN MEMORIA (Al arrancar el servidor) ---
print("Cargando modelos de Machine Learning...")
try:
    modelo_clasificacion = joblib.load('Modelos/modelo_clasificacion.pkl')
    modelo_regresion = joblib.load('Modelos/modelo_regresion.pkl')
    modelo_clustering = joblib.load('Modelos/modelo_clustering.pkl')
    scaler = joblib.load('Modelos/scaler.pkl')
    columnas_modelo = joblib.load('Modelos/columnas_modelo.pkl')
    print("✅ Todos los modelos cargados correctamente.")
except Exception as e:
    print(f"❌ Error al cargar los modelos: {e}")

# Diccionario de perfilado para el Clustering
nombres_clusters = {
    0: "Económicos Citadinos",
    1: "SUVs y Vehículos Pesados",
    2: "Gama Media Estándar",
    3: "Deportivos Premium"
}

# --- 3. DEFINICIÓN DEL ESQUEMA DE ENTRADA (Pydantic) ---
class AutoInput(BaseModel):
    # En lugar de tipiar 60 variables, le pedimos al usuario que envíe 
    # un diccionario con las características. Luego lo validaremos.
    caracteristicas: dict


@app.get("/")
def home():
    return {
        "estado": "En línea", 
        "mensaje": "Bienvenido a la API de Tasación y Segmentación de Vehículos",
        "modelos_cargados": 4
    }


# --- ENDPOINT 1 ---
@app.post("/analizar_vehiculo")
def analizar_vehiculo(auto: AutoInput):
    try:
        # 1. Convertimos el JSON que llega de la web a una tabla de Pandas (1 sola fila)
        df_input = pd.DataFrame([auto.caracteristicas])

        # 2. Alineación de Columnas (El guardián de seguridad)
        # Esto asegura que si el usuario manda pocas variables, Pandas rellene el resto con ceros 
        # (vital para las variables "One-Hot" de las marcas que no se seleccionaron).
        # También asegura que el orden sea exactamente el que espera el modelo.
        df_input = pd.get_dummies(df_input)
        df_input = df_input.reindex(columns=columnas_modelo, fill_value=0)

        # 3. Transformación Matemática (Usamos tu scaler.pkl)
        datos_escalados = scaler.transform(df_input)

        # 4. Inferencia: ¡Consultamos a los 3 cerebros!
        # A. Clasificador (0 o 1)
        pred_clas_raw = modelo_clasificacion.predict(datos_escalados)[0]
        gama = "Gama Alta / Premium" if pred_clas_raw == 1 else "Gama Estándar / Baja"

        # B. Regresor (Precio exacto)
        pred_precio_raw = modelo_regresion.predict(datos_escalados)[0]

        # C. Clustering (El segmento)
        pred_cluster_raw = modelo_clustering.predict(datos_escalados)[0]
        # Usamos el diccionario que armamos ayer para traducir el número a texto
        segmento = nombres_clusters.get(int(pred_cluster_raw), "Desconocido")

        # 5. Empaquetamos la respuesta para el cliente final
        return {
            "estado": "éxito",
            "diagnostico": {
                "segmento_estrategico": segmento,
                "clasificacion_mercado": gama,
                "precio_sugerido_usd": round(float(pred_precio_raw), 2)
            }
        }
        
    except Exception as e:
        # Si alguien manda un dato que rompe la matemática, atajamos el error
        raise HTTPException(status_code=400, detail=f"Error al procesar los datos: {str(e)}")
    

# --- ENDPOINT 2: DETECTOR DE OPORTUNIDADES ---
class AutoGangaInput(BaseModel):
    caracteristicas: dict
    precio_publicado: float  # ¡El nuevo dato que le pedimos al usuario!


@app.post("/detectar_ganga")
def detectar_ganga(oferta: AutoGangaInput):
    try:
        # 1. Preparamos los datos igual que antes
        df_input = pd.DataFrame([oferta.caracteristicas])
        df_input = pd.get_dummies(df_input)
        df_input = df_input.reindex(columns=columnas_modelo, fill_value=0)
        datos_escalados = scaler.transform(df_input)

        # 2. Consultamos al oráculo (Solo nos importa el precio esta vez)
        precio_justo = modelo_regresion.predict(datos_escalados)[0]
        
        # 3. Lógica de Negocio (¿Es una ganga?)
        diferencia = precio_justo - oferta.precio_publicado
        
        if diferencia > 2000:
            decision = "🔥 EXCELENTE OPORTUNIDAD: Comprar de inmediato. Margen de ganancia alto."
        elif diferencia > 0:
            decision = "✅ BUEN PRECIO: Ligeramente por debajo del mercado. Considerar compra."
        elif diferencia > -1500:
            decision = "⚠️ PRECIO JUSTO/ALTO: Negociar a la baja antes de comprar."
        else:
            decision = "❌ SOBREVALORADO: No comprar. Riesgo de pérdida."

        return {
            "estado": "éxito",
            "analisis_financiero": {
                "tasacion_usd": round(precio_justo, 2),
                "precio_vendedor_usd": oferta.precio_publicado,
                "margen_diferencia_usd": round(diferencia, 2),
                "recomendacion_comercial": decision
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")