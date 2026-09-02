from sqlalchemy import Column, Integer, Date, Numeric, DateTime, func
from app.database import Base


class TasaBCV(Base):
    __tablename__ = "tasas_bcv"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, unique=True, nullable=False, index=True)
    tasa_usd_ves = Column(Numeric(12, 4), nullable=False)  # Bs. por 1 USD
    fecha_registro = Column(DateTime, server_default=func.now())
