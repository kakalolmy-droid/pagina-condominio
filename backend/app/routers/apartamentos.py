"""CRUD de apartamentos y matriz de deudas."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.apartamento import Apartamento
from app.schemas.apartamento import ApartamentoCreate, ApartamentoUpdate, ApartamentoOut
from app.services.financiero import obtener_matriz_deudas
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/apartamentos", tags=["Apartamentos"])


@router.get("/", response_model=List[ApartamentoOut])
def listar_apartamentos(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return db.query(Apartamento).order_by(Apartamento.numero_apto).all()


@router.get("/deudas")
def matriz_deudas(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Retorna la matriz completa de deudas con conversión BCV."""
    return obtener_matriz_deudas(db)


@router.get("/{apartamento_id}", response_model=ApartamentoOut)
def obtener_apartamento(
    apartamento_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    apto = db.query(Apartamento).filter(Apartamento.id == apartamento_id).first()
    if not apto:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")
    return apto


@router.post("/", response_model=ApartamentoOut, status_code=status.HTTP_201_CREATED)
def crear_apartamento(
    data: ApartamentoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    if not (0 < float(data.alicuota) <= 1):
        raise HTTPException(status_code=400, detail="La alícuota debe estar entre 0 y 1 (ej: 0.025 = 2.5%)")

    apto = Apartamento(**data.model_dump())
    db.add(apto)
    db.commit()
    db.refresh(apto)
    return apto


@router.put("/{apartamento_id}", response_model=ApartamentoOut)
def actualizar_apartamento(
    apartamento_id: int,
    data: ApartamentoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    apto = db.query(Apartamento).filter(Apartamento.id == apartamento_id).first()
    if not apto:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(apto, campo, valor)
    db.commit()
    db.refresh(apto)
    return apto


@router.delete("/{apartamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_apartamento(
    apartamento_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    apto = db.query(Apartamento).filter(Apartamento.id == apartamento_id).first()
    if not apto:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")
    db.delete(apto)
    db.commit()


@router.get("/suma-alicuotas")
def verificar_suma_alicuotas(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Verifica que la suma de todas las alícuotas sea igual a 1 (100%)."""
    aptos = db.query(Apartamento).all()
    total = sum(float(a.alicuota) for a in aptos)
    return {
        "total_apartamentos": len(aptos),
        "suma_alicuotas": round(total, 6),
        "es_valida": abs(total - 1.0) < 0.0001,
        "diferencia": round(1.0 - total, 6),
    }
