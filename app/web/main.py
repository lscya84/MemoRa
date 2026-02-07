import streamlit as st
import os
import sys

# 현재 경로를 시스템 경로에 추가 (모듈 import 문제 해결)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 모듈 가져오기
from views.chat import chat_page
from views.history import history_page

# 페이지 설정
st.set_page_config(
    page_title="MemoRa",
    page_icon="🧠",
    layout="wide"
)

def main():
    # === 사이드바 구성 ===
    with st.sidebar:
        st.title("🧠 MemoRa")
        st.markdown("---")
        
        # 메뉴 선택
        menu = st.radio(
            "메뉴 선택",
            ["홈 (Dashboard)", "대화하기 (Chat)", "회의록 (History)"],
            index=0
        )
        
        st.markdown("---")
        st.caption("Proxmox Server Running 🚀")

    # === 메인 화면 라우팅 ===
    if "홈" in menu:
        st.title("📊 MemoRa Dashboard")
        st.success("시스템이 정상적으로 작동 중입니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="연결된 AI 모델", value="Gemma2:2b")
        with col2:
            st.metric(label="서버 상태", value="Online")
            
    elif "대화하기" in menu:
        chat_page()
        
    elif "회의록" in menu:
        history_page()

if __name__ == "__main__":
    main()