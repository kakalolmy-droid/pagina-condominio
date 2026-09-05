"""Servicio de sincronización persistente de la sesión de WhatsApp con PostgreSQL."""
import os
import glob
from app.database import SessionLocal
from app.models.whatsapp_session import WhatsAppSessionFile


def get_auth_dirs():
    """Retorna las rutas posibles donde se guarda auth_info_baileys."""
    posibles = [
        "/app/whatsapp_service/auth_info_baileys",
        os.path.join(os.getcwd(), "whatsapp_service", "auth_info_baileys"),
        os.path.join(os.getcwd(), "backend", "whatsapp_service", "auth_info_baileys"),
        os.path.join(os.path.dirname(__file__), "..", "..", "whatsapp_service", "auth_info_baileys"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "whatsapp_service", "auth_info_baileys"),
    ]
    rutas_validas = []
    for p in posibles:
        norm = os.path.normpath(p)
        if norm not in rutas_validas:
            rutas_validas.append(norm)
    return rutas_validas


def restaurar_archivos_sesion():
    """
    Restaura los archivos de sesión de WhatsApp desde PostgreSQL hacia el disco.
    Se ejecuta al iniciar el contenedor antes de levantar Node.js.
    """
    db = SessionLocal()
    try:
        registros = db.query(WhatsAppSessionFile).all()
        if not registros:
            print("ℹ️ No hay archivos de sesión de WhatsApp guardados en PostgreSQL.")
            return

        for auth_dir in get_auth_dirs():
            parent = os.path.dirname(auth_dir)
            if os.path.isdir(parent) or auth_dir.startswith("/app"):
                try:
                    os.makedirs(auth_dir, exist_ok=True)
                    for reg in registros:
                        filepath = os.path.join(auth_dir, reg.filename)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(reg.content)
                    print(f"✅ Sesión restaurada: {len(registros)} archivos volcados a {auth_dir}")
                except Exception as ex:
                    print(f"⚠️ No se pudo escribir en {auth_dir}: {ex}")
    except Exception as e:
        print("⚠️ Error restaurando sesión de WhatsApp desde PostgreSQL:", e)
    finally:
        db.close()


def obtener_archivos_sesion_dict() -> dict[str, str]:
    """Retorna un diccionario { filename: content } con todos los archivos guardados en PostgreSQL."""
    db = SessionLocal()
    try:
        registros = db.query(WhatsAppSessionFile).all()
        return {r.filename: r.content for r in registros}
    finally:
        db.close()


def guardar_archivos_sesion_dict(files_dict: dict[str, str]):
    """Guarda o actualiza archivos de sesión en PostgreSQL."""
    if not files_dict:
        return
    db = SessionLocal()
    try:
        for filename, content in files_dict.items():
            reg = db.query(WhatsAppSessionFile).filter(WhatsAppSessionFile.filename == filename).first()
            if reg:
                reg.content = content
            else:
                db.add(WhatsAppSessionFile(filename=filename, content=content))
        db.commit()
    except Exception as e:
        db.rollback()
        print("⚠️ Error guardando archivos de sesión en PostgreSQL:", e)
    finally:
        db.close()


def limpiar_archivos_sesion():
    """Borra todos los archivos de sesión de la base de datos (por ejemplo, al desvincular)."""
    db = SessionLocal()
    try:
        db.query(WhatsAppSessionFile).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print("⚠️ Error limpiando sesión de WhatsApp en PostgreSQL:", e)
    finally:
        db.close()
