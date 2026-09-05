from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class ConfiguracionCondominio(Base):
    __tablename__ = "configuracion_condominio"

    id = Column(Integer, primary_key=True, index=True)
    banco = Column(String(150), default="Banco de Venezuela (0102)")
    pago_movil = Column(String(150), default="0414-1234567 | C.I. V-00000001")
    cuenta_transferencia = Column(String(150), default="0102-0000-00-0000000000")
    zelle = Column(String(150), default="pagos@edificioalcatraz.com")
    nota_predeterminada = Column(Text, nullable=True, default="")
    telefono_whatsapp_emisor = Column(String(50), nullable=True, default="")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
