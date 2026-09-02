# 🏢 Edificio Alcatraz — Plataforma de Administración de Condominio

Sistema web integral para gestión de condominios con panel administrativo, portal del propietario, conciliación de pagos y reportes.

## Stack Tecnológico (100% Gratuito)

| Capa | Tecnología | Hosting |
|------|-----------|---------|
| Frontend | Vue 3 + Vite + Tailwind CSS | Vercel (gratis) |
| Backend | Python FastAPI | Koyeb (gratis) |
| Base de datos | PostgreSQL | Supabase (gratis) |
| Comprobantes | Cloudinary | Gratis 25GB |
| Email | Resend.com | Gratis 3k/mes |
| WhatsApp | Twilio | Sandbox gratis |

## Estructura del Proyecto

```
Pagina Condominio/
├── backend/          ← FastAPI (Python)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   └── auth/
│   ├── alembic/      ← Migraciones de DB
│   ├── requirements.txt
│   └── Dockerfile    ← Para Koyeb
└── frontend/         ← Vue 3 (JavaScript)
    ├── src/
    │   ├── views/
    │   │   ├── admin/         ← Panel administrativo
    │   │   └── propietario/   ← Portal del residente
    │   ├── components/neumorph/  ← Componentes UI
    │   ├── stores/            ← Estado Pinia
    │   ├── services/          ← API Axios
    │   └── router/            ← Rutas con guards
    └── vercel.json   ← Para Vercel
```

## 🐳 Inicio con Docker (Recomendado — TODO simultáneo)

Con un solo comando se levantan **todos los servicios al mismo tiempo**:
- ✅ PostgreSQL (con datos persistentes)
- ✅ Redis (cola de notificaciones)
- ✅ FastAPI backend (con hot-reload)
- ✅ Celery worker (envío asíncrono)
- ✅ Vue 3 frontend (Nginx en producción)

```bash
# 1. Copiar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus claves (Cloudinary, Twilio, Resend)

# 2. PRODUCCIÓN — Levantar todo
docker compose up --build -d

# 3. DESARROLLO — Con hot-reload y Vite HMR
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Ver logs de todos los servicios en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f worker

# Detener todo (los datos se conservan en los volúmenes)
docker compose down

# Detener Y borrar datos (¡cuidado!)
docker compose down -v
```

### Servicios y Puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `frontend` | `http://localhost:80` | App web Vue 3 (Nginx) |
| `backend` | `http://localhost:8000` | API FastAPI + docs en `/docs` |
| `db` | `localhost:5432` | PostgreSQL (acceso con DBeaver) |
| `redis` | `localhost:6379` | Cola de tareas |
| `worker` | — | Celery (sin puerto, interno) |

### Volúmenes Persistentes (los datos nunca se pierden)

| Volumen | Qué guarda |
|---------|-----------|
| `alcatraz_postgres_data` | Base de datos completa |
| `alcatraz_redis_data` | Cola de tareas pendientes |
| `alcatraz_comprobantes` | Comprobantes de pago subidos |

---

## Inicio Manual (sin Docker)

### Backend

```bash
cd backend
cp .env.example .env
# Editar .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# → http://localhost:8000
# → Docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## Sprints de Desarrollo

- ✅ **Sprint 1**: Base del proyecto, modelos DB, autenticación JWT, scraper BCV
- 🔲 **Sprint 2**: Panel administrativo (propietarios, apartamentos, recibos)
- 🔲 **Sprint 3**: Portal del propietario (auto-reporte de pagos)
- 🔲 **Sprint 4**: Conciliación 1-clic y generación de solvencias PDF
- 🔲 **Sprint 5**: Exportación Excel/PDF y notificaciones masivas WhatsApp/Email

## URLs del Sistema

| Entorno | Frontend | Backend |
|---------|----------|---------|
| Desarrollo | http://localhost:5173 | http://localhost:8000 |
| Producción | https://alcatraz.vercel.app | https://tu-backend.koyeb.app |
