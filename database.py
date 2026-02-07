import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite DB 파일 생성
DATABASE_URL = "sqlite:///memora.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 모델 정의 (명세서 기반) ---
class Recording(Base):
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    duration = Column(Float)
    file_size = Column(Float) # MB 단위
    created_at = Column(DateTime, default=datetime.now)
    processed = Column(Integer, default=0) # 0: 미처리, 1: 처리완료

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, index=True)
    full_text = Column(Text)
    summary = Column(Text)
    tags = Column(String) # JSON string or comma separated
    segments_json = Column(JSON) # 타임스탬프
    version = Column(Integer, default=1)
    
# DB 초기화 함수
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()