from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Recibo(Base):
    __tablename__ = "recibos"

    id = Column(Integer, primary_key=True, index=True)
    apartamento_id = Column(Integer, ForeignKey("apartamentos.id"), nullable=False)
    mes_periodo = Column(String(7), nullable=False)       # '2026-09'
    monto_total_usd = Column(Numeric(10, 2), nullable=False)
    monto_pendiente_usd = Column(Numeric(10, 2), nullable=False)
    estado_pago = Column(String(20), default="pendiente") # pendiente | parcial | pagado
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)

    # Relaciones
    apartamento = relationship("Apartamento", back_populates="recibos")
    pagos = relationship("Pago", back_populates="recibo")
