"""CRUD de apartamentos y matriz de deudas."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import date, timedelta
from app.database import get_db
from app.models.apartamento import Apartamento
from app.models.recibo import Recibo
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
    Simula el paso a un nuevo mes de facturación:
    1. Calcula el siguiente período YYYY-MM.
    2. Emite el recibo oficial correspondiente para cada apartamento activo.
    3. Incrementa +1 mes de deuda (meses_pendientes) en cada inmueble activo.
    """
    # 1. Determinar el siguiente período a partir del último recibo existente
    ultimo_recibo = db.query(Recibo).order_by(Recibo.mes_periodo.desc()).first()
    if ultimo_recibo and ultimo_recibo.mes_periodo:
        try:
            parts = ultimo_recibo.mes_periodo.split("-")
            year, month = int(parts[0]), int(parts[1])
            if month == 12:
                next_periodo = f"{year + 1:04d}-01"
            else:
                next_periodo = f"{year:04d}-{month + 1:02d}"
        except Exception:
            next_periodo = "2026-10"
    else:
        next_periodo = "2026-10"

    apartamentos = db.query(Apartamento).all()
    actualizados = 0
    hoy = date.today()
    vencimiento = hoy + timedelta(days=15)

    for apto in apartamentos:
        # Omitir cualquier apartamento o propietario desactivado
        if not apto.activo or apto.activo in (0, "0", False, "false"):
            continue
        if apto.propietario and (not apto.propietario.activo or apto.propietario.activo in (0, "0", False, "false")):
            continue

        apto.meses_pendientes = (apto.meses_pendientes or 0) + 1

        # Crear el recibo para este nuevo período si no existe ya
        recibo_existente = db.query(Recibo).filter(
            Recibo.apartamento_id == apto.id,
            Recibo.mes_periodo == next_periodo
        ).first()

        if not recibo_existente:
            monto = Decimal(str(apto.alicuota or 15.00))
            nuevo_recibo = Recibo(
                apartamento_id=apto.id,
                mes_periodo=next_periodo,
                monto_total_usd=monto,
                monto_pendiente_usd=monto,
                estado_pago="pendiente",
                fecha_emision=hoy,
                fecha_vencimiento=vencimiento,
            )
            db.add(nuevo_recibo)

        actualizados += 1

    db.commit()
    return {
        "mensaje": f"Se ha avanzado al período {next_periodo}. Se generaron los nuevos recibos y se sumó +1 mes a {actualizados} apartamentos activos.",
        "periodo_generado": next_periodo,
        "apartamentos_actualizados": actualizados,
    }


@router.post("/revertir-mes")
def revertir_mes(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Deshace la simulación:
    1. Resta 1 mes de deuda a los apartamentos activos.
    2. Elimina los recibos del último período simulado.
    """
    ultimo_recibo = db.query(Recibo).order_by(Recibo.mes_periodo.desc()).first()
    ultimo_periodo = ultimo_recibo.mes_periodo if ultimo_recibo else None

    apartamentos = db.query(Apartamento).all()
    actualizados = 0

    for apto in apartamentos:
        if not apto.activo or apto.activo in (0, "0", False, "false"):
            continue
        if apto.propietario and (not apto.propietario.activo or apto.propietario.activo in (0, "0", False, "false")):
            continue

        if apto.meses_pendientes and apto.meses_pendientes > 0:
            apto.meses_pendientes -= 1
            actualizados += 1

        if ultimo_periodo:
            recibo_borrar = db.query(Recibo).filter(
                Recibo.apartamento_id == apto.id,
                Recibo.mes_periodo == ultimo_periodo,
                Recibo.estado_pago == "pendiente"
            ).first()
            if recibo_borrar:
                db.delete(recibo_borrar)

    db.commit()
    return {
        "mensaje": f"Se ha revertido el período {ultimo_periodo or ''}. Recibos y meses actualizados para {actualizados} apartamentos.",
        "apartamentos_actualizados": actualizados,
    }


