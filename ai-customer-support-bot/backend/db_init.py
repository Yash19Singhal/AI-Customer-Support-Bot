# db_init.py
from sqlalchemy import create_engine, Column, String, Integer, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()
DB_PATH = "sqlite:///chat.db"

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    user_query = Column(Text)
    bot_reply = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    escalated = Column(Boolean, default=False)

class Escalation(Base):
    __tablename__ = "escalations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    user_query = Column(Text)
    reason = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    resolved = Column(Boolean, default=False)

def init_db():
    engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    print("DB initialized at chat.db")

if __name__ == "__main__":
    init_db()
