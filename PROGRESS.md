# MemoRa 개발 일지 (음성녹음 데이터베이스)



## Phase 1: Foundation (완료)
- [x] 프로젝트 초기화 (Git, 문서 생성)
- [x] 폴더 구조 생성 및 단일 Streamlit 아키텍처 확정
- [x] `requirements.txt` 및 `docker-compose.yml` 작성
- [x] `database.py` (SystemConfig 포함 DB 스키마 구현)

## Phase 2: Core Logic (진행 중)
- [x] `services.py` (FFmpeg 최적화 로직 및 Whisper 통합)
- [x] `services.py` (Ollama & OpenAI Refiner 연동)
- [x] `main.py` (Zero-Config DB 영속성 레이어)
- [x] `database.py` (SQLite Column 자동 생성 - Migration 로직)
- [ ] 텔레그램 봇 및 드라이브 감시 워커 구현 (Background Thread)



## Phase 3: Interface (진행 중)
- [x] Streamlit 웹 대시보드 (통합 대시보드, 분석/업로드 페이지)
- [x] 히스토리 아카이브 (DB 연동 완료)
- [x] 설정 페이지 (Zero-Config 구현 완료)
- [ ] 텔레그램 봇 연동
- [ ] 구글 드라이브 감시 워커 구현
