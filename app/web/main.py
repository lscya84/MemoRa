import streamlit as st
import os
import sys

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 뷰 모듈 가져오기
from views.chat import chat_page
from views.history import history_page
from views.meeting import meeting_page  # <--- 새로 추가된 부분

st.set_page_config(page_title="MemoRa", page_icon="🧠", layout="wide")

def main():
    # === 사이드바 ===
    with st.sidebar:
        st.title("🧠 MemoRa")
        st.markdown("---")
        
        # 메뉴에 '회의 분석' 추가
        menu = st.radio(
            "메뉴 선택",
            ["홈 (Dashboard)", "대화하기 (Chat)", "회의 분석 (Meeting)", "회의록 (History)"],
            index=0
        )
        
        st.markdown("---")
        st.caption("Proxmox Server Running 🚀")

    # === 화면 라우팅 ===
    if "홈" in menu:
        st.title("📊 MemoRa Dashboard")
        st.success("시스템 정상 작동 중")
        col1, col2 = st.columns(2)
        with col1: st.metric("AI 모델", "Gemma2:2b")
        with col2: st.metric("STT 엔진", "Faster-Whisper") # 업데이트

    elif "대화하기" in menu:
        chat_page()

    elif "회의 분석" in menu:  # <--- 새로 추가된 부분
        meeting_page()
        
    elif "회의록" in menu:
        history_page()

if __name__ == "__main__":
    main()