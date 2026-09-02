from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    telefono_whatsapp = Column(String(20), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="propietario")  # admin | junta | propietario
    fecha_registro = Column(DateTime, server_default=func.now())

    # Relaciones
    apartamentos = relationship("Apartamento", back_populates="propietario")
    pagos_aprobados = relationship(
        "Pago", back_populates="aprobado_por_usuario", foreign_keys="Pago.aprobado_por"
    )
