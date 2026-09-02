"""CRUD de usuarios/propietarios — Solo accesible por admin o junta."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioOut
from app.auth.dependencies import require_admin
from app.auth.jwt_handler import hashear_password

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


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
