from typing import Literal
from pydantic import BaseModel, Field

class Cliente(BaseModel):
    antiguedad_meses: int = Field(..., ge=0, description="Meses que lleva como cliente")
    gasto_mensual: float = Field(..., ge=0.0, description="Gasto mensual pagado por el cliente")
    visitas_ultimo_mes: int = Field(..., ge=0, description="Número de visitas en el último mes")
    dias_desde_ultima_visita: int = Field(..., ge=0, description="Días transcurridos desde la última visita")
    tickets_soporte: int = Field(..., ge=0, description="Reclamos/tickets abiertos en el último mes")
    plan: Literal["basico", "estandar", "premium"] = Field(..., description="Tipo de plan contratado")
    metodo_pago: Literal["tarjeta", "transferencia", "efectivo"] = Field(..., description="Método de pago de la suscripción")
    descuento_activo: int = Field(..., ge=0, le=1, description="Indica si posee descuento activo (0 o 1)")

class RespuestaPrediccion(BaseModel):
    probabilidad_cancelacion: float = Field(..., description="Probabilidad estimada de cancelación (0.0 a 1.0)")
    prediccion: str = Field(..., description="'cancela' o 'sigue activo' según el umbral")
    nivel_riesgo: str = Field(..., description="Clasificación de riesgo: 'bajo', 'medio' o 'alto'")
    umbral_usado: float = Field(..., description="Umbral de decisión aplicado")