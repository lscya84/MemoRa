import streamlit as st
import os
import sys

# views 폴더 경로 인식 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 뷰 모듈 가져오기
from views.chat import chat_page
from views.history import history_page
from views.meeting import meeting_page

st.set_page_config(page_title="MemoRa", page_icon="🧠", layout="wide")

def init_session_state():
    # 전역 설정 초기화
    if "ollama_model" not in st.session_state:
        st.session_state.ollama_model = "gemma2:2b"
    if "whisper_model_size" not in st.session_state:
        st.session_state.whisper_model_size = "base"
    # 회의 데이터 저장소
    if "meeting_history" not in st.session_state:
        st.session_state.meeting_history = []

def main():
    init_session_state()

    # === 사이드바 ===
    with st.sidebar:
        st.title("🧠 MemoRa")
        st.caption("Local AI archiving System")
        st.markdown("---")
        
        # 메뉴 선택
        menu = st.radio(
            "메뉴 선택",
            ["홈 (Dashboard)", "대화하기 (Chat)", "회의 분석 (Meeting)", "회의록 (History)"],
            index=0
        )
        
        st.markdown("---")
        
        # [PRD: Dynamic Engine] 설정 영역
        with st.expander("⚙️ 엔진 설정 (Zero-Config)", expanded=False):
            st.session_state.ollama_model = st.text_input(
                "Ollama 모델명", value=st.session_state.ollama_model
            )
            st.session_state.whisper_model_size = st.selectbox(
                "Whisper 모델 크기",
                ["tiny", "base", "small", "medium", "large-v3"],
                index=1,
                help="N100 추천: tiny 또는 base"
            )

    # === 화면 라우팅 ===
    if "홈" in menu:
        st.title("📊 MemoRa Dashboard")
        st.success("Proxmox/Local Server 정상 작동 중")
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("LLM 엔진", st.session_state.ollama_model)
        with col2: st.metric("STT 엔진", f"Faster-Whisper ({st.session_state.whisper_model_size})")
        with col3: st.metric("저장된 회의록", f"{len(st.session_state.meeting_history)}건")

    elif "대화하기" in menu:
        chat_page()

    elif "회의 분석" in menu:
        meeting_page()
        
    elif "회의록" in menu:
        history_page()

if __name__ == "__main__":
    main()