"""Servicio de autenticación: Login y registro de copropietarios."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.database import get_db
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento
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


class RegistroPropietario(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    email: str
    password: str
    telefono_whatsapp: str
    numero_apto: str
    piso: Optional[str] = "1"
    torre: Optional[str] = "Principal"


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


@router.post("/registro", response_model=TokenRespuesta, status_code=status.HTTP_201_CREATED)
def registro(
    data: RegistroPropietario,
    db: Session = Depends(get_db),
):
    """
    Registro público de copropietarios desde la pantalla de login.
    Crea el usuario y asigna/crea su apartamento con 0 deudas iniciales.
    """
    email_clean = data.email.strip().lower()
    cedula_clean = data.cedula.strip().upper()

    if db.query(Usuario).filter(Usuario.email == email_clean).first():
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya se encuentra registrado."
        )

    if db.query(Usuario).filter(Usuario.cedula == cedula_clean).first():
        raise HTTPException(
            status_code=400,
            detail="La cédula de identidad ya se encuentra registrada."
        )

    # Limpieza y formateo del teléfono WhatsApp
    tel = data.telefono_whatsapp.strip()
    tel_digits = "".join(filter(str.isdigit, tel))
    if not tel.startswith("+"):
        if tel_digits.startswith("58"):
            tel = f"+{tel_digits}"
        elif len(tel_digits) == 10:
            tel = f"+58{tel_digits}"
        elif len(tel_digits) == 11 and tel_digits.startswith("0"):
            tel = f"+58{tel_digits[1:]}"
        else:
            tel = f"+58{tel_digits}"

    nuevo_usuario = Usuario(
        nombre=data.nombre.strip(),
        apellido=data.apellido.strip(),
        cedula=cedula_clean,
        telefono_whatsapp=tel,
        email=email_clean,
        password_hash=hashear_password(data.password),
        rol="propietario",
        activo=True,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Crear o asignar apartamento con 0 deudas pendientes iniciales
    num_apto_clean = data.numero_apto.strip().upper()
    apto_existente = db.query(Apartamento).filter(Apartamento.numero_apto == num_apto_clean).first()

    if apto_existente:
        if not apto_existente.propietario_id:
            apto_existente.propietario_id = nuevo_usuario.id
            apto_existente.activo = True
            if apto_existente.meses_pendientes is None:
                apto_existente.meses_pendientes = 0
    else:
        nuevo_apto = Apartamento(
            numero_apto=num_apto_clean,
            piso=data.piso.strip() if data.piso else "1",
            torre=data.torre.strip() if data.torre else "Principal",
            alicuota=Decimal("15.00"),
            meses_pendientes=0,  # Entran con 0 deudas. El administrador colocará la deuda pendiente luego.
            activo=True,
            propietario_id=nuevo_usuario.id,
        )
        db.add(nuevo_apto)

    db.commit()

    token = crear_access_token(
        data={
            "sub": str(nuevo_usuario.id),
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol,
            "nombre": nuevo_usuario.nombre,
        }
    )

    return TokenRespuesta(
        access_token=token,
        rol=nuevo_usuario.rol,
        nombre=f"{nuevo_usuario.nombre} {nuevo_usuario.apellido}",
        email=nuevo_usuario.email,
        usuario_id=nuevo_usuario.id,
    )
