"""Servicio de gestión del Bot Autónomo de WhatsApp y emisión masiva."""
from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.configuracion import ConfiguracionCondominio
from app.services.whatsapp_sync import (
    obtener_archivos_sesion_dict,
    guardar_archivos_sesion_dict,
    limpiar_archivos_sesion,
)
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/whatsapp-bot", tags=["WhatsApp Bot"])

# Al correr juntos en el mismo contenedor en Render, se comunican por localhost
WPP_SERVICE_URL = "http://127.0.0.1:3000"


class PairingCodeRequest(BaseModel):
    phone: str


class PhonePayload(BaseModel):
    phone: str


class SessionFilesPayload(BaseModel):
    files: Dict[str, str]


@router.get("/status")
async def obtener_estado_bot(db: Session = Depends(get_db), _=Depends(require_admin)):
    """
    Obtiene el estado de conexión de WhatsApp, el Código QR y el número de teléfono oficial guardado.
    Detecta automáticamente el número real vinculado a la sesión de WhatsApp y lo persiste en PostgreSQL.
    """
    config = db.query(ConfiguracionCondominio).first()
    if not config:
        config = ConfiguracionCondominio()
        db.add(config)
        db.commit()
        db.refresh(config)

    saved_phone = config.telefono_whatsapp_emisor if config.telefono_whatsapp_emisor else ""
    if saved_phone == "04149998877":
        saved_phone = ""
        config.telefono_whatsapp_emisor = ""
        db.commit()

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(f"{WPP_SERVICE_URL}/status")
            data = res.json()

            # Extraer el número telefónico real vinculado a Baileys
            connected_phone = data.get("phone") or ""
            if not connected_phone and data.get("session") and isinstance(data["session"], dict):
                connected_phone = data["session"].get("phone") or ""
                if not connected_phone and data["session"].get("id"):
                    raw_id = str(data["session"]["id"])
                    if "@" in raw_id:
                        connected_phone = raw_id.split(":")[0].split("@")[0]

            if connected_phone == "04149998877":
                connected_phone = ""

            # Si el bot está conectado y detectamos el número real de la línea:
            if data.get("connected") and connected_phone:
                if not config.telefono_whatsapp_emisor or config.telefono_whatsapp_emisor == "04149998877":
                    config.telefono_whatsapp_emisor = connected_phone
                    db.commit()
                    saved_phone = connected_phone
                elif not saved_phone:
                    saved_phone = connected_phone

            data["saved_phone"] = saved_phone or connected_phone
            return data
    except Exception as e:
        return {
            "connected": False,
            "qr": None,
            "session": None,
            "saved_phone": saved_phone,
            "error": "Iniciando motor autónomo de WhatsApp..."
        }


@router.post("/save-phone")
def guardar_telefono(payload: PhonePayload, db: Session = Depends(get_db), _=Depends(require_admin)):
    """
    Guarda permanentemente el número de WhatsApp oficial del condominio en PostgreSQL.
    """
    config = db.query(ConfiguracionCondominio).first()
    if not config:
        config = ConfiguracionCondominio()
        db.add(config)
    phone_clean = payload.phone.strip()
    if phone_clean == "04149998877":
        phone_clean = ""
    config.telefono_whatsapp_emisor = phone_clean
    db.commit()
    return {"mensaje": "Teléfono guardado permanentemente", "phone": config.telefono_whatsapp_emisor}


@router.post("/request-pairing-code")
async def solicitar_codigo_vinculacion(
    payload: PairingCodeRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    """
    Solicita un código de vinculación numérico de 8 dígitos y guarda el número en PostgreSQL.
    """
    config = db.query(ConfiguracionCondominio).first()
    if not config:
        config = ConfiguracionCondominio()
        db.add(config)
    config.telefono_whatsapp_emisor = payload.phone.strip()
    db.commit()

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            res = await client.post(f"{WPP_SERVICE_URL}/request-pairing-code", json={"phone": payload.phone})
            data = res.json()
            data["saved_phone"] = config.telefono_whatsapp_emisor
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-qr")
async def refrescar_qr(_=Depends(require_admin)):
    """
    Fuerza la regeneración de un código QR nuevo y fresco.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(f"{WPP_SERVICE_URL}/refresh-qr")
            return res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def desvincular_numero(db: Session = Depends(get_db), _=Depends(require_admin)):
    """
    Desvincula el número actual y limpia los archivos de sesión y el número en PostgreSQL.
    """
    try:
        limpiar_archivos_sesion()
    except Exception:
        pass

    try:
        config = db.query(ConfiguracionCondominio).first()
        if config:
            config.telefono_whatsapp_emisor = ""
            db.commit()
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(f"{WPP_SERVICE_URL}/logout")
            return res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/internal/auto-save-connected-phone")
def auto_save_phone(payload: PhonePayload, db: Session = Depends(get_db)):
    """Guarda automáticamente el número real conectado desde Baileys a PostgreSQL."""
    phone = payload.phone.strip()
    if phone and phone != "04149998877":
        config = db.query(ConfiguracionCondominio).first()
        if not config:
            config = ConfiguracionCondominio()
            db.add(config)
        config.telefono_whatsapp_emisor = phone
        db.commit()
    return {"ok": True}


# ── Rutas internas para sincronización de sesión con el microservicio Node.js ──

@router.get("/internal/session-files")
def obtener_archivos_internos():
    """Retorna los archivos de sesión guardados en PostgreSQL para restaurar en Node.js."""
    return {"files": obtener_archivos_sesion_dict()}


@router.post("/internal/session-files")
def guardar_archivos_internos(payload: SessionFilesPayload):
    """Recibe archivos actualizados de auth_info_baileys desde Node.js y los guarda en PostgreSQL."""
    guardar_archivos_sesion_dict(payload.files)
    return {"ok": True, "archivos": len(payload.files)}


@router.delete("/internal/session-files")
def limpiar_archivos_internos():
    """Limpia los archivos de sesión en PostgreSQL."""
    limpiar_archivos_sesion()
    return {"ok": True}
