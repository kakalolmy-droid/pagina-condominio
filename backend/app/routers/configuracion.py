"""Configuración global del condominio (datos bancarios oficiales, cuentas y mensajes predeterminados)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.configuracion import ConfiguracionCondominio
from app.schemas.configuracion import DatosBancariosOut, DatosBancariosUpdate
from app.auth.dependencies import get_usuario_actual, require_admin
from app.config import get_settings

router = APIRouter(prefix="/api/configuracion", tags=["Configuración"])
settings = get_settings()


def _obtener_o_crear_config(db: Session) -> ConfiguracionCondominio:
    config = db.query(ConfiguracionCondominio).first()
    if not config:
        config = ConfiguracionCondominio(
            banco=settings.condominio_banco or "Banco de Venezuela (0102)",
            pago_movil=settings.condominio_pago_movil or "0414-1234567 | C.I. V-00000001",
            cuenta_transferencia=settings.condominio_cuenta or "0102-0000-00-0000000000",
            zelle="pagos@edificioalcatraz.com",
            nota_predeterminada="Recordamos reportar su comprobante de pago a través de la plataforma para validar su solvencia.",
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.get("/datos-bancarios", response_model=DatosBancariosOut)
def obtener_datos_bancarios(
    db: Session = Depends(get_db),
    _=Depends(get_usuario_actual),
):
    """
    Retorna los datos bancarios y de recaudación oficiales del condominio.
    Accesible para todos los usuarios autenticados (propietarios y administradores).
    """
    return _obtener_o_crear_config(db)


@router.post("/datos-bancarios", response_model=DatosBancariosOut)
def guardar_datos_bancarios(
    payload: DatosBancariosUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Actualiza permanentemente los datos bancarios y de recaudación del condominio.
    Solo administradores.
    """
    config = _obtener_o_crear_config(db)

    if payload.banco is not None:
        config.banco = payload.banco
    if payload.pago_movil is not None:
        config.pago_movil = payload.pago_movil
    if payload.cuenta_transferencia is not None:
        config.cuenta_transferencia = payload.cuenta_transferencia
    if payload.zelle is not None:
        config.zelle = payload.zelle
    if payload.nota_predeterminada is not None:
        config.nota_predeterminada = payload.nota_predeterminada

    db.commit()
    db.refresh(config)
    return config
