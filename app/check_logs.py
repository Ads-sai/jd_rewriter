import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import JDRewriteLog

db = SessionLocal()
logs = db.query(JDRewriteLog).all()

for log in logs:
    print("\n====================")
    print(f"User: {log.username}")
    print(f"Tone: {log.tone}")
    print(f"Latency: {log.latency_ms}ms")
    print(f"JD Text: {log.jd_text[:60]}...")
    print(f"Response:\n{log.response[:150]}...")
    print(f"Timestamp: {log.timestamp}")
    print("====================\n")

db.close()
