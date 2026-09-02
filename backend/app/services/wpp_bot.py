import asyncio
import logging
from typing import List, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# URL del contenedor alcatraz_whatsapp en la red Docker
WPP_SERVICE_URL = "http://alcatraz_whatsapp:3000"


async def enviar_mensaje_directo(numero_telefono: str, mensaje: str) -> bool:
    """
    Envía un mensaje de WhatsApp a través del bot autónomo en Docker.
    """
    tel_limpio = "".join(filter(str.isdigit, numero_telefono))
    if not tel_limpio.startswith("58") and len(tel_limpio) == 10:
        tel_limpio = f"58{tel_limpio}"

    payload = {
        "phone": tel_limpio,
        "message": mensaje,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{WPP_SERVICE_URL}/send-message", json=payload)
            logger.info(f"Envío WhatsApp a {tel_limpio} - Status: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Error enviando mensaje WhatsApp a {tel_limpio}: {e}")
        return False


async def despachar_cobro_masivo_background(avisos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Envía automáticamente en bucle de segundo plano a TODOS los números registrados.
    """
    enviados = 0
    for aviso in avisos:
        try:
            ok = await enviar_mensaje_directo(aviso["telefono"], aviso["mensaje_texto"])
            if ok:
                enviados += 1
            await asyncio.sleep(0.5)  # Breve pausa para no saturar el canal
        except Exception as e:
            logger.error(f"Error despachando aviso a {aviso['telefono']}: {e}")

    return {"total": len(avisos), "enviados": enviados}
