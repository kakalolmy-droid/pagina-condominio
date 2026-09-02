from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.bcv_scraper import actualizar_tasa_bcv, obtener_tasa_actual
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/tasa", tags=["Tasa BCV"])


@router.get("/actual")
async def get_tasa_actual(db: Session = Depends(get_db)):
    """Retorna la tasa BCV más reciente almacenada en la DB."""
    try:
        tasa = obtener_tasa_actual(db)
        return {
            "fecha": tasa.fecha,
            "tasa_usd_ves": float(tasa.tasa_usd_ves),
            "fecha_registro": tasa.fecha_registro,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sincronizar", dependencies=[Depends(require_admin)])
async def sincronizar_tasa(db: Session = Depends(get_db)):
    """
    Fuerza la sincronización inmediata de la tasa BCV.
    Solo accesible por admin o junta.
    """
    try:
        tasa = await actualizar_tasa_bcv(db)
        return {
            "mensaje": "Tasa BCV sincronizada correctamente",
            "fecha": tasa.fecha,
            "tasa_usd_ves": float(tasa.tasa_usd_ves),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al consultar el BCV: {str(e)}")


@router.get("/historial")
async def get_historial_tasas(
    limite: int = 30,
    db: Session = Depends(get_db),
):
    """Retorna el historial de tasas BCV de los últimos N días."""
    from app.models.tasa_bcv import TasaBCV
    tasas = (
        db.query(TasaBCV)
        .order_by(TasaBCV.fecha.desc())
        .limit(limite)
        .all()
    )
    return [
        {"fecha": t.fecha, "tasa_usd_ves": float(t.tasa_usd_ves)}
        for t in tasas
    ]
