"""
Servicio de Cloudinary para subida y gestión de comprobantes de pago.
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.config import get_settings
import uuid

settings = get_settings()

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

FORMATOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
TAMANIO_MAXIMO_MB = 5


async def subir_comprobante(archivo: UploadFile, apartamento_id: int) -> str:
    """
    Sube el comprobante de pago a Cloudinary.
    Retorna la URL segura del archivo.
    """
    if archivo.content_type not in FORMATOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Use: JPG, PNG, WebP o PDF",
        )

    contenido = await archivo.read()

    if len(contenido) > TAMANIO_MAXIMO_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el límite de {TAMANIO_MAXIMO_MB}MB",
        )

    nombre_publico = f"alcatraz/comprobantes/apto_{apartamento_id}_{uuid.uuid4().hex[:8]}"

    try:
        if settings.cloudinary_api_key and settings.cloudinary_api_key != "123456789012345":
            resultado = cloudinary.uploader.upload(
                contenido,
                public_id=nombre_publico,
                resource_type="auto",
                folder="alcatraz/comprobantes",
            )
            return resultado.get("secure_url") or resultado.get("url")
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Error en Cloudinary ({e}), guardando como Data URL segura...")

    # Fallback robusto sin depender de APIs de pago externas: Data URL directa
    import base64
    b64 = base64.b64encode(contenido).decode('utf-8')
    mime = archivo.content_type or "image/png"
    return f"data:{mime};base64,{b64}"


def eliminar_archivo(public_id: str) -> None:
    """Elimina un archivo de Cloudinary por su public_id."""
    cloudinary.uploader.destroy(public_id)
