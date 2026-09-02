"""Dependencias de seguridad y autorización para FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.auth.jwt_handler import decodificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Extrae y valida el usuario actual a partir del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if usuario is None:
        raise credentials_exception
    return usuario


def require_admin(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """Solo administradores."""
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido únicamente a administradores",
        )
    return usuario


def require_junta_o_admin(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """Administradores o miembros de la Junta."""
    if usuario.rol not in ["admin", "junta"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a la Junta o Administradores",
        )
    return usuario


def require_propietario(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """Propietarios, junta o admin."""
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
        )
    return usuario
