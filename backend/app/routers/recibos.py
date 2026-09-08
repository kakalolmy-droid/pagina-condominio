"""Gestión de recibos mensuales y emisión masiva por alícuota."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel
from app.database import get_db
from app.models.recibo import Recibo
from app.schemas.recibo import ReciboOut, ReciboConApartamento, EmisionMasivaRequest
from app.services.financiero import emitir_recibos_mes, sincronizar_recibos_todos_apartamentos
from app.auth.dependencies import require_admin, get_usuario_actual
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento

router = APIRouter(prefix="/api/recibos", tags=["Recibos"])


@router.get("/", response_model=List[ReciboOut])
def listar_recibos(
    periodo: Optional[str] = None,
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    sincronizar_recibos_todos_apartamentos(db)
    q = db.query(Recibo)
    if periodo:
        q = q.filter(Recibo.mes_periodo == periodo)
    if estado:
        q = q.filter(Recibo.estado_pago == estado)
    return q.order_by(Recibo.mes_periodo.desc(), Recibo.fecha_emision.desc()).all()


@router.get("/mis-recibos", response_model=List[ReciboOut])
def mis_recibos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    """Recibos del propietario autenticado."""
    sincronizar_recibos_todos_apartamentos(db)
    apto = db.query(Apartamento).filter(
        Apartamento.propietario_id == usuario_actual.id
    ).first()
    if not apto:
        return []
    return (
        db.query(Recibo)
        .filter(Recibo.apartamento_id == apto.id)
        .order_by(Recibo.mes_periodo.desc(), Recibo.fecha_emision.desc())
        .all()
    )


@router.get("/{recibo_id}", response_model=ReciboConApartamento)
def obtener_recibo(
    recibo_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_usuario_actual),
):
    recibo = db.query(Recibo).filter(Recibo.id == recibo_id).first()
    if not recibo:
        raise HTTPException(status_code=404, detail="Recibo no encontrado")
    return recibo


@router.post("/emitir-masivo")
def emitir_masivo(
    request: EmisionMasivaRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Emite recibos del mes a todos los apartamentos según su alícuota."""
    recibos = emitir_recibos_mes(db, request)
    return {
        "mensaje": f"{len(recibos)} recibos emitidos para el período {request.periodo}",
        "periodo": request.periodo,
        "total_emitidos": len(recibos),
        "gasto_total_usd": float(request.gasto_total_usd),
    }


@router.delete("/{recibo_id}", status_code=200)
def eliminar_recibo(
    recibo_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Elimina un recibo y sincroniza inmediatamente la deuda del apartamento."""
    recibo = db.query(Recibo).filter(Recibo.id == recibo_id).first()
    if not recibo:
        raise HTTPException(status_code=404, detail="Recibo no encontrado")

    from app.models.pago import Pago
    apto_id = recibo.apartamento_id

    # 1. Eliminar pagos asociados primero
    pagos = db.query(Pago).filter(Pago.recibo_id == recibo_id).all()
    for p in pagos:
        db.delete(p)

    # 2. Eliminar el recibo
    db.delete(recibo)
    db.commit()

    # 3. Sincronizar meses_pendientes del apartamento
    apto = db.query(Apartamento).filter(Apartamento.id == apto_id).first()
    if apto:
        pendientes = db.query(Recibo).filter(
            Recibo.apartamento_id == apto_id,
            Recibo.estado_pago != "pagado"
        ).count()
        apto.meses_pendientes = pendientes
        db.commit()

    return {"mensaje": "Recibo eliminado con éxito"}


class ReciboIndividualRequest(BaseModel):
    apartamento_id: int
    mes_periodo: str
    monto_total_usd: Optional[Decimal] = None


@router.post("/crear-individual", response_model=ReciboOut, status_code=201)
def crear_recibo_individual(
    req: ReciboIndividualRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Genera o emite un recibo para un mes específico a un apartamento si aún no existía."""
    from datetime import date, timedelta
    apto = db.query(Apartamento).filter(Apartamento.id == req.apartamento_id).first()
    if not apto:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")

    existente = db.query(Recibo).filter(
        Recibo.apartamento_id == apto.id,
        Recibo.mes_periodo == req.mes_periodo
    ).first()
    if existente:
        return existente

    hoy = date.today()
    monto = req.monto_total_usd if (req.monto_total_usd and req.monto_total_usd > 0) else (apto.alicuota or Decimal("15.00"))

    nuevo = Recibo(
        apartamento_id=apto.id,
        mes_periodo=req.mes_periodo,
        monto_total_usd=monto,
        monto_pendiente_usd=monto,
        estado_pago="pendiente",
        fecha_emision=hoy,
        fecha_vencimiento=hoy + timedelta(days=15),
    )
    db.add(nuevo)
    db.flush()

    # Actualizar meses pendientes
    pendientes = db.query(Recibo).filter(
        Recibo.apartamento_id == apto.id,
        Recibo.estado_pago != "pagado"
    ).count()
    apto.meses_pendientes = pendientes

    db.commit()
    db.refresh(nuevo)
    return nuevo
