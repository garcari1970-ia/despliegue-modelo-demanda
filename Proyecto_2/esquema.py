from datetime import date
from typing import List
from pydantic import BaseModel, Field

# --- ESQUEMAS DE ENTRADA (REQUEST) ---

class RegistroHistorico(BaseModel):
    fecha: date
    unidades: float = Field(ge=0, description="unidades vendidas ese dia, no puede ser negativa")


class SolicitudPronostico(BaseModel):
    store: int = Field(ge=1, le=10, description="el numero de tiendas, del 1 al 10")
    item: int = Field(ge=1, le=50, description="el numero de producto, del 1 al 50")
    historial: List[RegistroHistorico] = Field(
        min_length=28,
        max_length=365,
        description="Historico reciente de la serie. Minimo de 28 registros",
    )
    horizonte: int = Field(default=14, ge=1, le=28, description="Dias a pronosticar, de 1 a 28")


# --- ESQUEMAS DE SALIDA (RESPONSE) ---

class ElementoPrediccion(BaseModel):
    fecha: str = Field(description="Fecha pronosticada YYYY-MM-DD")
    prediccion: float = Field(description="Demanda estimada")


class RespuestaPronostico(BaseModel):
    store: int
    item: int
    pronostico: List[ElementoPrediccion]