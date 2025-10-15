
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_init import Chat, Escalation, Base
from faq_loader import FAQStore
from model_utils import llm_fallback
import os

DB_PATH = "sqlite:///chat.db"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="AI Customer Support Bot API")


FAQ_CSV = Path(__file__).parent / "faqs.csv"
faq_store = FAQStore(str(FAQ_CSV))


class AskRequest(BaseModel):
    query: str
    session_id: str = None

class AskResponse(BaseModel):
    session_id: str
    reply: str
    source: str
    score: float = None

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

def store_chat(session_id, user_query, bot_reply, escalated=False):
    db = SessionLocal()
    c = Chat(session_id=session_id, user_query=user_query, bot_reply=bot_reply, escalated=escalated)
    db.add(c)
    db.commit()
    db.close()

def create_escalation(session_id, user_query, reason="low_confidence"):
    db = SessionLocal()
    e = Escalation(session_id=session_id, user_query=user_query, reason=reason)
    db.add(e)
    db.commit()
    db.close()

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    query = req.query.strip()
    session_id = req.session_id or str(uuid.uuid4())

  
    for i, q in enumerate(faq_store.questions):
        if query.lower() == q.lower():
            answer = faq_store.answers[i]
            store_chat(session_id, query, answer, escalated=False)
            return {"session_id": session_id, "reply": answer, "source": "faq_exact", "score": 1.0}

    
    nearest = faq_store.nearest(query, top_k=3)
    best = nearest[0]
    score = best['score']  

    CONFIDENCE_THRESHOLD = 0.45 
    if score >= CONFIDENCE_THRESHOLD:
        reply = best['answer']
        store_chat(session_id, query, reply, escalated=False)
        return {"session_id": session_id, "reply": reply, "source": "faq_sim", "score": score}

    
    llm_reply = llm_fallback(query, context="; ".join([f"{r['question']}" for r in nearest]))
    if llm_reply:
        
        low_confidence_phrases = ["i don't know", "i'm not sure", "can't find"]
        if any(p in llm_reply.lower() for p in low_confidence_phrases):
            create_escalation(session_id, query, reason="llm_low_confidence")
            esc_msg = "I couldn't confidently answer that — escalating to a human agent."
            store_chat(session_id, query, esc_msg, escalated=True)
            return {"session_id": session_id, "reply": esc_msg, "source": "escalation", "score": 0.0}
        store_chat(session_id, query, llm_reply, escalated=False)
        return {"session_id": session_id, "reply": llm_reply, "source": "llm", "score": score}

    
    create_escalation(session_id, query, reason="low_similarity")
    esc_msg = "I couldn't confidently answer that — I'll connect you to a human agent."
    store_chat(session_id, query, esc_msg, escalated=True)
    return {"session_id": session_id, "reply": esc_msg, "source": "escalation", "score": score}

@app.get("/history/{session_id}")
def history(session_id: str):
    db = SessionLocal()
    chats = db.query(Chat).filter(Chat.session_id == session_id).order_by(Chat.timestamp).all()
    db.close()
    return [{"user_query": c.user_query, "bot_reply": c.bot_reply, "timestamp": c.timestamp.isoformat(), "escalated": c.escalated} for c in chats]

@app.post("/escalate")
def escalate(payload: dict):
   
    session_id = payload.get("session_id")
    user_query = payload.get("user_query", "")
    reason = payload.get("reason", "manual")
    create_escalation(session_id, user_query, reason=reason)
    return {"status":"ok", "message":"escalation logged"}
