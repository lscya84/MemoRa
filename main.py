import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.analyze import analyze_page
from views.chat import chat_page
from views.history import history_page
from views.settings import settings_page
from database import SessionLocal, SystemConfig, Recording, init_db

st.set_page_config(page_title="MemoRa", page_icon="🧠", layout="wide")

# DB 초기화
init_db()

# === Zero-Config DB 영속성 관리 ===
def load_settings():
    db = SessionLocal()
    try:
        configs = db.query(SystemConfig).all()
        db_settings = {c.key: c.value for c in configs}
        
        defaults = {
            "whisper_model": "base",
            "whisper_device": "cpu",
            "whisper_compute": "int8",
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma2:2b",
            "auto_delete": "True",
            "api_key": ""
        }
        
        for key, default_val in defaults.items():
            # DB에 있으면 DB값, 없으면 기본값 사용
            val = db_settings.get(key, default_val)
            # Boolean 처리
            if val == "True": val = True
            elif val == "False": val = False
            
            if key not in st.session_state:
                st.session_state[key] = val
    finally:
        db.close()

def main():
    load_settings() # 앱 실행 시 DB에서 설정 로드

    with st.sidebar:
        st.title("🧠 MemoRa")
        st.caption("Don't just say it, MemoRa it")
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            ["Dashboard", "Analyze (분석)", "Chat (비서)", "History (기록)", "Settings (설정)"],
        )
        
        st.markdown("---")
        st.caption(f"🔧 Engine: {st.session_state.whisper_model}")
        st.caption(f"🧠 LLM: {st.session_state.ollama_model}")

    if "Dashboard" in menu:
        st.title("📊 MemoRa Dashboard")
        
        db = SessionLocal()
        try:
            total_count = db.query(Recording).count()
        finally:
            db.close()

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("STT Engine", st.session_state.whisper_model, st.session_state.whisper_device)
        with col2: st.metric("LLM Model", st.session_state.ollama_model)
        with col3: st.metric("Saved Recordings", f"{total_count} 건")

    elif "Analyze" in menu:
        analyze_page()
    elif "Chat" in menu:
        chat_page()
    elif "History" in menu:
        history_page()
    elif "Settings" in menu:
        settings_page()

if __name__ == "__main__":
    main()