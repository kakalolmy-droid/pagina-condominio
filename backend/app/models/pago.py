from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    apartamento_id = Column(Integer, ForeignKey("apartamentos.id"), nullable=False)
    recibo_id = Column(Integer, ForeignKey("recibos.id"), nullable=False)

    # Datos del pago declarado por el propietario
    metodo_pago = Column(String(30), nullable=False)      # pago_movil | transferencia_ves | zelle | efectivo_usd
    banco_origen = Column(String(60))
    referencia_bancaria = Column(String(60), nullable=False)
    monto_declarado = Column(Numeric(14, 2), nullable=False)
    moneda_pago = Column(String(5), nullable=False)       # VES | USD

    # Conversión automática al momento del reporte
    tasa_bcv_aplicada = Column(Numeric(12, 4), nullable=False)
    monto_equivalente_usd = Column(Numeric(10, 2), nullable=False)

    # Comprobante subido
    comprobante_url = Column(Text, nullable=False)

    # Conciliación
    estado_conciliacion = Column(String(20), default="en_revision")  # en_revision | aprobado | rechazado
    motivo_rechazo = Column(Text)
    aprobado_por = Column(Integer, ForeignKey("usuarios.id"))

    # Timestamps
    fecha_reporte = Column(DateTime, server_default=func.now())
    fecha_aprobacion = Column(DateTime)

    # Relaciones
    apartamento = relationship("Apartamento", back_populates="pagos")
    recibo = relationship("Recibo", back_populates="pagos")
    aprobado_por_usuario = relationship(
        "Usuario", back_populates="pagos_aprobados", foreign_keys=[aprobado_por]
    )
