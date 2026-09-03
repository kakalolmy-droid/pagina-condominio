#!/bin/sh
set -e

PORT_TO_USE="${PORT:-8000}"

echo "🚀 Iniciando Microservicio de WhatsApp Baileys en puerto 3000..."
(cd /app/whatsapp_service && node server.js) &

echo "🏢 Iniciando API FastAPI en puerto $PORT_TO_USE..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT_TO_USE"
