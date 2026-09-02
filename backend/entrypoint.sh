#!/bin/sh
# ================================================================
#  entrypoint.sh — Script de inicio del backend
#  1. Espera a que PostgreSQL esté listo
#  2. Ejecuta las migraciones de Alembic automáticamente
#  3. Inicia el servidor FastAPI o el worker Celery
# ================================================================

set -e

echo "⏳ Esperando a que la base de datos esté lista..."
while ! python -c "
import psycopg2, os, sys
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; do
    echo "   DB no disponible, reintentando en 2s..."
    sleep 2
done

echo "✅ Base de datos lista"

echo "🔄 Ejecutando migraciones Alembic..."
alembic upgrade head
echo "✅ Migraciones aplicadas"

echo "🚀 Iniciando servicio: $@"
exec "$@"
