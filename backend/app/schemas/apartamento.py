from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.schemas.usuario import UsuarioSimple

class ApartamentoBase(BaseModel):
    numero_apto: str
    piso: Optional[str] = None
    torre: str = "Principal"
    alicuota: Decimal = Decimal("15.00")  # Cuota fija mensual en USD (ej: $15.00)
    activo: bool = True
    propietario_id: Optional[int] = None

class ApartamentoCreate(ApartamentoBase):
    pass

class ApartamentoUpdate(BaseModel):
    numero_apto: Optional[str] = None
    piso: Optional[str] = None
    torre: Optional[str] = None
    alicuota: Optional[Decimal] = None
    activo: Optional[bool] = None
    propietario_id: Optional[int] = None

class ApartamentoOut(ApartamentoBase):
    id: int
    saldo_favor_usd: Decimal
    propietario: Optional[UsuarioSimple] = None
    class Config:
        from_attributes = True

class ApartamentoConDeuda(ApartamentoOut):
    deuda_total_usd: Decimal = Decimal("0.00")
    deuda_total_ves: Decimal = Decimal("0.00")
    meses_adeudados: list[str] = []
    estado: str = "solvente"  # solvente | moroso | parcial
