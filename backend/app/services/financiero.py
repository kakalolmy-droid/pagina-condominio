"""
Servicio financiero: cálculo de cuotas por cuota fija / alícuota,
emisión masiva de recibos y construcción de la matriz de deudas.
"""
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.apartamento import Apartamento
from app.models.recibo import Recibo
from app.services.bcv_scraper import obtener_tasa_actual
from app.schemas.recibo import EmisionMasivaRequest


def emitir_recibos_mes(db: Session, request: EmisionMasivaRequest) -> list[Recibo]:
    """
    Emite un recibo por cada apartamento ACTIVO para el período indicado.
    Si ya existe un recibo para ese período y apartamento, lo omite.
    """
    apartamentos = db.query(Apartamento).filter(Apartamento.activo == True).all()
    recibos_emitidos = []
    hoy = date.today()
    vencimiento = hoy + timedelta(days=request.dias_vencimiento)

    for apto in apartamentos:
        # Si el propietario está inactivo, omitir emisión
        if apto.propietario and not apto.propietario.activo:
            continue

        existente = db.query(Recibo).filter(
            Recibo.apartamento_id == apto.id,
            Recibo.mes_periodo == request.periodo,
        ).first()
        if existente:
            continue

        monto = Decimal(str(apto.alicuota)) if (apto.alicuota and apto.alicuota > 0) else Decimal("15.00")
        
        recibo = Recibo(
            apartamento_id=apto.id,
            mes_periodo=request.periodo,
            monto_total_usd=monto,
            monto_pendiente_usd=monto,
            estado_pago="pendiente",
            fecha_emision=hoy,
            fecha_vencimiento=vencimiento,
        )
        db.add(recibo)
        recibos_emitidos.append(recibo)

    db.commit()
    for r in recibos_emitidos:
        db.refresh(r)
    return recibos_emitidos


def obtener_matriz_deudas(db: Session) -> list[dict]:
    """
    Genera la matriz completa de deudas de todos los apartamentos.
    Calcula la deuda multiplicando la cuota mensual por los meses pendientes.
    """
    try:
        tasa = obtener_tasa_actual(db)
        tasa_valor = tasa.tasa_usd_ves
    except ValueError:
        tasa_valor = Decimal("0")

    apartamentos = db.query(Apartamento).all()
    matriz = []

    for apto in apartamentos:
        cuota_mensual = float(apto.alicuota or 15.0)
        meses_pend = int(apto.meses_pendientes if apto.meses_pendientes is not None else 1)
        
        deuda_usd = round(cuota_mensual * meses_pend, 2)
        deuda_ves = round(deuda_usd * float(tasa_valor), 2) if tasa_valor else 0.0
        estado = "solvente" if meses_pend == 0 else "moroso"

        matriz.append({
            "apartamento_id": apto.id,
            "numero_apto": apto.numero_apto,
            "piso": apto.piso,
            "torre": apto.torre,
            "cuota_mensual_usd": cuota_mensual,
            "meses_pendientes": meses_pend,
            "activo": bool(apto.activo),
            "propietario": f"{apto.propietario.nombre} {apto.propietario.apellido}" if apto.propietario else "-",
            "telefono": apto.propietario.telefono_whatsapp if apto.propietario else "-",
            "email": apto.propietario.email if apto.propietario else "-",
            "deuda_total_usd": deuda_usd,
            "deuda_total_ves": deuda_ves,
            "saldo_favor_usd": float(apto.saldo_favor_usd or 0),
            "meses_adeudados": [f"{meses_pend} mes(es)"],
            "estado": estado,
        })

    return sorted(matriz, key=lambda x: x["estado"] != "moroso")
