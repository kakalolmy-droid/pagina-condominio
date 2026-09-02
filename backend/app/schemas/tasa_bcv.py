from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal

class TasaBCVOut(BaseModel):
    id: int
    fecha: date
    tasa_usd_ves: Decimal
    fecha_registro: datetime
    class Config:
        from_attributes = True
