"""Servicio de autenticación: Login y registro de copropietarios."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import secrets
from datetime import datetime, timedelta
import httpx
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


# ── Recuperación de Contraseña por WhatsApp (OTP) ──────────────────────────

class SolicitudRecuperacion(BaseModel):
    identificador: str  # Email, cédula o número de WhatsApp


class RestablecerPassword(BaseModel):
    identificador: str
    codigo: str
    nueva_password: str


def buscar_usuario_por_identificador(db: Session, identificador: str) -> Optional[Usuario]:
    """Busca a un usuario por email, cédula o número de teléfono celular."""
    texto = identificador.strip()
    if not texto:
        return None

    # 1. Por correo electrónico exacto
    u = db.query(Usuario).filter(Usuario.email.ilike(texto.lower())).first()
    if u:
        return u

    # 2. Por cédula de identidad
    cedula_limpia = texto.upper().replace(" ", "")
    u = db.query(Usuario).filter(Usuario.cedula == cedula_limpia).first()
    if u:
        return u
    if not any(cedula_limpia.startswith(pref) for pref in ["V-", "E-", "J-"]):
        u = db.query(Usuario).filter(Usuario.cedula == f"V-{cedula_limpia}").first()
        if u:
            return u

    # 3. Por número de teléfono WhatsApp
    digitos = "".join(filter(str.isdigit, texto))
    if len(digitos) >= 7:
        ultimos = digitos[-10:] if len(digitos) >= 10 else digitos
        usuarios = db.query(Usuario).all()
        for cand in usuarios:
            cand_digitos = "".join(filter(str.isdigit, cand.telefono_whatsapp or ""))
            if cand_digitos and cand_digitos.endswith(ultimos):
                return cand

    return None


@router.post("/forgot-password")
async def solicitar_recuperacion_contrasena(
    data: SolicitudRecuperacion,
    db: Session = Depends(get_db),
):
    """
    Genera un código de seguridad OTP de 6 dígitos con 15 minutos de vigencia
    y lo despacha al WhatsApp registrado del copropietario.
    """
    identificador = data.identificador.strip()
    usuario = buscar_usuario_por_identificador(db, identificador)
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ningún usuario activo con los datos proporcionados. Verifique el correo, cédula o teléfono.",
        )

    if not usuario.telefono_whatsapp:
        raise HTTPException(
            status_code=400,
            detail="El usuario no posee un número de WhatsApp registrado para recibir el código.",
        )

    # Generar código OTP de 6 dígitos numéricos
    otp = f"{secrets.randbelow(900000) + 100000}"
    usuario.reset_token = otp
    usuario.reset_token_exp = datetime.utcnow() + timedelta(minutes=15)
    db.commit()

    # Formatear teléfono para Baileys
    clean_phone = "".join(filter(str.isdigit, usuario.telefono_whatsapp))
    if not clean_phone.startswith("58") and len(clean_phone) == 10:
        clean_phone = f"58{clean_phone}"

    # Mensaje de WhatsApp
    mensaje_wpp = (
        f"🏢 *Edificio Alcatraz — Recuperación de Contraseña*\n\n"
        f"Hola *{usuario.nombre} {usuario.apellido}*,\n\n"
        f"Has solicitado restablecer tu contraseña de acceso al portal de condominio.\n\n"
        f"Tu código de seguridad de un solo uso es:\n"
        f"🔑 *{otp}*\n\n"
        f"⏱️ Este código es válido durante los próximos *15 minutos*.\n\n"
        f"_Si no solicitaste este cambio, por favor desestima este mensaje._"
    )

    WPP_SERVICE_URL = "http://127.0.0.1:3000"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{WPP_SERVICE_URL}/send-message",
                json={"phone": clean_phone, "message": mensaje_wpp},
            )
            if res.status_code != 200:
                data_err = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
                err_msg = data_err.get("error", "No se pudo entregar el mensaje por WhatsApp")
                raise HTTPException(
                    status_code=400,
                    detail=f"No se pudo enviar el mensaje por WhatsApp: {err_msg}. Asegúrese de que la línea oficial del condominio esté vinculada.",
                )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="El servicio de WhatsApp del condominio no se encuentra en línea en este momento. Por favor contacte a la Junta de Condominio o intente más tarde.",
        )

    tel_raw = usuario.telefono_whatsapp
    tel_mascarado = f"***{tel_raw[-4:]}" if len(tel_raw) >= 4 else "***"

    return {
        "ok": True,
        "mensaje": f"Se ha enviado un código de seguridad de 6 dígitos a tu WhatsApp ({tel_mascarado}).",
        "telefono_mascarado": tel_mascarado,
        "usuario_email": usuario.email,
    }


@router.post("/reset-password")
def restablecer_contrasena(
    data: RestablecerPassword,
    db: Session = Depends(get_db),
):
    """
    Verifica el código OTP recibido por WhatsApp y actualiza la contraseña del usuario.
    """
    usuario = buscar_usuario_por_identificador(db, data.identificador)
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado.",
        )

    if not usuario.reset_token or usuario.reset_token.strip() != data.codigo.strip():
        raise HTTPException(
            status_code=400,
            detail="El código de seguridad ingresado es incorrecto.",
        )

    if not usuario.reset_token_exp or usuario.reset_token_exp < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="El código de seguridad ha expirado. Por favor solicita uno nuevo.",
        )

    nueva_pwd = data.nueva_password.strip()
    if len(nueva_pwd) < 6:
        raise HTTPException(
            status_code=400,
            detail="La nueva contraseña debe tener al menos 6 caracteres.",
        )

    usuario.password_hash = hashear_password(nueva_pwd)
    usuario.reset_token = None
    usuario.reset_token_exp = None
    db.commit()

    return {
        "ok": True,
        "mensaje": "¡Tu contraseña ha sido restablecida exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.",
    }

