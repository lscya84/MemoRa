# Dockerfile
FROM python:3.10-slim

# FFmpeg 설치 (오디오 변환용 필수)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 전체 소스 코드 복사 (이제 app/ 폴더가 없으므로 현재 위치(.)를 복사)
COPY . .

# 실행 명령어
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
# 8501: Streamlit 웹 UI
# 8000: Backend API (추후 확장용)
EXPOSE 8501 8000
# [추가] entrypoint.sh 파일에 실행 권한 부여
RUN chmod +x entrypoint.sh

# 실행 명령어
ENTRYPOINT ["./entrypoint.sh"]
# 또는 CMD ["./entrypoint.sh"] (작성하신 내용에 따라)