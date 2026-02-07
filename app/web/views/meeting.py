import streamlit as st
import os
import requests
import json
from faster_whisper import WhisperModel
from datetime import datetime

# 모델 로드 (캐싱하여 속도 향상)
# 주의: Streamlit의 캐싱은 해시 가능한 인자여야 하므로 모델 사이즈를 인자로 받음
@st.cache_resource
def load_whisper_model(model_size):
    # N100 CPU 환경 최적화 (int8)
    return WhisperModel(model_size, device="cpu", compute_type="int8")

def meeting_page():
    st.header("🎙️ 회의 녹음 분석")
    st.caption("녹음 파일을 업로드하면 AI가 텍스트로 변환하고 요약해줍니다.")

    # 1. 파일 업로드
    uploaded_file = st.file_uploader("녹음 파일 선택 (mp3, wav, m4a)", type=["mp3", "wav", "m4a"])

    if uploaded_file is not None:
        # data 폴더 확인 및 생성
        os.makedirs("data", exist_ok=True)
        save_path = os.path.join("data", uploaded_file.name)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.info(f"파일 준비 완료: {uploaded_file.name}")

        # 2. 분석 시작 버튼
        if st.button("🚀 분석 시작 (Transcribe & Summarize)", type="primary"):
            current_model_size = st.session_state.whisper_model_size
            model = load_whisper_model(current_model_size)
            
            # --- STT 단계 ---
            st.markdown("### 1. 텍스트 변환 중...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # faster-whisper 실행
                segments, info = model.transcribe(save_path, beam_size=5)
                
                full_text = ""
                segment_list = [] # 타임스탬프 등 저장용
                
                # 제너레이터이므로 루프를 돌며 처리
                for i, segment in enumerate(segments):
                    full_text += segment.text + " "
                    segment_list.append(segment)
                    status_text.text(f"처리 중: {segment.start:.1f}s ~ {segment.end:.1f}s")
                    # 진행률 시각화 (임의 계산)
                    if i < 90: progress_bar.progress(i + 1)
                
                progress_bar.progress(100)
                status_text.text("텍스트 변환 완료!")
                
                with st.expander("원문 보기 (Transcript)", expanded=False):
                    st.text_area("전체 대화 내용", full_text, height=150)

                # --- 요약 단계 ---
                st.markdown("### 2. AI 요약 및 분석")
                summary_placeholder = st.empty()
                summary_result = ""

                prompt = f"""
                다음 회의 녹취록을 전문적인 비즈니스 보고서 형태로 요약해줘.
                
                [요청 사항]
                1. 전체 내용을 3줄로 핵심 요약할 것.
                2. 주요 논의 사항을 불렛 포인트로 정리할 것.
                3. 결정된 사항(Decisions)과 향후 할 일(Action Items)을 명확히 분리할 것.

                [녹취록]
                {full_text}
                """

                # Ollama 호출
                OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
                llm_model = st.session_state.ollama_model
                
                payload = {
                    "model": llm_model,
                    "prompt": prompt,
                    "stream": True
                }
                
                try:
                    with requests.post(f"{OLLAMA_URL}/api/generate", json=payload, stream=True) as response:
                        for line in response.iter_lines():
                            if line:
                                data = json.loads(line.decode("utf-8"))
                                if "response" in data:
                                    summary_result += data["response"]
                                    summary_placeholder.markdown(summary_result + "▌")
                    
                    summary_placeholder.markdown(summary_result)

                    # --- 결과 저장 (History 연동) ---
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "filename": uploaded_file.name,
                        "full_text": full_text,
                        "summary": summary_result,
                        "model": f"{llm_model} + Whisper-{current_model_size}"
                    }
                    st.session_state.meeting_history.append(record)
                    st.success("✅ 분석 결과가 회의록에 저장되었습니다.")

                except Exception as e:
                    st.error(f"Ollama 연결 오류: {e}")

            except Exception as e:
                st.error(f"Whisper 변환 오류: {e}")