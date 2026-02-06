import streamlit as st
import sys
import os

# 프로젝트 루트 경로를 파이썬 경로에 추가 (모듈 import 위함)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.database import init_db, SystemConfig

st.set_page_config(page_title="MemoRa", page_icon="🧠", layout="wide")

st.title("🧠 MemoRa Dashboard")
st.subheader("나만의 로컬 AI 회의 비서")

# 사이드바
with st.sidebar:
    st.info("시스템 상태: 🟢 정상")
    if st.button("DB 연결 테스트"):
        try:
            db = init_db()
            config_count = db.query(SystemConfig).count()
            st.success(f"DB 연결 성공! (저장된 설정: {config_count}개)")
        except Exception as e:
            st.error(f"연결 실패: {e}")

st.write("---")
st.markdown("### 👋 환영합니다!")
st.write("현재 MemoRa 시스템이 Docker 환경에서 성공적으로 실행되고 있습니다.")
st.write("좌측 사이드바 메뉴를 통해 설정을 진행해주세요 (개발 중).")