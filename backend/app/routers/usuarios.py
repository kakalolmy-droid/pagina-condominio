"""CRUD de usuarios/propietarios — Solo accesible por admin o junta."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioOut, PerfilUpdate, PerfilOut
from app.auth.dependencies import require_admin, get_usuario_actual
from app.auth.jwt_handler import hashear_password

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=PerfilOut)
def obtener_perfil_actual(
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    """
    Retorna la información personal del usuario autenticado junto con
    los datos de sus inmuebles y balances (solo lectura).
    """
    return usuario_actual


@router.put("/me", response_model=PerfilOut)
def actualizar_perfil_actual(
    data: PerfilUpdate,
    usuario_actual: Usuario = Depends(get_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Permite al usuario autenticado actualizar únicamente sus datos personales:
    nombre, apellido, teléfono WhatsApp, email y opcionalmente su contraseña.
    ESTRICTAMENTE PROTEGIDO: Rechaza e ignora cualquier modificación a los datos
    del apartamento, alícuotas o deudas pendientes (solo modificables por administración).
    """
    # 1. Validación y actualización de correo electrónico
    if data.email:
        nuevo_email = data.email.strip().lower()
        if nuevo_email != usuario_actual.email.lower():
            existente = db.query(Usuario).filter(Usuario.email == nuevo_email).first()
            if existente and existente.id != usuario_actual.id:
                raise HTTPException(
                    status_code=400,
                    detail="El correo electrónico ingresado ya está en uso por otra cuenta.",
                )
            usuario_actual.email = nuevo_email

    # 2. Nombre y Apellido
    if data.nombre is not None:
        nom = data.nombre.strip()
        if len(nom) < 2:
            raise HTTPException(status_code=400, detail="El nombre debe tener al menos 2 caracteres.")
        usuario_actual.nombre = nom

    if data.apellido is not None:
        ape = data.apellido.strip()
        if len(ape) < 2:
            raise HTTPException(status_code=400, detail="El apellido debe tener al menos 2 caracteres.")
        usuario_actual.apellido = ape

    # 3. Teléfono WhatsApp
    if data.telefono_whatsapp is not None:
        tel = data.telefono_whatsapp.strip()
        tel_digits = "".join(filter(str.isdigit, tel))
        if len(tel_digits) < 7:
            raise HTTPException(
                status_code=400,
                detail="Por favor ingresa un número de WhatsApp válido.",
            )
        if not tel.startswith("+"):
            if tel_digits.startswith("58"):
                tel = f"+{tel_digits}"
            elif len(tel_digits) == 10:
                tel = f"+58{tel_digits}"
            elif len(tel_digits) == 11 and tel_digits.startswith("0"):
                tel = f"+58{tel_digits[1:]}"
            else:
                tel = f"+58{tel_digits}"
        usuario_actual.telefono_whatsapp = tel

    # 4. Contraseña (opcional)
    if data.password is not None and data.password.strip():
        pwd = data.password.strip()
        if len(pwd) < 6:
            raise HTTPException(
                status_code=400,
                detail="La nueva contraseña debe tener al menos 6 caracteres.",
            )
        usuario_actual.password_hash = hashear_password(pwd)

    db.commit()
    db.refresh(usuario_actual)
    return usuario_actual


@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(
    rol: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Lista todos los usuarios, opcionalmente filtrando por rol."""
    q = db.query(Usuario)
    if rol:
        q = q.filter(Usuario.rol == rol)
    return q.order_by(Usuario.apellido).all()


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Crea un nuevo propietario desde el panel administrativo."""
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if db.query(Usuario).filter(Usuario.cedula == data.cedula).first():
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")

    nuevo = Usuario(
        nombre=data.nombre,
        apellido=data.apellido,
        cedula=data.cedula,
        telefono_whatsapp=data.telefono_whatsapp,
        email=data.email,
        password_hash=hashear_password(data.password),
        rol=data.rol,
        activo=data.activo,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password_hash"] = hashear_password(update_data.pop("password"))
    for campo, valor in update_data.items():
        setattr(usuario, campo, valor)

    # Sincronización bidireccional inmediata en BD: Si cambia activo, propagar a todos sus inmuebles
    if "activo" in update_data:
        for a in usuario.apartamentos:
            a.activo = usuario.activo

    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/toggle-activo", response_model=UsuarioOut)
def alternar_estado_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Activa o desactiva a un usuario sin borrar sus datos históricos."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.activo = not bool(usuario.activo)
    for a in usuario.apartamentos:
        a.activo = usuario.activo
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
