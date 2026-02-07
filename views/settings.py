import streamlit as st
import os
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
            
            if st.button("🔌 Ollama 연결 테스트", use_container_width=True):
                import requests
                try:
                    url = f"{st.session_state.ollama_url}/api/tags"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        models = [m['name'] for m in response.json().get('models', [])]
                        if st.session_state.ollama_model in models:
                            st.success(f"연결 성공! '{st.session_state.ollama_model}' 모델이 준비되었습니다.")
                        else:
                            st.warning(f"연결 성공! 하지만 '{st.session_state.ollama_model}' 모델이 없습니다. (설치된 모델: {', '.join(models)})")
                    else:
                        st.error(f"연결 실패 (HTTP {response.status_code})")
                except Exception as e:
                    st.error(f"연결 오류: {e}\nURL: {st.session_state.ollama_url}")

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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 임시 파일 삭제", help="data/temp 폴더의 모든 파일을 삭제합니다.", use_container_width=True):
                temp_dir = "data/temp"
                if os.path.exists(temp_dir):
                    files = os.listdir(temp_dir)
                    for f in files:
                        os.remove(os.path.join(temp_dir, f))
                    st.success(f"{len(files)}개의 임시 파일을 삭제했습니다.")
                else:
                    st.info("삭제할 임시 폴더가 없습니다.")
        
        with col2:
            if st.button("🚨 모든 기록 초기화", help="DB와 저장된 모든 오디오 파일을 삭제합니다.", type="secondary", use_container_width=True):
                # 실제 삭제 로직은 더 신중해야 하므로 세션 상태로 확인 창을 띄우거나 바로 실행
                # 여기서는 간단히 storage 삭제 로직 예시
                storage_dir = "data/storage"
                if os.path.exists(storage_dir):
                    files = os.listdir(storage_dir)
                    for f in files:
                        os.remove(os.path.join(storage_dir, f))
                    st.warning("저장소의 모든 오디오 파일이 삭제되었습니다. (DB는 유지)")
        
        st.toggle(
            "프라이버시 모드 (외부 API 차단)",
            value=True,
            disabled=True,
            help="MemoRa는 기본적으로 모든 데이터를 로컬에서 처리합니다."
        )

    # 3. 외부 연동 및 동기화
    with st.container(border=True):
        st.subheader("🔗 외부 연동 (Google Drive)")
        
        st.info("Google Drive API를 사용하려면 `credentials.json` 파일이 프로젝트 루트에 있어야 합니다.")
        
        gdrive_folder_id = st.text_input(
            "Google Drive Folder ID",
            key="gdrive_folder_id",
            on_change=lambda: save_setting("gdrive_folder_id", st.session_state.gdrive_folder_id),
            placeholder="folder-id-string-here",
            help="동기화할 구글 드라이브 폴더의 ID를 입력하세요."
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("지금 동기화", type="secondary", use_container_width=True):
                with st.spinner("구글 드라이브에서 파일을 가져오는 중..."):
                    try:
                        from gdrive_service import sync_from_gdrive
                        result = sync_from_gdrive(st.session_state.gdrive_folder_id)
                        if "Error" in result:
                            st.error(result)
                        else:
                            st.success(result)
                            st.info("가져온 파일은 'Analyze' 메뉴에서 분석할 수 있습니다.")
                    except Exception as e:
                        st.error(f"동기화 중 오류 발생: {e}")
        with col2:
             st.caption("폴더 내의 신규 오디오 파일(.mp3, .m4a, .wav)을 자동으로 수집합니다.")

        st.text_input("Telegram Bot Token", 
                     placeholder="토큰 입력 (준비 중)", 
                     disabled=True,
                     help="텔레그램으로 음성을 보내면 자동으로 분석되도록 업데이트 예정입니다.")

    # 설정 저장 버튼 (Streamlit은 즉시 반영되지만, 명시적 확인용)
    if st.button("설정 상태 확인", type="primary"):
        st.toast(f"현재 설정: Whisper-{st.session_state.whisper_model} / {st.session_state.ollama_model}", icon="✅")