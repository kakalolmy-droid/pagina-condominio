from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Base de datos
    database_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Cloudinary
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    # Twilio WhatsApp
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # Resend Email
    resend_api_key: str = ""
    email_from: str = "notificaciones@edificioalcatraz.com"

    # Condominio
    condominio_nombre: str = "Edificio Alcatraz"
    condominio_rif: str = ""
    condominio_banco: str = ""
    condominio_cuenta: str = ""
    condominio_pago_movil: str = ""
    condominio_portal_url: str = "https://alcatraz.vercel.app"

    # BCV
    bcv_url: str = "https://www.bcv.org.ve/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
