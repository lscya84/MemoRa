import streamlit as st
import os
import requests
import json
from faster_whisper import WhisperModel
from datetime import datetime

# 설정값에 따라 모델을 로드 (인자값이 바뀌면 캐시 새로고침)
@st.cache_resource
def load_whisper_model(model_size, device, compute_type):
    return WhisperModel(model_size, device=device, compute_type=compute_type)

def meeting_page():
    st.header("🎙️ 회의/음성 분석")
    
    # 현재 설정 상태 표시
    st.info(f"현재 엔진: Whisper **{st.session_state.whisper_model}** ({st.session_state.whisper_device}) | LLM: **{st.session_state.ollama_model}**")

    uploaded_file = st.file_uploader("녹음 파일 업로드", type=["mp3", "wav", "m4a"])

    if uploaded_file is not None:
        os.makedirs("data", exist_ok=True)
        save_path = os.path.join("data", uploaded_file.name)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("🚀 분석 시작", type="primary"):
            # 1. 설정값 가져오기 (Zero-Config)
            w_model = st.session_state.whisper_model
            w_device = st.session_state.whisper_device
            w_compute = st.session_state.whisper_compute
            
            # 2. 모델 로드
            model = load_whisper_model(w_model, w_device, w_compute)
            
            st.markdown("### 📝 STT 변환 중...")
            progress = st.progress(0)
            
            try:
                segments, info = model.transcribe(save_path, beam_size=5)
                full_text = ""
                
                for i, segment in enumerate(segments):
                    full_text += segment.text + " "
                    # 진행률 시각적 표시 (정확하진 않음)
                    if i < 100: progress.progress(i + 1)
                
                progress.progress(100)
                st.success("텍스트 변환 완료")

                # 3. LLM 요약
                st.markdown("### 🧠 AI 요약 중...")
                summary_text = ""
                placeholder = st.empty()
                
                prompt = f"다음 내용을 요약해줘:\n{full_text}"
                
                # 설정된 Ollama URL 사용
                ollama_url = st.session_state.ollama_url
                ollama_model = st.session_state.ollama_model
                
                try:
                    payload = {"model": ollama_model, "prompt": prompt, "stream": True}
                    with requests.post(f"{ollama_url}/api/generate", json=payload, stream=True) as res:
                        for line in res.iter_lines():
                            if line:
                                data = json.loads(line.decode("utf-8"))
                                if "response" in data:
                                    summary_text += data["response"]
                                    placeholder.markdown(summary_text + "▌")
                    placeholder.markdown(summary_text)

                    # 4. 저장 및 정리
                    record = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "filename": uploaded_file.name,
                        "full_text": full_text,
                        "summary": summary_text,
                        "model": f"{w_model} / {ollama_model}"
                    }
                    st.session_state.meeting_history.append(record)

                    # [PRD: Storage Efficient] 원본 삭제 옵션 확인
                    if st.session_state.auto_delete:
                        os.remove(save_path)
                        st.toast("용량 절약을 위해 원본 파일을 삭제했습니다.", icon="🗑️")
                    
                except Exception as e:
                    st.error(f"Ollama 연결 실패: {e}")

            except Exception as e:
                st.error(f"Whisper 오류: {e}")