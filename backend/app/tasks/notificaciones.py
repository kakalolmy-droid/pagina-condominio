"""
Tareas asíncronas de notificaciones.
Estas funciones se ejecutan en el worker de Celery (contenedor separado),
no bloquean el servidor FastAPI principal.
"""
from app.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_whatsapp(self, telefono: str, mensaje: str):
    """Envía un mensaje de WhatsApp vía Twilio."""
    try:
        from app.config import get_settings
        from twilio.rest import Client

        settings = get_settings()
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        message = client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=f"whatsapp:{telefono}",
            body=mensaje,
        )
        logger.info(f"WhatsApp enviado a {telefono} | SID: {message.sid}")
        return {"status": "enviado", "sid": message.sid}

    except Exception as exc:
        logger.error(f"Error enviando WhatsApp a {telefono}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_email(self, destinatario: str, asunto: str, html_body: str):
    """Envía un email vía Resend.com."""
    try:
        import resend
        from app.config import get_settings

        settings = get_settings()
        resend.api_key = settings.resend_api_key

        params = {
            "from": settings.email_from,
            "to": [destinatario],
            "subject": asunto,
            "html": html_body,
        }
        response = resend.Emails.send(params)
        logger.info(f"Email enviado a {destinatario} | ID: {response['id']}")
        return {"status": "enviado", "id": response["id"]}

    except Exception as exc:
        logger.error(f"Error enviando email a {destinatario}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def enviar_cobro_masivo(periodo: str):
    """
    Envía avisos de cobro a TODOS los propietarios con deuda pendiente.
    Se ejecuta de forma asíncrona sin bloquear la API.
    """
    from app.database import SessionLocal
    from app.models.apartamento import Apartamento
    from app.models.recibo import Recibo
    from app.models.usuario import Usuario
    from app.services.bcv_scraper import obtener_tasa_actual
    from app.config import get_settings
    from decimal import Decimal

    settings = get_settings()
    db = SessionLocal()

    try:
        tasa = obtener_tasa_actual(db)
        tasa_valor = float(tasa.tasa_usd_ves)

        recibos_pendientes = (
            db.query(Recibo)
            .join(Apartamento)
            .join(Usuario)
            .filter(
                Recibo.mes_periodo == periodo,
                Recibo.estado_pago.in_(["pendiente", "parcial"]),
            )
            .all()
        )

        enviados = 0
        for recibo in recibos_pendientes:
            apto = recibo.apartamento
            propietario = apto.propietario
            monto_usd = float(recibo.monto_pendiente_usd)
            monto_ves = round(monto_usd * tasa_valor, 2)
            saldo_favor = float(apto.saldo_favor_usd)

            mensaje = (
                f"Estimado/a {propietario.nombre} {propietario.apellido}, Apto {apto.numero_apto}:\n\n"
                f"Su estado de cuenta al período {periodo}:\n"
                f"• Deuda Total: ${monto_usd:.2f} (Bs. {monto_ves:,.2f} a tasa BCV: Bs. {tasa_valor:.4f})\n"
                f"• Saldo a Favor: ${saldo_favor:.2f}\n\n"
                f"Datos para pago:\n"
                f"- Banco: {settings.condominio_banco}\n"
                f"- Cuenta/Pago Móvil: {settings.condominio_cuenta}\n"
                f"- Cédula/RIF: {settings.condominio_rif}\n\n"
                f"Reporte su pago en: {settings.condominio_portal_url}/mi-cuenta/pagar\n\n"
                f"— {settings.condominio_nombre}"
            )

            # Encolar envío WhatsApp
            if propietario.telefono_whatsapp:
                enviar_whatsapp.delay(propietario.telefono_whatsapp, mensaje)

            # Encolar envío Email
            if propietario.email:
                html = f"<pre style='font-family:sans-serif'>{mensaje}</pre>"
                enviar_email.delay(
                    propietario.email,
                    f"Estado de Cuenta {periodo} — {settings.condominio_nombre}",
                    html,
                )

            enviados += 1

        logger.info(f"Cobro masivo {periodo}: {enviados} avisos encolados")
        return {"periodo": periodo, "avisos_encolados": enviados}

    finally:
        db.close()
