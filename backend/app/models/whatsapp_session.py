from sqlalchemy import Column, String, Text, DateTime, func
from app.database import Base


class WhatsAppSessionFile(Base):
    __tablename__ = "whatsapp_session_files"

    filename = Column(String(255), primary_key=True, index=True)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
