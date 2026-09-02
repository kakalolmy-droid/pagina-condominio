from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Apartamento(Base):
    __tablename__ = "apartamentos"

    id = Column(Integer, primary_key=True, index=True)
    numero_apto = Column(String(10), nullable=False)
    piso = Column(String(5))
    torre = Column(String(20), default="Principal")
    alicuota = Column(Numeric(5, 4), nullable=False)  # Ej: 0.0250 = 2.50%
    saldo_favor_usd = Column(Numeric(10, 2), default=0.00)
    propietario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))

    # Relaciones
    propietario = relationship("Usuario", back_populates="apartamentos")
    recibos = relationship("Recibo", back_populates="apartamento")
    pagos = relationship("Pago", back_populates="apartamento")
