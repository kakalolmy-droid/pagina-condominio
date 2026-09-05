from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from app.models import *  # noqa
from app.database import Base, engine, SessionLocal
from app.auth.jwt_handler import hash_password
from app.models.usuario import Usuario
from app.models.apartamento import Apartamento
from app.models.tasa_bcv import TasaBCV
from datetime import date
from decimal import Decimal
from app.routers import auth, tasa, usuarios, apartamentos, recibos, pagos, conciliacion, reportes, whatsapp_bot, configuracion
from app.models.whatsapp_session import WhatsAppSessionFile
from app.models.configuracion import ConfiguracionCondominio
from app.services.whatsapp_sync import restaurar_archivos_sesion
from app.config import get_settings

settings = get_settings()


def auto_seed_database():
    """Auto-inicializa tablas y datos de prueba si la base de datos está vacía (Cloud / Render)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Migraciones seguras independientes para PostgreSQL y SQLite
        migraciones = [
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
            "ALTER TABLE apartamentos ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
            "ALTER TABLE apartamentos ADD COLUMN IF NOT EXISTS meses_pendientes INTEGER DEFAULT 1;",
            "ALTER TABLE pagos ALTER COLUMN comprobante_url TYPE TEXT;",
            "CREATE TABLE IF NOT EXISTS whatsapp_session_files (filename VARCHAR(255) PRIMARY KEY, content TEXT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
            "ALTER TABLE configuracion_condominio ADD COLUMN IF NOT EXISTS telefono_whatsapp_emisor VARCHAR(50) DEFAULT '';",
        ]
        for sql in migraciones:
            try:
                with engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()
            except Exception:
                pass

        # Restaurar archivos de sesión de WhatsApp desde PostgreSQL
        try:
            restaurar_archivos_sesion()
        except Exception:
            pass

        admin = db.query(Usuario).filter(Usuario.email == "admin@alcatraz.com").first()
        if not admin:
            admin = Usuario(
                email="admin@alcatraz.com",
                password_hash=hash_password("admin123"),
                nombre="Administrador",
                apellido="Principal",
                cedula="V-00000001",
                telefono_whatsapp="+584120000000",
                rol="admin",
                activo=True,
            )
            db.add(admin)

            # Propietarios
            cesar = Usuario(
                email="fariascba@gmail.com",
                password_hash=hash_password("admin123"),
                nombre="Cesar",
                apellido="Farias",
                cedula="V-12345678",
                telefono_whatsapp="+584127040138",
                rol="propietario",
                activo=True,
            )
            lormy = Usuario(
                email="lormym48@gmail.com",
                password_hash=hash_password("admin123"),
                nombre="Lormy",
                apellido="Moreno",
                cedula="V-87654321",
                telefono_whatsapp="+584226410044",
                rol="propietario",
                activo=True,
            )
            db.add_all([cesar, lormy])
            db.commit()

            # Apartamentos
            apto1 = Apartamento(
                numero_apto="2-6",
                piso="2",
                torre="A",
                alicuota=Decimal("15.00"),
                meses_pendientes=1,
                activo=True,
                propietario_id=cesar.id,
            )
            apto2 = Apartamento(
                numero_apto="2-5",
                piso="2",
                torre="A",
                alicuota=Decimal("15.00"),
                meses_pendientes=1,
                activo=True,
                propietario_id=lormy.id,
            )
            db.add_all([apto1, apto2])

            # Tasa
            tasa_ini = TasaBCV(fecha=date.today(), tasa_usd_ves=Decimal("798.326"))
            db.add(tasa_ini)
            db.commit()
            print("🌱 Base de datos auto-inicializada con usuarios de prueba en la nube.")
    except Exception as e:
        print(f"Nota en auto_seed: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    auto_seed_database()
    try:
        from app.services.bcv_scraper import actualizar_tasa_bcv
        from app.services.financiero import (
            verificar_facturacion_automatica_mensual,
            sincronizar_recibos_todos_apartamentos,
        )
        db = SessionLocal()
        await actualizar_tasa_bcv(db)
        verificar_facturacion_automatica_mensual(db)
        sincronizar_recibos_todos_apartamentos(db)
        db.close()
    except Exception as e:
        print(f"Nota en lifespan: {e}")
    print(f"🏢 {settings.condominio_nombre} — API iniciada con éxito en Render")
    yield
    print("🛑 API detenida")


app = FastAPI(
    title=f"API — {settings.condominio_nombre}",
    description="Plataforma integral de administración de condominio — Edificio Alcatraz",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Total ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_trace = traceback.format_exc()
    print("GLOBAL EXCEPTION:", error_trace)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error del servidor: {str(exc)}", "trace": error_trace.splitlines()[-4:]},
    )

# ─── ROUTERS ─────────────────────────────────────────────────────
app.include_router(auth.router)           # /api/auth/
app.include_router(tasa.router)           # /api/tasa/
app.include_router(usuarios.router)       # /api/usuarios/
app.include_router(apartamentos.router)   # /api/apartamentos/
app.include_router(recibos.router)        # /api/recibos/
app.include_router(pagos.router)          # /api/pagos/
app.include_router(conciliacion.router)   # /api/conciliacion/
app.include_router(reportes.router)       # /api/reportes/
app.include_router(whatsapp_bot.router)   # /api/whatsapp-bot/
app.include_router(configuracion.router)   # /api/configuracion/


@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
async def root():
    return {
        "sistema": settings.condominio_nombre,
        "version": "1.0.0",
        "estado": "operativo",
        "documentacion": "/docs",
    }


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
async def health_check():
    return {"status": "ok"}
