const express = require('express');
const cors = require('cors');
const QRCode = require('qrcode');
const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion,
    Browsers
} = require('@whiskeysockets/baileys');
const pino = require('pino');
const fs = require('fs');

const app = express();
app.use(cors());
app.use(express.json());

let sock = null;
let qrCodeImage = null;
let isConnected = false;
let sessionInfo = null;

const logger = pino({ level: 'silent' });

async function connectToWhatsApp() {
    try {
        const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
        const { version, isLatest } = await fetchLatestBaileysVersion();
        console.log(`Usando Baileys v${version.join('.')}, isLatest: ${isLatest}`);

        sock = makeWASocket({
            version,
            logger,
            printQRInTerminal: false,
            auth: state,
            browser: Browsers.macOS('Desktop'),
            syncFullHistory: false,
            connectTimeoutMs: 60000,
            defaultQueryTimeoutMs: 60000,
            keepAliveIntervalMs: 10000,
        });

        sock.ev.on('creds.update', saveCreds);

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                try {
                    // Genera imagen QR nítida en tiempo real
                    qrCodeImage = await QRCode.toDataURL(qr, { margin: 2, scale: 6 });
                    isConnected = false;
                    console.log('📱 Nuevo código QR Baileys generado.');
                } catch (err) {
                    console.error('Error generando QR:', err);
                }
            }

            if (connection === 'close') {
                const statusCode = (lastDisconnect?.error)?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
                console.log(`Conexión cerrada (status ${statusCode}). Reconectando:`, shouldReconnect);
                
                isConnected = false;
                qrCodeImage = null;
                sessionInfo = null;

                if (statusCode === DisconnectReason.loggedOut) {
                    // Limpiar auth si fue desvinculado
                    try {
                        fs.rmSync('auth_info_baileys', { recursive: true, force: true });
                    } catch (e) {}
                }

                setTimeout(() => {
                    connectToWhatsApp();
                }, 3000);
            } else if (connection === 'open') {
                console.log('✅ WhatsApp Conectado exitosamente como línea del condominio.');
                isConnected = true;
                qrCodeImage = null;
                sessionInfo = {
                    id: sock.user?.id || 'Línea Conectada',
                    name: sock.user?.name || 'Administración Edificio Alcatraz'
                };
            }
        });
    } catch (err) {
        console.error('Error al inicializar socket de WhatsApp:', err);
        setTimeout(connectToWhatsApp, 5000);
    }
}

// Iniciar conexión al levantar el servicio
connectToWhatsApp();

// ── Endpoints REST para FastAPI y Vue ──

// Estado actual y QR
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        qr: qrCodeImage,
        session: sessionInfo
    });
});

// Desconectar / Cerrar sesión para cambiar de número o limpiar sesión
app.post('/logout', async (req, res) => {
    try {
        if (sock) {
            try { await sock.logout(); } catch (e) {}
        }
        isConnected = false;
        qrCodeImage = null;
        sessionInfo = null;
        try {
            fs.rmSync('auth_info_baileys', { recursive: true, force: true });
        } catch (e) {}
        setTimeout(connectToWhatsApp, 1000);
        res.json({ status: 'ok', message: 'Sesión de WhatsApp reseteada. Generando nuevo código QR...' });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Endpoint para solicitar nuevo QR forzadamente
app.post('/refresh-qr', async (req, res) => {
    try {
        if (sock) {
            try { sock.end(); } catch (e) {}
        }
        qrCodeImage = null;
        setTimeout(connectToWhatsApp, 500);
        res.json({ status: 'ok', message: 'Regenerando código QR...' });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Envío de mensaje individual
app.post('/send-message', async (req, res) => {
    const { phone, message } = req.body;
    if (!isConnected || !sock) {
        return res.status(400).json({ error: 'WhatsApp no está vinculado. Escanea el código QR primero.' });
    }

    try {
        let cleanPhone = phone.replace(/\D/g, '');
        if (!cleanPhone.startsWith('58') && cleanPhone.length === 10) {
            cleanPhone = '58' + cleanPhone;
        }
        const jid = `${cleanPhone}@s.whatsapp.net`;
        await sock.sendMessage(jid, { text: message });
        res.json({ success: true, jid });
    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        res.status(500).json({ error: error.message });
    }
});

const PORT = 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🤖 Microservicio WhatsApp corriendo en puerto ${PORT}`);
});
