FROM python:3.10-slim

# 1. 필수 패키지 설치 (ffmpeg: 오디오 변환, dos2unix: 윈도우 스크립트 변환, curl: 헬스체크용)
RUN apt-get update && \
    apt-get install -y ffmpeg dos2unix curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 전체 소스 복사
COPY . .

# 4. [중요] entrypoint.sh 권한 및 포맷 수정
# 윈도우에서 작성된 스크립트(CRLF)를 리눅스용(LF)으로 변환하고 실행 권한 부여
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

# 5. 실행 포트 노출
EXPOSE 8501

# 6. 진입점 설정
ENTRYPOINT ["./entrypoint.sh"]

# 7. 기본 실행 명령어 (entrypoint.sh의 "$@" 부분에 전달됨)
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]