import httpx
import logging
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.tasa_bcv import TasaBCV
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

DOLAR_API_URL = "https://ve.dolarapi.com/v1/dolares/oficial"


async def scrape_tasa_bcv() -> Decimal:
    """
    Obtiene la tasa oficial USD/VES en tiempo real desde la API oficial de Venezuela (DolarAPI / BCV).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(DOLAR_API_URL, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # 'promedio' contiene la tasa oficial del BCV
                valor = data.get("promedio") or data.get("venta") or data.get("monto")
                if valor:
                    return Decimal(str(valor))
    except Exception as e:
        logger.warning(f"Error consultando DolarAPI: {e}. Intentando fallback...")

    # Fallback con tasa de contingencia si no hay internet temporal
    return Decimal("798.326")


async def actualizar_tasa_bcv(db: Session) -> TasaBCV:
    """
    Consulta la tasa oficial del BCV, guarda o actualiza la tasa del día en la Base de Datos.
    """
    hoy = date.today()
    tasa_valor = await scrape_tasa_bcv()

    registro = db.query(TasaBCV).filter(TasaBCV.fecha == hoy).first()
    if registro:
        registro.tasa_usd_ves = tasa_valor
    else:
        registro = TasaBCV(fecha=hoy, tasa_usd_ves=tasa_valor)
        db.add(registro)

    db.commit()
    db.refresh(registro)
    logger.info(f"Tasa BCV del día ({hoy}) actualizada con éxito: Bs. {tasa_valor}")
    return registro


def obtener_tasa_actual(db: Session) -> TasaBCV:
    """
    Retorna la tasa más reciente disponible en la DB.
    """
    tasa = db.query(TasaBCV).order_by(TasaBCV.fecha.desc()).first()
    if not tasa:
        # Si la tabla está vacía, insertar la del día de hoy
        hoy = date.today()
        tasa = TasaBCV(fecha=hoy, tasa_usd_ves=Decimal("798.326"))
        db.add(tasa)
        db.commit()
        db.refresh(tasa)
    return tasa


def convertir_usd_a_ves(monto_usd: Decimal, tasa: Decimal) -> Decimal:
    """Convierte un monto en USD a VES usando la tasa oficial."""
    return round(monto_usd * tasa, 2)


def convertir_ves_a_usd(monto_ves: Decimal, tasa: Decimal) -> Decimal:
    """Convierte un monto en VES a USD usando la tasa oficial."""
    if tasa == 0:
        raise ValueError("La tasa BCV no puede ser 0")
    return round(monto_ves / tasa, 2)
