\# 기술 명세서



\## 1. 아키텍처

\- \*\*Language:\*\* Python 3.10+

\- \*\*Framework:\*\* Streamlit (UI & Logic 통합)

\- \*\*Database:\*\* SQLite (SQLAlchemy ORM) - 설정값과 데이터를 단일 파일로 관리.

\- \*\*AI Engine:\*\*

&nbsp;   - STT: `faster-whisper` (int8/float16 동적 전환)

&nbsp;   - LLM: `ollama` API 연동

&nbsp;   - Refiner: Gemini/OpenAI API 또는 Local LLM 선택 가능 (맞춤법 교정용)



\## 2. 데이터베이스 스키마

\- \*\*SystemConfigs:\*\* `key`, `value` (하드웨어 모드, 텔레그램 토큰, 드라이브 경로 등)

\- \*\*Recordings:\*\* `file\_path`, `duration`, `file\_size`, `processed`

\- \*\*Transcripts:\*\*

&nbsp;   - `full\_text` (전체 스크립트)

&nbsp;   - `summary` (요약)

&nbsp;   - `tags` (자동 생성된 태그)

&nbsp;   - `segments\_json` (타임스탬프: `\[{start:0.0, end:5.0, text:"..."}]`)

&nbsp;   - `version` (수정 이력 관리)



\## 3. 오디오 처리 파이프라인

1\. \*\*Ingest:\*\* 파일 감지 (텔레그램/드라이브) -> `data/temp` 이동.

2\. \*\*Optimize:\*\* FFmpeg로 `mp3 64k mono` 변환 -> 원본 삭제.

3\. \*\*Analyze:\*\* Whisper(STT) -> Ollama(요약/태깅) -> 타임스탬프 추출.

4\. \*\*Archive:\*\* `data/storage` (또는 구글드라이브 마운트 경로)로 최종 이동 및 DB 저장.

