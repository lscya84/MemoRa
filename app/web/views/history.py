import streamlit as st

def history_page():
    st.header("📜 회의록 히스토리")
    st.info("데이터베이스에 저장된 회의 기록을 이곳에서 보여줄 예정입니다.")
    
    # (예시 데이터)
    st.dataframe([
        {"날짜": "2026-02-07", "제목": "프로젝트 기획 회의", "요약": "Docker 도입 결정"},
        {"날짜": "2026-02-06", "제목": "서버 아키텍처 논의", "요약": "Proxmox 활용 방안"},
    ])