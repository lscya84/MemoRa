import streamlit as st
import requests
import os
import json

def chat_page():
    st.header("💬 AI 비서와 대화하기")
    
    # 설정된 모델 확인
    current_model = st.session_state.get("ollama_model", "gemma2:2b")
    st.caption(f"Current Engine: {current_model}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
            
            try:
                payload = {
                    "model": current_model, # 동적 모델 적용
                    "prompt": prompt,
                    "stream": True
                }
                with requests.post(f"{OLLAMA_URL}/api/generate", json=payload, stream=True) as response:
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                full_response += data["response"]
                                message_placeholder.markdown(full_response + "▌")
                                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"AI 서버({OLLAMA_URL}) 연결 오류: {e}")