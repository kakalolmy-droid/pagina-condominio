"""
Generador de recibos PDF de solvencia usando WeasyPrint.
"""
from datetime import datetime
import uuid
from app.models.pago import Pago
from app.config import get_settings

settings = get_settings()


def _generar_html_solvencia(pago: Pago) -> str:
    """Genera el HTML del recibo de solvencia."""
    apto = pago.apartamento
    propietario = apto.propietario
    codigo = str(uuid.uuid4()).upper()[:16]
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    metodos = {
        "pago_movil": "Pago Móvil",
        "transferencia_ves": "Transferencia Bancaria (VES)",
        "zelle": "Zelle (USD)",
        "efectivo_usd": "Efectivo (USD)",
    }
    metodo_nombre = metodos.get(pago.metodo_pago, pago.metodo_pago)

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Arial', sans-serif; margin: 40px; color: #3D3D3D; background: #F7F5F0; }}
            .header {{ text-align: center; border-bottom: 3px solid #2D5A43; padding-bottom: 20px; margin-bottom: 30px; }}
            .titulo {{ color: #2D5A43; font-size: 28px; font-weight: bold; }}
            .subtitulo {{ color: #3B7A5C; font-size: 14px; }}
            .solvente {{ background: #27AE60; color: white; padding: 10px 20px; border-radius: 8px; font-size: 18px; font-weight: bold; display: inline-block; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
            .campo {{ margin-bottom: 10px; }}
            .etiqueta {{ font-size: 11px; color: #6B6B6B; text-transform: uppercase; }}
            .valor {{ font-size: 15px; font-weight: bold; color: #3D3D3D; }}
            .codigo {{ background: #EFECE4; border: 1px dashed #2D5A43; padding: 10px; text-align: center; font-family: monospace; font-size: 14px; letter-spacing: 2px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 11px; color: #6B6B6B; border-top: 1px solid #D4CFC5; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="titulo">🏢 {settings.condominio_nombre}</div>
            <div class="subtitulo">Recibo Digital de Solvencia</div>
            <br>
            <span class="solvente">✓ SOLVENTE</span>
        </div>

        <div class="grid">
            <div>
                <div class="campo"><div class="etiqueta">Propietario</div><div class="valor">{propietario.nombre if propietario else '-'} {propietario.apellido if propietario else ''}</div></div>
                <div class="campo"><div class="etiqueta">Cédula</div><div class="valor">{propietario.cedula if propietario else '-'}</div></div>
                <div class="campo"><div class="etiqueta">Apartamento</div><div class="valor">{apto.numero_apto} — Piso {apto.piso or "—"}</div></div>
            </div>
            <div>
                <div class="campo"><div class="etiqueta">Período Cancelado</div><div class="valor">{pago.recibo.mes_periodo if pago.recibo else '-'}</div></div>
                <div class="campo"><div class="etiqueta">Monto Pagado</div><div class="valor">${float(pago.monto_equivalente_usd):.2f} USD</div></div>
                <div class="campo"><div class="etiqueta">Método de Pago</div><div class="valor">{metodo_nombre}</div></div>
                <div class="campo"><div class="etiqueta">Referencia Bancaria</div><div class="valor">{pago.referencia_bancaria}</div></div>
                <div class="campo"><div class="etiqueta">Tasa BCV Aplicada</div><div class="valor">Bs. {float(pago.tasa_bcv_aplicada):.4f} / $1</div></div>
                <div class="campo"><div class="etiqueta">Fecha de Aprobación</div><div class="valor">{ahora}</div></div>
            </div>
        </div>

        <div class="codigo">Código de Validación: {codigo}</div>

        <div class="footer">
            Documento generado automáticamente por el sistema de gestión del {settings.condominio_nombre}<br>
            Este recibo tiene validez oficial. Conserve para sus registros.
        </div>
    </body>
    </html>
    """


def generar_pdf_solvencia(pago: Pago) -> bytes:
    """
    Genera el PDF del recibo de solvencia para un pago aprobado.
    Retorna los bytes del PDF.
    """
    from weasyprint import HTML
    html_content = _generar_html_solvencia(pago)
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
