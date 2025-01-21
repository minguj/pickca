import streamlit as st
from konlpy.tag import Okt
import os
import jpype
import subprocess



st.title("Streamlit + konlpy 테스트")

# 텍스트 입력
text = st.text_input("텍스트를 입력하세요:")
if text:
    try:
        okt = Okt()
        tokens = okt.morphs(text)
        st.write("형태소 분석 결과:")
        st.write(tokens)
    except Exception as e:
        st.error(f"에러 발생: {e}")