from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Apartamento(Base):
    __tablename__ = "apartamentos"

    id = Column(Integer, primary_key=True, index=True)
    numero_apto = Column(String(10), nullable=False)
    piso = Column(String(5))
    torre = Column(String(20), default="Principal")
    alicuota = Column(Numeric(10, 2), default=15.00)  # Cuota fija mensual en USD (ej: $15.00)
    saldo_favor_usd = Column(Numeric(10, 2), default=0.00)
    activo = Column(Boolean, default=True)  # Si está inactivo, no se le envían avisos ni cobra
    propietario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))

    # Relaciones
    propietario = relationship("Usuario", back_populates="apartamentos")
    recibos = relationship("Recibo", back_populates="apartamento")
    pagos = relationship("Pago", back_populates="apartamento")
