import streamlit as st
import os
import requests
import json
from faster_whisper import WhisperModel
from datetime import datetime

# 모델 캐싱 (매번 로딩하지 않도록 설정)
@st.cache_resource
def load_whisper_model():
    # N100 CPU 환경을 고려하여 'tiny' 또는 'base' 모델 사용 권장
    # 성능이 부족하면 'tiny', 좀 더 정확한 걸 원하면 'small'로 변경 가능
    return WhisperModel("base", device="cpu", compute_type="int8")

def meeting_page():
    st.header("🎙️ 회의 녹음 분석")
    st.caption("녹음 파일을 업로드하면 AI가 텍스트로 변환하고 요약해줍니다.")

    # 1. 파일 업로드
    uploaded_file = st.file_uploader("녹음 파일 선택 (mp3, wav, m4a)", type=["mp3", "wav", "m4a"])

    if uploaded_file is not None:
        # 파일 저장 (임시)
        save_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"파일 업로드 완료: {uploaded_file.name}")

        # 2. 텍스트 변환 (STT) 버튼
        if st.button("📝 텍스트 변환 및 요약 시작"):
            model = load_whisper_model()
            
            with st.spinner("열심히 받아적는 중입니다... (CPU 성능에 따라 시간 소요)"):
                segments, info = model.transcribe(save_path, beam_size=5)
                
                full_text = ""
                progress_bar = st.progress(0)
                
                # 변환 과정 실시간 표시
                for i, segment in enumerate(segments):
                    full_text += segment.text + " "
                    # (진행률은 정확히 알 수 없으므로 시각적 효과만)
                    if i % 10 == 0:
                        progress_bar.progress(min(i, 100))
                
                progress_bar.progress(100)
            
            st.success("변환 완료!")
            
            # 결과 보여주기
            with st.expander("원문 보기 (Transcript)", expanded=False):
                st.text_area("전체 대화 내용", full_text, height=200)

            # 3. AI 요약 요청 (Ollama)
            st.markdown("### 🧠 AI 회의 요약")
            summary_placeholder = st.empty()
            summary_text = ""

            prompt = f"""
            아래 회의 내용을 보고서 형식으로 깔끔하게 요약해줘.
            중요한 결정 사항과 할 일(Action Item)을 따로 정리해줘.
            
            [회의 내용]
            {full_text}
            """

            try:
                OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
                payload = {
                    "model": "gemma2:2b",
                    "prompt": prompt,
                    "stream": True
                }
                
                with requests.post(f"{OLLAMA_URL}/api/generate", json=payload, stream=True) as response:
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                summary_text += data["response"]
                                summary_placeholder.markdown(summary_text + "▌")
                
                summary_placeholder.markdown(summary_text)
                
            except Exception as e:
                st.error(f"요약 중 오류 발생: {e}")