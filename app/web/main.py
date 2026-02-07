import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.chat import chat_page
from views.history import history_page
from views.meeting import meeting_page
from views.settings import settings_page  # <--- 추가됨

st.set_page_config(page_title="MemoRa", page_icon="🧠", layout="wide")

# === Zero-Config 초기값 설정 ===
def init_settings():
    defaults = {
        "whisper_model": "base",
        "whisper_device": "cpu",
        "whisper_compute": "int8",
        "ollama_url": "http://localhost:11434",
        "ollama_model": "gemma2:2b",
        "auto_delete": False,
        "meeting_history": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    init_settings() # 앱 실행 시 설정 로드

    with st.sidebar:
        st.title("🧠 MemoRa")
        st.caption("Don't just say it, MemoRa it")
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            ["Dashboard", "Meeting (분석)", "Chat (비서)", "History (기록)", "Settings (설정)"],
        )
        
        st.markdown("---")
        # 사이드바에 현재 핵심 설정 상태 표시
        st.caption(f"🔧 Engine: {st.session_state.whisper_model}")
        st.caption(f"🧠 LLM: {st.session_state.ollama_model}")

    if "Dashboard" in menu:
        st.title("📊 MemoRa Dashboard")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("STT Model", st.session_state.whisper_model, st.session_state.whisper_device)
        with col2: st.metric("LLM Model", st.session_state.ollama_model)
        with col3: st.metric("Total Memos", f"{len(st.session_state.meeting_history)}건")

    elif "Meeting" in menu:
        meeting_page()
    elif "Chat" in menu:
        chat_page()
    elif "History" in menu:
        history_page()
    elif "Settings" in menu:
        settings_page()

if __name__ == "__main__":
    main()