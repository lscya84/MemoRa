import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, DateTime, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite DB 파일 경로 (Docker 볼륨 마운트 고려)
DB_DIR = "data/db"
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR}/memora.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 모델 정의 (명세서 기반) ---
class SystemConfig(Base):
    __tablename__ = "system_configs"
    key = Column(String, primary_key=True)
    value = Column(String)

class Recording(Base):
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    duration = Column(Float)
    file_size = Column(Float) # MB 단위
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0) # 0: 미처리, 1: 처리완료

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, index=True)
    full_text = Column(Text)
    summary = Column(Text)
    tags = Column(String) 
    segments_json = Column(JSON) # 타임스탬프: [{start, end, text}, ...]
    version = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
# DB 초기화 함수
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # --- Zero-Config Migration: missing columns check ---
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('transcripts')]
    
    if 'updated_at' not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE transcripts ADD COLUMN updated_at DATETIME"))
            conn.commit()
            print("🚀 Migrated: Added 'updated_at' column to 'transcripts' table.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_setting(key, value):
    db = SessionLocal()
    try:
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = str(value)
        else:
            db.add(SystemConfig(key=key, value=str(value)))
        db.commit()
    finally:
        db.close()