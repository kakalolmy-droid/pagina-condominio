from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal
from app.schemas.apartamento import ApartamentoOut

class ReciboBase(BaseModel):
    apartamento_id: int
    mes_periodo: str  # '2026-09'
    monto_total_usd: Decimal
    fecha_emision: date
    fecha_vencimiento: date

class ReciboCreate(ReciboBase):
    pass

class ReciboOut(ReciboBase):
    id: int
    monto_pendiente_usd: Decimal
    estado_pago: str
    ultimo_pago_estado: Optional[str] = None
    class Config:
        from_attributes = True

class ReciboConApartamento(ReciboOut):
    apartamento: Optional[ApartamentoOut] = None

class EmisionMasivaRequest(BaseModel):
    periodo: str         # '2026-09'
    gasto_total_usd: Decimal
    dias_vencimiento: int = 30
