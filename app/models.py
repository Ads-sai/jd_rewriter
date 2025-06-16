from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class JDRewriteLog(Base):
    __tablename__ = "jd_rewrite_logs"

    id = Column(Integer, primary_key=True, index=True)
    tone = Column(String(50))
    jd_text = Column(Text)
    rewritten_versions = Column(Text)
    latency_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
