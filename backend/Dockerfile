FROM python:3.11-slim

WORKDIR /app

# Instalar Node.js 20 oficial, npm y curl
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependencias del servicio WhatsApp Baileys
COPY whatsapp_service/package.json ./whatsapp_service/
RUN cd whatsapp_service && npm install

# Copiar todo el código fuente
COPY . .

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
