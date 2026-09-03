const express = require('express');
const cors = require('cors');
const QRCode = require('qrcode');
const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    fetchLatestBaileysVersion
} = require('@whiskeysockets/baileys');
const pino = require('pino');

const app = express();
app.use(cors());
app.use(express.json());

let sock = null;
let qrCodeImage = null;
let isConnected = false;
let sessionInfo = null;

const logger = pino({ level: 'silent' });

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
        version,
        logger,
        printQRInTerminal: false,
        auth: state,
        browser: ['Edificio Alcatraz', 'Chrome', '1.0.0']
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            try {
                qrCodeImage = await QRCode.toDataURL(qr);
                isConnected = false;
                console.log('📱 Nuevo código QR generado para vinculación.');
            } catch (err) {
                console.error('Error generando QR:', err);
            }
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Conexión cerrada. Reconectando:', shouldReconnect);
            isConnected = false;
            qrCodeImage = null;
            sessionInfo = null;
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('✅ WhatsApp Conectado exitosamente como línea del condominio.');
            isConnected = true;
            qrCodeImage = null;
            sessionInfo = {
                id: sock.user?.id || 'Conectado',
                name: sock.user?.name || 'Línea Edificio Alcatraz'
            };
        }
    });
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

// Desconectar / Cerrar sesión para cambiar de número
app.post('/logout', async (req, res) => {
    try {
        if (sock) {
            await sock.logout();
            isConnected = false;
            qrCodeImage = null;
            sessionInfo = null;
            connectToWhatsApp();
        }
        res.json({ status: 'ok', message: 'Sesión de WhatsApp cerrada. Listo para nuevo escaneo.' });
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
