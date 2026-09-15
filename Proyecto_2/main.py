from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from inferencia import pronosticar
# 1. Importamos la clase de respuesta junto a la de solicitud
from esquema import SolicitudPronostico, RespuestaPronostico

# Ruta del bundle, donde se encuentra alojada
NOMBRE_BUNDLE = "modelo_demanda.joblib"

estado_servicio = {"bundle": None}

# Carga el bundle antes de la API
@asynccontextmanager
async def lifespan(app: FastAPI):
    estado_servicio["bundle"] = joblib.load(NOMBRE_BUNDLE)
    print("Bundle cargado correctamente")
    yield
    estado_servicio["bundle"] = None

# Configuración de la API
app = FastAPI(
    title="API - Servicio de Pronostico Demanda",
    description="Pronostico de demanda por un Forecast",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def estado():
    return {
        "servicio": "API - Servicio de Prediccion de demanda",
        "modelo_cargado": estado_servicio["bundle"] is not None
    }

# 2. Agregamos response_model para que Swagger UI dibuje el esquema en Responses (200)
@app.post("/predecir", response_model=RespuestaPronostico)
def predecir(datos: SolicitudPronostico):
    
    store = datos.store
    item = datos.item
    horizonte = datos.horizonte
    registros = datos.historial

    historial = pd.DataFrame(
        {
            "date": pd.to_datetime([r.fecha for r in registros]),
            "store": store,
            "item": item,
            "sales": [r.unidades for r in registros]
        }
    )
     
    bundle = estado_servicio["bundle"]
    
    pronostico = pronosticar(bundle, historial, horizonte)

    return {
        "store": store,
        "item": item,
        "pronostico": pronostico
    }
