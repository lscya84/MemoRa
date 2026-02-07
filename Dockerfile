# 1. Base Image: 가볍고 빠른 Python 3.10 Slim 버전 사용
FROM python:3.10-slim

# 2. System Dependencies 설치
# ffmpeg: 오디오 변환(mp3 압축)을 위해 필수
# curl: entrypoint.sh에서 Ollama 서버 상태를 체크하기 위해 필수
# git: 일부 Python 패키지 설치를 위해 필요
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. Python 라이브러리 설치
# (requirements.txt가 변경되지 않았다면 캐시를 사용하여 빌드 속도 향상)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 전체 복사
COPY . .

# 6. Entrypoint 스크립트 설정
# (서버 실행 전 Ollama 연결을 확인하는 스크립트)
COPY entrypoint.sh .
# 윈도우에서 작성 시 권한 문제가 생길 수 있으므로 실행 권한 부여
RUN chmod +x entrypoint.sh

# 7. 포트 개방
# 8501: Streamlit 웹 UI
# 8000: Backend API (추후 확장용)
EXPOSE 8501 8000

# 8. 실행 명령
# entrypoint.sh를 먼저 실행하여 AI 모델을 준비한 뒤, Streamlit을 실행함
ENTRYPOINT ["./entrypoint.sh"]
CMD ["streamlit", "run", "app/web/main.py", "--server.address=0.0.0.0"]