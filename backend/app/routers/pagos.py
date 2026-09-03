"""Auto-reporte de pagos por el propietario con upload de comprobante."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.database import get_db
from app.models.pago import Pago
from app.models.recibo import Recibo
from app.models.apartamento import Apartamento
from app.schemas.pago import PagoOut
from app.services.cloudinary_service import subir_comprobante
from app.services.bcv_scraper import obtener_tasa_actual, convertir_ves_a_usd
from app.auth.dependencies import get_usuario_actual
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/pagos", tags=["Pagos"])


@router.get("/mis-pagos", response_model=List[PagoOut])
def mis_pagos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    """Historial de pagos reportados por el propietario autenticado."""
    apto = db.query(Apartamento).filter(
        Apartamento.propietario_id == usuario_actual.id
    ).first()
    if not apto:
        return []
    return (
        db.query(Pago)
        .filter(Pago.apartamento_id == apto.id)
        .order_by(Pago.fecha_reporte.desc())
        .all()
    )


@router.post("/reportar", response_model=PagoOut, status_code=201)
async def reportar_pago(
    recibo_id: int = Form(...),
    metodo_pago: str = Form(...),
    referencia_bancaria: str = Form(...),
    monto_declarado: Decimal = Form(...),
    moneda_pago: str = Form(...),  # VES | USD
    banco_origen: Optional[str] = Form(None),
    comprobante: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    try:
        """Registra un pago reportado por el propietario."""
        apto = db.query(Apartamento).filter(
            Apartamento.propietario_id == usuario_actual.id
        ).first()
        if not apto:
            raise HTTPException(status_code=404, detail="No tiene apartamento registrado")

        recibo = db.query(Recibo).filter(
            Recibo.id == recibo_id,
            Recibo.apartamento_id == apto.id,
        ).first()
        if not recibo:
            raise HTTPException(status_code=404, detail="Recibo no encontrado o no le pertenece")
        if recibo.estado_pago == "pagado":
            raise HTTPException(status_code=400, detail="Este recibo ya está completamente pagado")

        tasa = obtener_tasa_actual(db)
        if moneda_pago == "VES":
            monto_usd = convertir_ves_a_usd(monto_declarado, tasa.tasa_usd_ves)
        else:
            monto_usd = monto_declarado

        comprobante_url = await subir_comprobante(comprobante, apto.id)

        try:
            from sqlalchemy import text
            db.execute(text("ALTER TABLE pagos ALTER COLUMN comprobante_url TYPE TEXT;"))
            db.commit()
        except Exception:
            pass

        pago = Pago(
            apartamento_id=apto.id,
            recibo_id=recibo_id,
            metodo_pago=metodo_pago,
            banco_origen=banco_origen,
            referencia_bancaria=referencia_bancaria,
            monto_declarado=monto_declarado,
            moneda_pago=moneda_pago,
            tasa_bcv_aplicada=tasa.tasa_usd_ves,
            monto_equivalente_usd=monto_usd,
            comprobante_url=comprobante_url,
            estado_conciliacion="en_revision",
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)
        return pago

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error en servidor al guardar pago: {str(e)}")
