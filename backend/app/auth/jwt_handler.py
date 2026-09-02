"""Manejo de tokens JWT y hashing de contraseñas directamente con bcrypt."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.config import get_settings

settings = get_settings()


def hashear_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt nativo."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verificar_password(password_plano: str, password_hasheado: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    try:
        pwd_bytes = password_plano.encode('utf-8')[:72]
        hash_bytes = password_hasheado.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera un JWT firmado con los datos del usuario."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decodificar_token(token: str) -> dict:
    """Decodifica y valida un token JWT."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
