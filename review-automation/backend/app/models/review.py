from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON, Enum as SAEnum
import enum
from app.database import Base


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(64), nullable=False)
    external_id = Column(String(128), unique=True, nullable=True)
    author = Column(String(256), nullable=True)
    rating = Column(Integer, nullable=True)
    title = Column(String(512), nullable=True)
    body = Column(Text, nullable=False)
    language = Column(String(16), default="en")
    received_at = Column(DateTime, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow, index=True)

    sentiment = Column(String(16), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    topics = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    draft_response = Column(Text, nullable=True)

    analysis_status = Column(
        SAEnum(AnalysisStatus, name="analysisstatus"),
        default=AnalysisStatus.pending,
    )
    routed_to = Column(String(64), nullable=True)
    routed_at = Column(DateTime, nullable=True)
    is_escalated = Column(Boolean, default=False)
    response_sent = Column(Boolean, default=False)
