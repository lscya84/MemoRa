import streamlit as st
from utils import load_config, save_config, get_ollama_models

def settings_page():
    st.header("⚙️ 환경 설정")
    st.caption("AI 모델과 시스템 설정을 변경합니다.")

    # 현재 설정 불러오기
    current_config = load_config()

    with st.form("settings_form"):
        st.subheader("🤖 AI 모델 설정")
        
        # 1. Ollama 모델 선택 (서버에서 목록 가져오기)
        available_models = get_ollama_models()
        # 현재 설정된 모델이 목록에 없으면 기본값 추가
        index = 0
        if current_config["ai_model"] in available_models:
            index = available_models.index(current_config["ai_model"])
            
        selected_model = st.selectbox(
            "사용할 AI 모델 (Ollama)", 
            available_models, 
            index=index
        )

        # 2. 창의성 (Temperature)
        temperature = st.slider(
            "창의성 (Temperature)", 
            min_value=0.0, max_value=1.0, 
            value=current_config.get("temperature", 0.7),
            help="높을수록 창의적이고, 낮을수록 사실적인 답변을 합니다."
        )

        st.markdown("---")
        st.subheader("🎙️ 음성 인식 (STT) 설정")

        # 3. Whisper 모델 크기 (N100 성능 고려)
        stt_options = ["tiny", "base", "small", "medium"]
        stt_index = 1 # 기본값 base
        if current_config["stt_model"] in stt_options:
            stt_index = stt_options.index(current_config["stt_model"])

        selected_stt = st.selectbox(
            "Whisper 모델 크기", 
            stt_options, 
            index=stt_index,
            help="Tiny(빠름/부정확) < Base(균형) < Small(정확/느림). N100은 Base 추천."
        )

        st.markdown("---")
        st.subheader("🧠 페르소나 설정")

        # 4. 시스템 프롬프트
        system_prompt = st.text_area(
            "시스템 프롬프트 (AI의 역할)",
            value=current_config.get("system_prompt", ""),
            height=100
        )

        # 저장 버튼
        if st.form_submit_button("설정 저장"):
            new_config = {
                "ai_model": selected_model,
                "stt_model": selected_stt,
                "temperature": temperature,
                "system_prompt": system_prompt
            }
            save_config(new_config)
            st.success("✅ 설정이 저장되었습니다! (새 설정은 다음 대화부터 적용됩니다)")
            # 세션 갱신을 위해 리런
            st.rerun()