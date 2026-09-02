from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.schemas.usuario import UsuarioSimple
from app.schemas.recibo import ReciboOut

class PagoBase(BaseModel):
    recibo_id: int
    metodo_pago: str  # pago_movil | transferencia_ves | zelle | efectivo_usd
    banco_origen: Optional[str] = None
    referencia_bancaria: str
    monto_declarado: Decimal
    moneda_pago: str  # VES | USD

class PagoCreate(PagoBase):
    pass

class PagoOut(PagoBase):
    id: int
    apartamento_id: int
    tasa_bcv_aplicada: Decimal
    monto_equivalente_usd: Decimal
    comprobante_url: str
    estado_conciliacion: str
    motivo_rechazo: Optional[str] = None
    fecha_reporte: datetime
    fecha_aprobacion: Optional[datetime] = None
    aprobado_por_usuario: Optional[UsuarioSimple] = None
    recibo: Optional[ReciboOut] = None
    class Config:
        from_attributes = True

class PagoConciliacion(BaseModel):
    accion: str  # 'aprobar' | 'rechazar'
    motivo_rechazo: Optional[str] = None
