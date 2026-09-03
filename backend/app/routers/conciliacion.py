"""Conciliación de pagos: aprobación/rechazo y emisión de solvencia PDF."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.models.pago import Pago
from app.models.recibo import Recibo
from app.schemas.pago import PagoOut
from app.services.pdf_generator import generar_pdf_solvencia
from app.auth.dependencies import require_admin, get_usuario_actual
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/conciliacion", tags=["Conciliación"])


@router.get("/pendientes", response_model=List[PagoOut])
def pagos_pendientes(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Retorna todos los pagos en estado 'en_revision'."""
    return (
        db.query(Pago)
        .filter(Pago.estado_conciliacion == "en_revision")
        .order_by(Pago.fecha_reporte.asc())
        .all()
    )


@router.post("/{pago_id}/aprobar", response_model=PagoOut)
def aprobar_pago(
    pago_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    """
    Aprueba un pago:
    1. Actualiza estado del recibo (parcial o pagado)
    2. Acredita excedente al saldo a favor del apartamento
    3. Registra quién aprobó y cuándo
    """
    try:
        pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not pago:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        if pago.estado_conciliacion != "en_revision":
            raise HTTPException(status_code=400, detail="Este pago ya fue procesado")

        recibo = pago.recibo
        apto = pago.apartamento
        monto_usd = pago.monto_equivalente_usd
        pendiente = recibo.monto_pendiente_usd if recibo else Decimal("15.00")

        if recibo:
            if monto_usd >= pendiente:
                excedente = monto_usd - pendiente
                recibo.monto_pendiente_usd = Decimal("0.00")
                recibo.estado_pago = "pagado"
                if excedente > 0 and apto:
                    apto.saldo_favor_usd = (apto.saldo_favor_usd or Decimal("0")) + excedente
            else:
                recibo.monto_pendiente_usd = pendiente - monto_usd
                recibo.estado_pago = "parcial"

        pago.estado_conciliacion = "aprobado"
        pago.fecha_aprobacion = datetime.utcnow()
        pago.aprobado_por = admin.id

        db.flush()

        if apto:
            # Actualizar meses_pendientes del apartamento en tiempo real
            recibos_restantes = db.query(Recibo).filter(
                Recibo.apartamento_id == apto.id,
                Recibo.estado_pago != "pagado"
            ).count()
            apto.meses_pendientes = recibos_restantes

        db.commit()
        db.refresh(pago)

        try:
            if apto and apto.propietario:
                from app.tasks.notificaciones import enviar_whatsapp
                propietario = apto.propietario
                from app.config import get_settings
                s = get_settings()
                msg = (
                    f"✅ Pago aprobado — {s.condominio_nombre}\n"
                    f"Período: {recibo.mes_periodo if recibo else 'Actual'}\n"
                    f"Monto: ${float(monto_usd):.2f} USD\n"
                    f"Su recibo de solvencia fue generado.\n"
                    f"Descárguelo en: {s.condominio_portal_url}/mi-cuenta/recibos"
                )
                if propietario.telefono_whatsapp:
                    enviar_whatsapp.delay(propietario.telefono_whatsapp, msg)
        except BaseException:
            pass

        return pago

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al aprobar pago: {str(e)}")


@router.post("/{pago_id}/rechazar", response_model=PagoOut)
def rechazar_pago(
    pago_id: int,
    motivo: str,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    """Rechaza un pago con un motivo."""
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if pago.estado_conciliacion != "en_revision":
        raise HTTPException(status_code=400, detail="Este pago ya fue procesado")

    pago.estado_conciliacion = "rechazado"
    pago.motivo_rechazo = motivo
    pago.aprobado_por = admin.id
    db.commit()
    db.refresh(pago)
    return pago


@router.get("/solvencia/{pago_id}/pdf")
def descargar_solvencia(
    pago_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_usuario_actual),
):
    """Descarga el PDF del recibo de solvencia para un pago aprobado."""
    pago = db.query(Pago).filter(
        Pago.id == pago_id,
        Pago.estado_conciliacion == "aprobado",
    ).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Solvencia no encontrada o pago no aprobado")

    pdf_bytes = generar_pdf_solvencia(pago)
    nombre = f"solvencia_{pago.apartamento.numero_apto}_{pago.recibo.mes_periodo}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
