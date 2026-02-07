import os
import json
import requests
import streamlit as st

# 설정 파일 경로 (Docker 볼륨인 data 폴더에 저장해야 날아가지 않음)
CONFIG_PATH = os.path.join("data", "config.json")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# 기본 설정값
DEFAULT_CONFIG = {
    "ai_model": "gemma2:2b",
    "stt_model": "base",
    "temperature": 0.7,
    "system_prompt": "당신은 도움이 되는 AI 비서입니다. 한국어로 답변해주세요."
}

def load_config():
    """설정 파일 불러오기 (없으면 기본값 생성)"""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

def save_config(config):
    """설정 파일 저장하기"""
    # data 폴더가 없으면 생성
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def get_ollama_models():
    """Ollama 서버에 설치된 모델 리스트 가져오기"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            models = [m["name"] for m in response.json()["models"]]
            return models
    except:
        pass
    return ["gemma2:2b"] # 연결 실패 시 기본값