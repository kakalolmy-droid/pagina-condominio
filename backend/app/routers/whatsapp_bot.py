"""Servicio de gestión del Bot Autónomo de WhatsApp y emisión masiva."""
from fastapi import APIRouter, Depends, HTTPException
import httpx
from pydantic import BaseModel
from typing import Optional
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/whatsapp-bot", tags=["WhatsApp Bot"])

# Al correr juntos en el mismo contenedor en Render, se comunican por localhost
WPP_SERVICE_URL = "http://127.0.0.1:3000"


class PairingCodeRequest(BaseModel):
    phone: str


@router.get("/status")
async def obtener_estado_bot(_=Depends(require_admin)):
    """
    Obtiene el estado de conexión de WhatsApp y el Código QR si está pendiente de vinculación.
    """
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(f"{WPP_SERVICE_URL}/status")
            return res.json()
    except Exception as e:
        return {
            "connected": False,
            "qr": None,
            "session": None,
            "error": "Iniciando motor autónomo de WhatsApp..."
        }


@router.post("/request-pairing-code")
async def solicitar_codigo_vinculacion(payload: PairingCodeRequest, _=Depends(require_admin)):
    """
    Solicita un código de vinculación numérico de 8 dígitos para enlazar WhatsApp sin escanear cámara.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(f"{WPP_SERVICE_URL}/request-pairing-code", json={"phone": payload.phone})
            return res.json()
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
async def desvincular_numero(_=Depends(require_admin)):
    """
    Desvincula el número actual para que la junta o administrador pueda vincular uno nuevo.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(f"{WPP_SERVICE_URL}/logout")
            return res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
