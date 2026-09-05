from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    telefono_whatsapp: str
    email: EmailStr
    rol: str = "propietario"
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    cedula: Optional[str] = None
    telefono_whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    password: Optional[str] = None
    activo: Optional[bool] = None

class UsuarioSimple(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    rol: str
    activo: bool = True
    class Config:
        from_attributes = True

class UsuarioOut(UsuarioBase):
    id: int
    fecha_registro: Optional[datetime] = None
    class Config:
        from_attributes = True

class ApartamentoLecturaPerfil(BaseModel):
    id: int
    numero_apto: str
    piso: Optional[str] = None
    torre: Optional[str] = None
    alicuota: Optional[float] = None
    meses_pendientes: Optional[int] = 0
    saldo_favor_usd: Optional[float] = 0.0
    activo: Optional[bool] = True
    class Config:
        from_attributes = True

class PerfilUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono_whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class PerfilOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    cedula: str
    telefono_whatsapp: str
    email: EmailStr
    rol: str
    activo: bool
    apartamentos: list[ApartamentoLecturaPerfil] = []
    class Config:
        from_attributes = True
