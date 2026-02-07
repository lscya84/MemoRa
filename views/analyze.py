import streamlit as st
import os
from faster_whisper import WhisperModel
from services import optimize_audio, refine_text_with_ai, transcribe_audio
from database import SessionLocal, Recording, Transcript, init_db

# DB 초기화는 main.py에서 수행하므로 여기선 생략 가능하지만 안전을 위해 유지
init_db()

@st.cache_resource
def load_model(size, device, compute):
    return WhisperModel(size, device=device, compute_type=compute)

def analyze_page():
    st.header("🎙️ 음성 분석 및 AI 검토")
    st.caption("음성 업로드 -> 저용량 최적화 -> AI 텍스트 변환 -> AI 검토/요약")

    # --- 사이드바: Refiner 설정 ---
    with st.sidebar:
        st.markdown("### 🤖 Refiner 설정")
        refiner_api_key = st.text_input("OpenAI/Gemini API Key", type="password")
        refiner_mode = st.selectbox("검토 모드", ["오탈자/비문 교정", "요약 요청", "중요 사항 추출"])

    # 1. 파일 업로드
    uploaded_file = st.file_uploader("음성 파일 업로드 (자동 최적화)", type=["mp3", "wav", "m4a"])

    if uploaded_file:
        os.makedirs("data/temp", exist_ok=True)
        temp_path = os.path.join("data/temp", uploaded_file.name)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("🚀 분석 시작", type="primary"):
            status = st.status("작업 진행 중...", expanded=True)
            
            # [Step 1] Optimize
            status.write("💾 오디오 최적화 진행 중...")
            optimized_path = optimize_audio(temp_path, output_folder="data/storage")
            
            if not optimized_path:
                status.error("오디오 변환 실패 (FFmpeg 설치 여부를 확인하세요)")
                status.update(label="작업 실패", state="error")
                return

            try:
                # [Step 2] Analyze (STT)
                status.write("📝 Whisper AI가 음성을 텍스트로 변환 중...")
                
                w_size = st.session_state.get("whisper_model", "base")
                w_device = st.session_state.get("whisper_device", "cpu")
                w_compute = st.session_state.get("whisper_compute", "int8")
                
                model = load_model(w_size, w_device, w_compute)
                full_text, segments_list = transcribe_audio(model, optimized_path)
                
                status.write("✅ 분석 완료!")
                
                st.session_state.current_script = full_text
                st.session_state.current_segments = segments_list
                st.session_state.optimized_path = optimized_path

                # [Step 3] DB Archive
                status.write("🗂️ 데이터베이스 저장 중...")
                db = SessionLocal()
                
                new_rec = Recording(
                    filename=os.path.basename(optimized_path),
                    file_path=optimized_path,
                    file_size=os.path.getsize(optimized_path) / (1024*1024),
                    processed=1
                )
                db.add(new_rec)
                db.commit()
                db.refresh(new_rec)
                
                new_trans = Transcript(
                    recording_id=new_rec.id,
                    full_text=full_text,
                    segments_json=segments_list,
                    version=1
                )
                db.add(new_trans)
                db.commit()
                db.close()
                
                status.update(label="모든 작업 완료!", state="complete", expanded=False)

            except Exception as e:
                status.error(f"오류 발생: {e}")
                status.update(label="작업 중단", state="error")

    # --- 결과 검토 및 AI 요청 UI ---
    if "current_script" in st.session_state:
        st.divider()
        st.subheader("📝 스크립트 검토")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            script_area = st.text_area("변환된 텍스트", value=st.session_state.current_script, height=300)
            st.caption("👇 아래 내용을 복사하여 사용하세요")
            st.code(script_area, language="text")

        with col2:
            st.info("🤖 AI Refiner")
            st.write(f"모드: **{refiner_mode}**")
            
            if st.button("AI에게 검토/수정 요청"):
                if not refiner_api_key:
                    st.error("사이드바에 API Key를 먼저 입력해주세요.")
                else:
                    with st.spinner("AI가 내용을 분석하고 있습니다..."):
                        mode_map = {
                            "오탈자/비문 교정": "fix",
                            "요약 요청": "summarize",
                            "중요 사항 추출": "action_item"
                        }
                        
                        try:
                            ai_config = {
                                "ollama_url": st.session_state.get("ollama_url"),
                                "ollama_model": st.session_state.get("ollama_model"),
                                "api_key": refiner_api_key
                            }
                            result = refine_text_with_ai(script_area, ai_config, mode_map[refiner_mode])
                            
                            st.success("검토 완료!")
                            st.text_area("AI 분석 결과", value=result, height=200)
                            st.caption("결과 복사:")
                            st.code(result, language="text")
                        except Exception as e:
                            st.error(f"AI 요청 실패: {e}")
