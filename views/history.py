import streamlit as st
from database import SessionLocal, Recording, Transcript

def history_page():
    st.header("🗂️ 음성녹음 기록 (History)")
    
    db = SessionLocal()
    # 최신순으로 정렬하여 데이터 가져오기 (Recording과 Transcript 조인 가능성 고려)
    try:
        # 간단하게 Recording 정보를 먼저 가져오고, 클릭 시 Transcript를 가져오거나 한꺼번에 가져옴
        recordings = db.query(Recording).order_by(Recording.created_at.desc()).all()
        
        if not recordings:
            st.info("아직 저장된 기록이 없습니다. 'Analyze' 메뉴에서 음성을 분석해보세요.")
            return

        for rec in recordings:
            # 해당 레코딩의 최신 트랜스크립트 가져오기
            trans = db.query(Transcript).filter(Transcript.recording_id == rec.id).order_by(Transcript.version.desc()).first()
            
            with st.expander(f"🎵 {rec.filename} ({rec.created_at.strftime('%Y-%m-%d %H:%M')})", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"파일 경로: {rec.file_path} | 용량: {rec.file_size:.2f} MB")
                with col2:
                    if st.button("삭제", key=f"del_{rec.id}"):
                        # 삭제 로직 (실제 파일은 남겨둘지 선택 가능하지만 여기선 DB만 처리하는 예시)
                        db.delete(rec)
                        # 연관된 트랜스크립트도 삭제 (CASCADE 설정에 따라 자동일 수 있음)
                        if trans: db.delete(trans)
                        db.commit()
                        st.rerun()

                if trans:
                    tab1, tab2 = st.tabs(["💡 내용 요약", "📝 전체 텍스트"])
                    with tab1:
                        if trans.summary:
                            st.markdown(trans.summary)
                        else:
                            st.info("요약 정보가 없습니다. 상세 분석을 진행해주세요.")
                    
                    with tab2:
                        st.text_area("전체 내용", trans.full_text, height=300, key=f"text_{rec.id}")
                else:
                    st.warning("변환된 텍스트 정보가 없습니다.")
    finally:
        db.close()