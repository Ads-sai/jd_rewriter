import os
import time
import json
from collections import Counter
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import func
from jose import jwt, JWTError
from dotenv import load_dotenv

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth import create_access_token, SECRET_KEY
from app.database import engine, SessionLocal
from app.models import Base, JDRewriteLog
from app.models import JDRewriteLog   
from app.database import Base, engine

Base.metadata.create_all(bind=engine) 
from openai import OpenAI

# --- Environment & Setup ---
load_dotenv()
Base.metadata.create_all(bind=engine)
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(
        status_code=429, content={"detail": "Rate limit exceeded. Please try again later."}
    ),
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Models ---
class JDRequest(BaseModel):
    jd_text: str
    tone: str = "professional"

# --- Auth Endpoint ---
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "admin123":
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# --- Rewrite JD Endpoint ---
@app.post("/rewrite")
@limiter.limit("5/minute")
def rewrite_jd(
    request: Request,
    payload: JDRequest = Body(...),
    token: str = Depends(oauth2_scheme)
):
    # Auth
    try:
        payload_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload_data.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Prompt
    prompt = f"""
You are a job description rewriting assistant.

Take the following job description and rewrite it in three different styles. Format each rewrite clearly on separate lines:

1. Concise:
<short version here>

2. Inclusive:
<inclusive version here>

3. SEO-Optimized:
<SEO version here>

Tone: {payload.tone}

Job Description:
{payload.jd_text}

Respond exactly in this format, without combining them into paragraphs.
"""

    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        latency = (time.time() - start_time) * 1000  # in milliseconds
        full_output = response.choices[0].message.content

        # Log to DB
        db = SessionLocal()
        try:
            log = JDRewriteLog(
                tone=payload.tone,
                jd_text=payload.jd_text,
                rewritten_versions=full_output,
                latency_ms=latency
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

        return {"rewritten_versions": full_output}

    except Exception as e:
        print("🔥 OpenAI API error:", str(e))
        raise HTTPException(status_code=500, detail="LLM processing failed.")

# --- Root ---
@app.get("/")
def read_root():
    return {"message": "JD Rewriter API is live 🚀"}

# --- Metrics Endpoint ---
@app.get("/metrics")
def get_metrics():
    db = SessionLocal()

    total_requests = db.query(func.count(JDRewriteLog.id)).scalar()
    avg_latency = db.query(func.avg(JDRewriteLog.latency_ms)).scalar()
    tones = db.query(JDRewriteLog.tone).all()
    tone_counts = Counter([t[0] for t in tones])

    db.close()

    return JSONResponse({
        "total_requests": total_requests or 0,
        "average_latency_ms": round(avg_latency or 0),
        "top_tones": tone_counts
    })
