import os
import json
import requests
import logging
from faster_whisper import WhisperModel
from app.database import init_db, SystemConfig

logger = logging.getLogger(__name__)

class AIWorker:
    def __init__(self):
        self.db = init_db()
        self.model = None
        self.current_config = {}
        self.load_config()

    def load_config(self):
        """DB에서 설정을 읽어와 현재 상태를 갱신합니다."""
        configs = self.db.query(SystemConfig).all()
        new_config = {c.key: c.value for c in configs}
        
        # 기본값 설정
        self.device = new_config.get("ai_device", "cpu") # cpu or cuda
        self.model_size = new_config.get("whisper_model", "base")
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.ollama_url = new_config.get("ollama_url", "http://host.docker.internal:11434")
        self.ollama_model = new_config.get("ollama_model", "gemma2:2b")
        
        return new_config

    def load_whisper(self):
        """설정이 변경되었거나 모델이 없으면 Whisper 모델을 로드합니다."""
        new_config = self.load_config()
        
        # 이미 로드된 모델이 있고 설정이 같다면 재사용 (시간 절약)
        if self.model and self.current_config == new_config:
            return

        logger.info(f"🔄 Whisper 모델 로딩 중... (Device: {self.device}, Model: {self.model_size})")
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            self.current_config = new_config
            logger.info("✅ 모델 로드 완료!")
        except Exception as e:
            logger.error(f"❌ 모델 로드 실패: {e}")
            # 실패 시 안전하게 CPU/base 모델로 폴백
            if self.device == "cuda":
                logger.warning("⚠️ CPU 모드로 전환하여 재시도합니다.")
                self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, file_path):
        """오디오를 텍스트로 변환하고 타임스탬프를 추출합니다."""
        if not self.model:
            self.load_whisper()

        logger.info(f"🎙️ STT 변환 시작: {file_path}")
        segments, info = self.model.transcribe(file_path, beam_size=5)

        full_text = []
        segments_data = []

        for segment in segments:
            full_text.append(segment.text)
            segments_data.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })

        return " ".join(full_text), segments_data

    def summarize(self, text):
        """Ollama API를 호출하여 요약과 태그를 생성합니다."""
        if not text or len(text) < 10:
            return "내용이 너무 짧습니다.", "#기록"

        prompt = f"""
        너는 전문 비서야. 아래 회의록을 분석해서 다음 JSON 형식으로만 답해줘. 다른 말은 하지 마.
        {{
            "summary": "핵심 내용을 3줄 요약",
            "tags": "#키워드1 #키워드2 #키워드3",
            "title": "한줄_파일_제목_제안"
        }}
        
        [회의록 내용]
        {text[:3000]} 
        """
        # (텍스트가 너무 길면 앞부분 3000자만 보냄 - N100 속도 고려)

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json" # JSON 모드 강제
                },
                timeout=120
            )
            if response.status_code == 200:
                result = response.json().get("response", "")
                data = json.loads(result)
                return data.get("summary"), data.get("tags"), data.get("title")
            else:
                logger.error(f"Ollama 오류: {response.text}")
                return "요약 실패 (API 오류)", "#에러", "제목없음"
        except Exception as e:
            logger.error(f"Ollama 연결 실패: {e}")
            return "요약 실패 (연결 불가)", "#연결실패", "제목없음"