"""CRUD de apartamentos y matriz de deudas."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
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
    if float(data.alicuota) < 0:
        raise HTTPException(status_code=400, detail="La cuota fija mensual debe ser mayor o igual a 0")

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
    
    # Sincronización bidireccional inmediata en BD: Si cambia activo, propagar al propietario
    if "activo" in data.model_dump(exclude_unset=True) and apto.propietario:
        apto.propietario.activo = apto.activo

    db.commit()
    db.refresh(apto)
    return apto


@router.patch("/{apartamento_id}/toggle-activo", response_model=ApartamentoOut)
def alternar_estado_apartamento(
    apartamento_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Activa o desactiva el apartamento (para omitir notificaciones/avisos)."""
    apto = db.query(Apartamento).filter(Apartamento.id == apartamento_id).first()
    if not apto:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")
    apto.activo = not bool(apto.activo)
    if apto.propietario:
        apto.propietario.activo = apto.activo
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
    """Retorna el resumen de cuotas fijas mensuales de todos los apartamentos."""
    aptos = db.query(Apartamento).all()
    activos = [a for a in aptos if a.activo]
    total_recaudacion_esperada = sum(float(a.alicuota or 0) for a in activos)
    return {
        "total_apartamentos": len(aptos),
        "apartamentos_activos": len(activos),
        "suma_cuotas_usd": round(total_recaudacion_esperada, 2),
        "promedio_cuota_usd": round(total_recaudacion_esperada / len(activos), 2) if activos else 0,
        "es_valida": True,
    }


@router.post("/simular-avance-mes")
def simular_avance_mes(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Simula el paso a un nuevo mes de facturación.
    Incrementa +1 mes de deuda a todos los apartamentos activos
    y recalcula las deudas del condominio.
    """
    apartamentos = db.query(Apartamento).filter(Apartamento.activo == True).all()
    actualizados = 0

    for apto in apartamentos:
        if apto.propietario and not apto.propietario.activo:
            continue

        apto.meses_pendientes = (apto.meses_pendientes or 0) + 1
        actualizados += 1

    db.commit()
    return {
        "mensaje": f"Se ha simulado el avance al siguiente mes. {actualizados} apartamentos activos recibieron +1 mes de cuota.",
        "apartamentos_actualizados": actualizados,
    }


@router.post("/revertir-mes")
def revertir_mes(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Resta 1 mes de deuda a los apartamentos activos que tengan al menos 1 mes pendiente.
    Permite deshacer la simulación.
    """
    apartamentos = db.query(Apartamento).filter(Apartamento.activo == True).all()
    actualizados = 0

    for apto in apartamentos:
        if apto.propietario and not apto.propietario.activo:
            continue
        if apto.meses_pendientes and apto.meses_pendientes > 0:
            apto.meses_pendientes -= 1
            actualizados += 1

    db.commit()
    return {
        "mensaje": f"Se ha revertido 1 mes de cuota a {actualizados} apartamentos activos.",
        "apartamentos_actualizados": actualizados,
    }

