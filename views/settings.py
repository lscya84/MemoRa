import streamlit as st
from database import save_setting

def settings_page():
    st.header("⚙️ 시스템 설정 (Zero-Config)")
    st.caption("서버 재시작 없이 AI 엔진과 시스템 동작 방식을 즉시 변경합니다.")

    st.markdown("---")

    # 1. 동적 엔진 설정 (Dynamic Engine)
    with st.container(border=True):
        st.subheader("🤖 AI 엔진 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🗣️ STT (Whisper)")
            st.selectbox(
                "Whisper 모델 크기",
                ["tiny", "base", "small", "medium", "large-v3"],
                key="whisper_model",
                on_change=lambda: save_setting("whisper_model", st.session_state.whisper_model),
                help="N100 등 저전력 서버는 'tiny' 또는 'base' 권장"
            )
            # 하드웨어 가속 설정
            st.selectbox(
                "연산 장치 (Device)",
                ["cpu", "cuda", "auto"],
                key="whisper_device",
                on_change=lambda: save_setting("whisper_device", st.session_state.whisper_device),
                help="GPU가 없으면 'cpu'를 선택하세요."
            )
            st.selectbox(
                "정밀도 (Compute Type)",
                ["int8", "float16", "float32"],
                key="whisper_compute",
                on_change=lambda: save_setting("whisper_compute", st.session_state.whisper_compute),
                help="int8은 메모리를 적게 사용합니다 (N100 권장)."
            )

        with col2:
            st.markdown("#### 🧠 LLM (Ollama)")
            # Ollama 설정
            st.text_input(
                "Ollama 서버 URL",
                key="ollama_url",
                on_change=lambda: save_setting("ollama_url", st.session_state.ollama_url),
                help="예: http://localhost:11434"
            )
            st.text_input(
                "사용할 모델명",
                key="ollama_model",
                on_change=lambda: save_setting("ollama_model", st.session_state.ollama_model),
                placeholder="예: gemma2:2b, llama3",
                help="Ollama에 설치된 모델 이름을 입력하세요."
            )
            st.text_input(
                "API Key (Fallback)",
                key="api_key",
                type="password",
                on_change=lambda: save_setting("api_key", st.session_state.api_key),
                help="Ollama가 안될 때 사용할 OpenAI/Gemini 키"
            )

    # 2. 저장소 및 프라이버시 (Storage Efficient & Privacy)
    with st.container(border=True):
        st.subheader("💾 저장소 및 프라이버시")
        
        st.toggle(
            "분석 후 원본 오디오 삭제 (Storage Efficient)",
            key="auto_delete",
            on_change=lambda: save_setting("auto_delete", st.session_state.auto_delete),
            help="활성화 시, 분석이 끝나면 용량이 큰 원본 파일은 삭제합니다."
        )
        st.toggle(
            "프라이버시 모드 (외부 API 차단)",
            value=True,
            disabled=True,
            help="MemoRa는 기본적으로 모든 데이터를 로컬에서 처리합니다."
        )

    # 3. 다중 수집 설정 (Placeholder)
    with st.container(border=True):
        st.subheader("🔗 외부 연동 (준비 중)")
        st.text_input("Telegram Bot Token", placeholder="토큰 입력", disabled=True)
        st.text_input("Google Drive 경로", placeholder="/mnt/gdrive", disabled=True)

    # 설정 저장 버튼 (Streamlit은 즉시 반영되지만, 명시적 확인용)
    if st.button("설정 상태 확인", type="primary"):
        st.toast(f"현재 설정: Whisper-{st.session_state.whisper_model} / {st.session_state.ollama_model}", icon="✅")