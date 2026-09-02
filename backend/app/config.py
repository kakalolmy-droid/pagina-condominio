from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Base de datos (con fallback automático a SQLite local persistente si no se configura PostgreSQL en la nube)
    database_url: str = "sqlite:///./alcatraz_cloud.db"

    # Redis (opcional para la nube)
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "clave-secreta-super-segura-edificio-alcatraz-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Cloudinary (opcional)
    cloudinary_cloud_name: str = "demo-alcatraz"
    cloudinary_api_key: str = "123456789012345"
    cloudinary_api_secret: str = "abcdefghijklmnopqrstuvwxyz1234"

    # Twilio / Notificaciones
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # Resend Email
    resend_api_key: str = ""
    email_from: str = "notificaciones@edificioalcatraz.com"

    # Condominio
    condominio_nombre: str = "Edificio Alcatraz"
    condominio_rif: str = ""
    condominio_banco: str = "Banco de Venezuela (0102)"
    condominio_cuenta: str = "0102-0000-00-0000000000"
    condominio_pago_movil: str = "0414-1234567 | C.I. V-00000001"
    condominio_portal_url: str = "https://pagina-condominio.vercel.app"

    # BCV
    bcv_url: str = "https://www.bcv.org.ve/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
