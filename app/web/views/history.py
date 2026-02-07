import streamlit as st

def history_page():
    st.header("🗂️ 회의록 아카이브")
    
    history = st.session_state.get("meeting_history", [])
    
    if not history:
        st.info("아직 저장된 회의록이 없습니다. '회의 분석' 메뉴에서 분석을 진행해주세요.")
        return

    for i, item in enumerate(reversed(history)):
        with st.expander(f"📄 {item['date']} - {item['filename']}", expanded=(i==0)):
            st.caption(f"Used Engine: {item['model']}")
            
            tab1, tab2 = st.tabs(["💡 요약본", "📝 전체 스크립트"])
            
            with tab1:
                st.markdown(item['summary'])
            
            with tab2:
                st.text_area("전체 내용", item['full_text'], height=200, key=f"hist_{i}")
            
            if st.button("삭제", key=f"del_{i}"):
                # 리스트에서 삭제 후 리런 (인덱스 주의: reversed 상태라 원본 데이터 처리 필요하지만 간소화함)
                st.warning("새로고침 시 삭제가 반영됩니다.")
                st.session_state.meeting_history.remove(item)
                st.rerun()