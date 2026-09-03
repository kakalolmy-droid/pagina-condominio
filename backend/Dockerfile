FROM node:20-slim AS node-base

FROM python:3.11-slim

WORKDIR /app

# Instalar Node.js, npm y curl en el contenedor de Render
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependencias del servicio WhatsApp Baileys
COPY whatsapp_service/package.json ./whatsapp_service/
RUN cd whatsapp_service && npm install --production

# Copiar todo el código fuente
COPY . .

# Script de arranque simultáneo (Node WhatsApp + FastAPI)
RUN echo '#!/bin/sh\n\
cd /app/whatsapp_service && node server.js &\n\
cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
