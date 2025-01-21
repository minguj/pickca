import streamlit as st
from konlpy.tag import Okt
import os
import jpype
import subprocess


# openjdk 설치 여부 확인
result = subprocess.run(['dpkg-query', '-l', 'openjdk-11-jdk'], capture_output=True, text=True)

if result.returncode == 0:
    print("openjdk-11-jdk is installed.")
else:
    print("openjdk-11-jdk is not installed.")



# st.title("Streamlit + konlpy 테스트")

# # 텍스트 입력
# text = st.text_input("텍스트를 입력하세요:")
# if text:
#     try:
#         okt = Okt()
#         tokens = okt.morphs(text)
#         st.write("형태소 분석 결과:")
#         st.write(tokens)
#     except Exception as e:
#         st.error(f"에러 발생: {e}")