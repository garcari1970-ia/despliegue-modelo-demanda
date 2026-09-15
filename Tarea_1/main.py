import os
import sys

# 1. Agregamos la ruta absoluta de esta carpeta a sys.path ANTES de importar esquema
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from contextlib import asynccontextmanager
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

# 2. Ahora Python encuentra esquema.py sin importar desde dónde ejecutes Uvicorn
from esquema import Cliente, RespuestaPrediccion

NOMBRE_BUNDLE = "modelo_churn.joblib"

estado_servicio = {"bundle": None}

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ruta_bundle = os.path.join(DIRECTORIO_ACTUAL, NOMBRE_BUNDLE)
        estado_servicio["bundle"] = joblib.load(ruta_bundle)
        print("Bundle cargado correctamente")
    except Exception as e:
        print(f"Error al cargar el bundle: {e}")
    yield
    estado_servicio["bundle"] = None

app = FastAPI(
    title="API de Predicción de Cancelación (Churn)",
    description="Recibe datos de un cliente y predice el riesgo de cancelación del servicio",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def estado():
    return {
        "servicio": "API de predicción de cancelación de clientes",
        "modelo_cargado": estado_servicio["bundle"] is not None
    }

@app.post("/predecir", response_model=RespuestaPrediccion)
def predecir(cliente: Cliente):
    bundle = estado_servicio["bundle"]

    if bundle is None:
        raise HTTPException(status_code=503, detail="El modelo aun no está cargado")

    fila = cliente.model_dump()
    X_nuevo = pd.DataFrame([fila])

    modelo = bundle["modelo"]
    probabilidad = float(modelo.predict_proba(X_nuevo)[0, 1])

    umbral = bundle.get("umbral", 0.5)
    prediccion_texto = "cancela" if probabilidad >= umbral else "sigue activo"

    if probabilidad < 0.35:
        nivel_riesgo = "bajo"
    elif probabilidad < 0.65:
        nivel_riesgo = "medio"
    else:
        nivel_riesgo = "alto"

    return RespuestaPrediccion(
        probabilidad_cancelacion=round(probabilidad, 4),
        prediccion=prediccion_texto,
        nivel_riesgo=nivel_riesgo,
        umbral_usado=umbral
    )