"""Exportación de reportes Excel/PDF y generador masivo de cobranza WhatsApp."""
from fastapi import APIRouter, Depends, Response, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import urllib.parse
import httpx
import logging

from app.database import get_db
from app.services.excel_export import generar_excel_reporte
from app.services.bcv_scraper import obtener_tasa_actual, actualizar_tasa_bcv
from app.models.apartamento import Apartamento
from app.models.recibo import Recibo
from app.models.usuario import Usuario
from app.models.configuracion import ConfiguracionCondominio
from app.config import get_settings
from app.auth.dependencies import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/reportes", tags=["Reportes"])
settings = get_settings()

WPP_SERVICE_URL = "http://127.0.0.1:3000"


class SolicitudAvisosWhatsApp(BaseModel):
    periodo: str
    fecha_limite: str
    banco: Optional[str] = None
    pago_movil: Optional[str] = None
    transferencia: Optional[str] = None
    zelle: Optional[str] = None
    nota_adicional: Optional[str] = None


@router.get("/excel")
def exportar_excel(
    periodo: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Exporta el reporte del período como archivo Excel (.xlsx)."""
    excel_bytes = generar_excel_reporte(db, periodo)
    nombre = f"reporte_alcatraz_{periodo}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.post("/whatsapp/enviar-masivo-automatico")
async def enviar_masivo_automatico(
    payload: SolicitudAvisosWhatsApp,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Envía DIRECTA y AUTOMÁTICAMENTE a todos los teléfonos vinculados por WhatsApp
    con toda la información de recaudación, cuota, meses pendientes y total a pagar.
    """
    # 1. Validar estrictamente que la línea de WhatsApp del condominio esté vinculada
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            status_res = await client.get(f"{WPP_SERVICE_URL}/status")
            bot_data = status_res.json() if status_res.status_code == 200 else {}
            if not bot_data.get("connected", False):
                raise HTTPException(
                    status_code=400,
                    detail="⚠️ No se pueden enviar los avisos: La línea oficial de WhatsApp del condominio no está vinculada. Por favor escanea el código QR o vincula tu número arriba primero.",
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando estado de WhatsApp: {e}")
        raise HTTPException(
            status_code=400,
            detail="⚠️ La línea oficial de WhatsApp no se encuentra disponible o no está vinculada. Por favor vincula tu número de WhatsApp arriba primero.",
        )

    try:
        tasa = await actualizar_tasa_bcv(db)
    except Exception as e:
        logger.warning(f"Error actualizando tasa en vivo antes del envío: {e}")
        tasa = obtener_tasa_actual(db)
    tasa_valor = float(tasa.tasa_usd_ves)

    config = db.query(ConfiguracionCondominio).first()
    if config:
        if payload.banco:
            config.banco = payload.banco
        if payload.pago_movil:
            config.pago_movil = payload.pago_movil
        if payload.transferencia:
            config.cuenta_transferencia = payload.transferencia
        if payload.zelle:
            config.zelle = payload.zelle
        if payload.nota_adicional:
            config.nota_predeterminada = payload.nota_adicional
        db.commit()

    banco = payload.banco or (config.banco if config else None) or settings.condominio_banco or "Banco de Venezuela (0102)"
    pago_movil = payload.pago_movil or (config.pago_movil if config else None) or settings.condominio_pago_movil or "0414-1234567 | C.I. V-00000001"
    transferencia = payload.transferencia or (config.cuenta_transferencia if config else None) or settings.condominio_cuenta or "0102-0000-00-0000000000"
    zelle = payload.zelle or (config.zelle if config else None) or "pagos@edificioalcatraz.com"
    portal_url = "https://pagina-condominio.vercel.app/mi-cuenta/pagar"

    aptos = db.query(Apartamento).filter(
        Apartamento.propietario_id != None
    ).all()
    
    enviados_exitosos = []
    errores = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        for apto in aptos:
            # 1. Comprobación estricta de que el apartamento esté activo
            if not apto.activo or apto.activo in (0, "0", False, "false"):
                logger.info(f"Omitiendo Apto {apto.numero_apto}: apartamento desactivado.")
                continue

            # 2. Comprobación estricta de que el propietario esté activo y tenga teléfono
            p = apto.propietario
            if not p or not p.activo or p.activo in (0, "0", False, "false") or not p.telefono_whatsapp:
                logger.info(f"Omitiendo Apto {apto.numero_apto}: propietario desactivado o sin teléfono.")
                continue

            cuota_mes = float(apto.alicuota or 15.00)
            meses_pend = int(apto.meses_pendientes if apto.meses_pendientes is not None else 1)
            
            # Monto total calculado según la cuota y la cantidad de meses pendientes
            monto_usd = round(cuota_mes * meses_pend, 2)
            monto_ves = round(monto_usd * tasa_valor, 2)

            msg = (
                f"🏢 *{settings.condominio_nombre} — AVISO DE COBRO*\n\n"
                f"Estimado/a *{p.nombre} {p.apellido}* (Apto *{apto.numero_apto}*),\n\n"
                f"Le informamos el estado de su cuenta de condominio para el período *{payload.periodo}*:\n"
                f"💵 *Cuota Mensual:* ${cuota_mes:.2f} USD\n"
                f"📌 *Meses Pendientes:* {meses_pend} mes(es)\n"
                f"💰 *TOTAL A PAGAR:* ${monto_usd:.2f} USD\n"
                f"🇻🇪 *Equivalente en Bs:* {monto_ves:,.2f} VES (Tasa BCV: Bs. {tasa_valor:.4f})\n"
                f"📅 *Fecha Límite:* {payload.fecha_limite}\n\n"
                f"📌 *DATOS OFICIALES DE RECAUDACIÓN:*\n"
                f"• Banco: {banco}\n"
                f"• Pago Móvil: {pago_movil}\n"
                f"• Transferencia: {transferencia}\n"
                f"• Zelle: {zelle}\n\n"
                f"🔗 *Reporte su pago y suba su comprobante directamente aquí:*\n"
                f"{portal_url}\n\n"
                f"{payload.nota_adicional or '¡Gracias por su puntualidad y colaboración!'}"
            )

            tel_limpio = "".join(filter(str.isdigit, p.telefono_whatsapp))
            if not tel_limpio.startswith("58") and len(tel_limpio) == 10:
                tel_limpio = f"58{tel_limpio}"

            try:
                res = await client.post(
                    f"{WPP_SERVICE_URL}/send-message",
                    json={"phone": tel_limpio, "message": msg},
                )
                if res.status_code == 200:
                    enviados_exitosos.append(f"{p.nombre} {p.apellido} ({tel_limpio})")
                else:
                    errores.append(f"{p.nombre}: {res.text}")
            except Exception as e:
                errores.append(f"{p.nombre}: {str(e)}")

    if len(enviados_exitosos) == 0:
        detalle = errores[0] if errores else "No se encontraron propietarios activos con número de WhatsApp registrado para notificar."
        raise HTTPException(
            status_code=400,
            detail=f"No se pudo enviar ningún aviso: {detalle}",
        )

    return {
        "status": "enviado",
        "mensaje": f"¡Avisos de WhatsApp enviados con éxito a {len(enviados_exitosos)} propietarios activos!",
        "total_destinatarios": len(enviados_exitosos),
        "destinatarios": enviados_exitosos,
        "errores": errores,
    }
