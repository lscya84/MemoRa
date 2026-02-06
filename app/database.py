import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

# 데이터 저장 경로 (Docker 내부 경로 기준)
# 로컬 테스트 시에는 프로젝트 루트의 data/db 폴더 사용
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "../data/db")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = f"sqlite:///{os.path.join(DB_DIR, 'memora.db')}"

Base = declarative_base()

# 1. 시스템 설정 테이블 (웹 UI에서 제어)
class SystemConfig(Base):
    __tablename__ = "system_configs"
    key = Column(String, primary_key=True)  # 예: 'ai_device', 'telegram_token'
    value = Column(String)                  # 예: 'cuda', '1234:ABC...'

# 2. 녹음 파일 테이블
class Recording(Base):
    __tablename__ = "recordings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, nullable=False) # 저장된 파일 경로
    filename = Column(String)                  # 원본 파일명
    file_size = Column(Integer)                # 파일 크기 (bytes)
    duration = Column(Integer)                 # 재생 시간 (초)
    source = Column(String)                    # telegram, web, drive
    created_at = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False) # 처리 완료 여부
    
    transcripts = relationship("Transcript", back_populates="recording", cascade="all, delete-orphan")

# 3. 스크립트 & 요약 테이블 (버전 관리 지원)
class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recording_id = Column(Integer, ForeignKey("recordings.id"))
    version = Column(Integer, default=1)       # 1=AI초안, 2=수정본...
    
    full_text = Column(Text)                   # 전체 스크립트
    summary = Column(Text)                     # 요약 내용
    tags = Column(String)                      # #태그 #키워드
    segments_json = Column(JSON)               # 싱크용 타임스탬프 데이터
    
    is_final = Column(Boolean, default=True)   # 현재 대표 버전인지 여부
    created_at = Column(DateTime, default=datetime.now)
    
    recording = relationship("Recording", back_populates="transcripts")

# DB 초기화 및 세션 생성
def init_db():
    engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()

if __name__ == "__main__":
    init_db()
    print(f"✅ 데이터베이스가 성공적으로 생성되었습니다: {DB_PATH}")