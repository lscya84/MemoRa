# Dockerfile

FROM python:3.10-slim

# 1. 필수 패키지 설치
RUN apt-get update && \
    apt-get install -y ffmpeg dos2unix curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 소스 코드 복사
COPY . .

# 4. [핵심 수정] entrypoint.sh를 시스템 경로로 복사하고 권한 부여
# 이렇게 하면 docker-compose의 volumes 설정이 이 파일을 덮어쓰지 못함 (안전지대)
COPY entrypoint.sh /usr/local/bin/
RUN dos2unix /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

# 5. 실행 포트 노출
EXPOSE 8501

# 6. 진입점 설정 (시스템 경로에 있는 파일 실행)
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# 7. 기본 실행 명령어
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]