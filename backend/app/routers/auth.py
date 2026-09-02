"""Servicio de autenticación: Login y registro de administradores."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.usuario import Usuario
from app.auth.jwt_handler import verificar_password, crear_access_token, hashear_password
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
    email: str
    usuario_id: int


@router.post("/login", response_model=TokenRespuesta)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Inicio de sesión universal que soporta tanto JSON como form-urlencoded.
    """
    content_type = request.headers.get("content-type", "")
    email = ""
    password = ""

    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email") or body.get("username", "")
        password = body.get("password", "")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email", "")
        password = form.get("password", "")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not verificar_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_access_token(
        data={
            "sub": str(usuario.id),
            "email": usuario.email,
            "rol": usuario.rol,
            "nombre": usuario.nombre,
        }
    )

    return TokenRespuesta(
        access_token=token,
        rol=usuario.rol,
        nombre=f"{usuario.nombre} {usuario.apellido}",
        email=usuario.email,
        usuario_id=usuario.id,
    )
