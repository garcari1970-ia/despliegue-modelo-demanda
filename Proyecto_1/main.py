from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

#nombre bundle, donde se encuentra alojada
NOMBRE_BUNDLE= "modelo_bundle_e_cardiaca.pkl"

estado_servicio = {"bundle": None}

#carga el bundle antes de la API
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    estado_servicio["bundle"] = joblib.load(NOMBRE_BUNDLE)
    print("Bundle cargado correctamente")
    yield
    estado_servicio["bundle"] = None

#configuracion del API
app = FastAPI(
title="API de Predicción de Enfermedad Cardiaca",
description="Recibe datos clínicos de un paciente y predice el riesgo de cardiopatia coronaria (chd)",
version="1.0.0",
lifespan=lifespan
)

#contruir la clase para las entradas y las salidas de los parametros a predecir en la API
#las llaves deben estar escritas tal cual como las columnas que se usaron para entrenar el modelo
class PacienteInput(BaseModel):
    sbp: int = Field(...,description="Presion arterial sistolica"),
    Tabaco: float = Field(...,description="Tabaco acumulado (kg)"),
    ldl: float = Field(...,description="Colesterol LDL"),
    Adiposidad: float = Field(...,description="Adiposidad"),
    Familia: Literal["Presente",
                     "Ausente"] = Field(
                         ...,description="Antecedentes familiares de enfermedad cardiaca"),
    Tipo: int = Field(...,description="Comportamiento tipo-A"),
    Obesidad: float = Field(...,description="Obesidad"),
    Alcohol: float = Field(...,description="Consumo actual de alcohol"),
    Edad: int = Field(...,description="edad")

#clase para la salida
class PacienteOutput(BaseModel):
    chd_predicho: int
    probabilidad: float
    riesgo: str

#construir el endpoint de verificacion
@app.get("/")
def estado():
    return{
        "servicio":"API de predicción de enfermedad cardíaca",
        "modelo_cargado": estado_servicio["bundle"] is not None
    }

#construir el endpoint de Predecir
@app.post("/predecir",response_model=PacienteOutput)
def predecir(paciente: PacienteInput):

    # validar el modelo
    bundle = estado_servicio["bundle"]

    if bundle is None:
        raise HTTPException(status_code=503,detail="El modelo aun no está cargado")
    
    #convertir a diccionario
    fila = paciente.model_dump()

    #aplicar transformacion de mapeo
    fila["Familia"] = bundle["mapeo_familia"][fila["Familia"]]

    #convertir en dataframe el diccionario
    X_nuevo = pd.DataFrame([fila])[bundle["columnas"]]

    #Predicciones
    prediccion = bundle["pipeline"].predict(X_nuevo)[0]
    probabilidad = bundle["pipeline"].predict_proba(X_nuevo)[0,1]

    # Devolver resultados
    return PacienteOutput(
        chd_predicho=prediccion,
        probabilidad=round(probabilidad,4),
        riesgo="alto" if prediccion == 1 else "bajo"
    )