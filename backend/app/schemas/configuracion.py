from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DatosBancariosBase(BaseModel):
    banco: Optional[str] = "Banco de Venezuela (0102)"
    pago_movil: Optional[str] = "0414-1234567 | C.I. V-00000001"
    cuenta_transferencia: Optional[str] = "0102-0000-00-0000000000"
    zelle: Optional[str] = "pagos@edificioalcatraz.com"
    nota_predeterminada: Optional[str] = ""
    telefono_whatsapp_emisor: Optional[str] = ""


class DatosBancariosUpdate(DatosBancariosBase):
    pass


class DatosBancariosOut(DatosBancariosBase):
    id: Optional[int] = 1
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
