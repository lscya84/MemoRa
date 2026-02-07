import streamlit as st
import requests
import os
import json

# 환경변수에서 주소 가져오기 (없으면 기본값)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def chat_page():
    st.header("💬 AI 비서와 대화하기")

    # 세션 상태 초기화 (대화 기록 저장용)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 기존 대화 내용 화면에 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    if prompt := st.chat_input("무엇을 도와드릴까요?"):
        # 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성 (스트리밍)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Ollama API 호출
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
                                full_response += data["response"]
                                message_placeholder.markdown(full_response + "▌")
                                
                message_placeholder.markdown(full_response)
                
                # AI 응답 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"AI 서버 연결 오류: {e}")