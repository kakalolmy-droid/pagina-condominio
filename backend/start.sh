#!/bin/sh
set -e

echo "🚀 Iniciando Microservicio de WhatsApp Baileys en puerto 3000..."
(cd /app/whatsapp_service && node server.js) &

echo "🏢 Iniciando API FastAPI en puerto 8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
