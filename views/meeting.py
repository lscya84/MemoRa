import streamlit as st
import os
import time
from services import optimize_audio, refine_text_with_ai
from database import SessionLocal, ...
# DB 초기화
init_db()

@st.cache_resource
def load_model(size, device, compute):
    return WhisperModel(size, device=device, compute_type=compute)

def meeting_page():
    st.header("🎙️ 회의 분석 및 AI 검토")
    st.caption("저용량 최적화 업로드 -> 분석 -> AI Refiner(교정/검토)")

    # --- 사이드바: Refiner 설정 ---
    with st.sidebar:
        st.markdown("### 🤖 Refiner 설정")
        refiner_api_key = st.text_input("OpenAI/Gemini API Key", type="password")
        refiner_mode = st.selectbox("검토 모드", ["오탈자/비문 교정", "요약 요청", "Action Item 추출"])

    # 1. 파일 업로드
    uploaded_file = st.file_uploader("음성 파일 (자동 최적화)", type=["mp3", "wav", "m4a"])

    if uploaded_file:
        # 임시 저장 (Ingest)
        os.makedirs("data/temp", exist_ok=True)
        temp_path = os.path.join("data/temp", uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 분석 버튼
        if st.button("🚀 최적화 및 분석 시작", type="primary"):
            status = st.status("작업 진행 중...", expanded=True)
            
            # [Step 1] Optimize (압축 및 원본 삭제)
            status.write("💾 오디오 최적화 (64k mono) 변환 중...")
            optimized_path = optimize_audio(temp_path, output_folder="data/storage")
            
            if not optimized_path:
                status.error("오디오 변환 실패")
                return

            # [Step 2] Analyze (STT)
            status.write("📝 Whisper AI가 받아쓰는 중...")
            
            # 설정값 가져오기 (main.py의 session_state)
            w_size = st.session_state.get("whisper_model", "base")
            w_device = st.session_state.get("whisper_device", "cpu")
            w_compute = st.session_state.get("whisper_compute", "int8")
            
            model = load_model(w_size, w_device, w_compute)
            segments, _ = model.transcribe(optimized_path, beam_size=5)
            
            full_text = ""
            for segment in segments:
                full_text += segment.text + " "
            
            status.write("✅ 분석 완료!")
            status.update(label="작업 완료!", state="complete", expanded=False)

            # 결과 세션 저장
            st.session_state.current_script = full_text
            st.session_state.optimized_path = optimized_path

            # [Step 3] DB Archive (메타데이터 저장)
            db = SessionLocal()
            new_rec = Recording(
                filename=os.path.basename(optimized_path),
                file_path=optimized_path,
                file_size=os.path.getsize(optimized_path) / (1024*1024),
                processed=1
            )
            db.add(new_rec)
            db.commit()
            
            # Transcript 저장
            new_trans = Transcript(
                recording_id=new_rec.id,
                full_text=full_text,
                version=1
            )
            db.add(new_trans)
            db.commit()
            db.close()

    # --- 결과 검토 및 AI 요청 UI ---
    if "current_script" in st.session_state:
        st.divider()
        st.subheader("📝 스크립트 검토")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 원본 스크립트 (수정 가능)
            script_area = st.text_area("생성된 스크립트", value=st.session_state.current_script, height=300)
            
            # 복사 기능 (Streamlit의 code 블록 이용)
            st.caption("아래 버튼을 눌러 복사하세요:")
            st.code(script_area, language="text")

        with col2:
            st.info("🤖 AI Refiner")
            st.write(f"모드: **{refiner_mode}**")
            
            if st.button("AI에게 검토/수정 요청"):
                if not refiner_api_key:
                    st.error("사이드바에 API Key를 입력하세요.")
                else:
                    with st.spinner("AI가 검토 중입니다..."):
                        # Refine 모드별 키워드 매핑
                        mode_map = {
                            "오탈자/비문 교정": "fix",
                            "요약 요청": "summarize",
                            "Action Item 추출": "action_item"
                        }
                        result = refine_text_with_ai(script_area, refiner_api_key, mode_map[refiner_mode])
                        
                        st.success("검토 완료!")
                        st.text_area("AI 제안 결과", value=result, height=200)
                        st.caption("결과 복사:")
                        st.code(result, language="text")