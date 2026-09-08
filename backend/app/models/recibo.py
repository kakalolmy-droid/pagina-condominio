from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Recibo(Base):
    __tablename__ = "recibos"
    __table_args__ = (
        Index("idx_recibo_apto_periodo", "apartamento_id", "mes_periodo"),
        Index("idx_recibo_apto_estado", "apartamento_id", "estado_pago"),
    )

    id = Column(Integer, primary_key=True, index=True)
    apartamento_id = Column(Integer, ForeignKey("apartamentos.id"), nullable=False, index=True)
    mes_periodo = Column(String(7), nullable=False, index=True)       # '2026-09'
    monto_total_usd = Column(Numeric(10, 2), nullable=False)
    monto_pendiente_usd = Column(Numeric(10, 2), nullable=False)
    estado_pago = Column(String(20), default="pendiente", index=True) # pendiente | parcial | pagado
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)

    # Relaciones
    apartamento = relationship("Apartamento", back_populates="recibos")
    pagos = relationship("Pago", back_populates="recibo")

    @property
    def ultimo_pago(self):
        if self.pagos:
            # Priorizar pago en revisión si existe
            en_rev = [p for p in self.pagos if p.estado_conciliacion == "en_revision"]
            if en_rev:
                return en_rev[-1]
            return self.pagos[-1]
        return None

    @property
    def ultimo_pago_id(self):
        p = self.ultimo_pago
        return p.id if p else None

    @property
    def ultimo_pago_estado(self):
        p = self.ultimo_pago
        return p.estado_conciliacion if p else None

    @property
    def comprobante_url(self):
        p = self.ultimo_pago
        return p.comprobante_url if p else None

    @property
    def ultimo_pago_referencia(self):
        p = self.ultimo_pago
        return p.referencia_bancaria if p else None

    @property
    def ultimo_pago_metodo(self):
        p = self.ultimo_pago
        return p.metodo_pago if p else None

    @property
    def ultimo_pago_monto(self):
        p = self.ultimo_pago
        return p.monto_declarado if p else None

    @property
    def ultimo_pago_fecha(self):
        p = self.ultimo_pago
        return p.fecha_reporte if p else None

