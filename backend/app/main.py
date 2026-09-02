from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models import *  # noqa
from app.routers import auth, tasa, usuarios, apartamentos, recibos, pagos, conciliacion, reportes, whatsapp_bot
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🏢 {settings.condominio_nombre} — API iniciada")
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

# ─── CORS Total (Permite cualquier origen para entorno de desarrollo) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── ROUTERS — Un archivo por módulo ──────────────────────────────
app.include_router(auth.router)           # /api/auth/
app.include_router(tasa.router)           # /api/tasa/
app.include_router(usuarios.router)       # /api/usuarios/
app.include_router(apartamentos.router)   # /api/apartamentos/
app.include_router(recibos.router)        # /api/recibos/
app.include_router(pagos.router)          # /api/pagos/
app.include_router(conciliacion.router)   # /api/conciliacion/
app.include_router(reportes.router)       # /api/reportes/
app.include_router(whatsapp_bot.router)   # /api/whatsapp-bot/


@app.get("/", tags=["Root"])
async def root():
    return {
        "sistema": settings.condominio_nombre,
        "version": "1.0.0",
        "estado": "operativo",
        "documentacion": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de salud para Koyeb y Docker healthcheck."""
    return {"status": "ok"}
