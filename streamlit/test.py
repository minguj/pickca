import streamlit as st
from konlpy.tag import Okt
import os
import jpype
import subprocess


subprocess.run(['sudo', 'apt-get', 'install', '-y', 'openjdk-11-jdk'], check=True)

# 패키지 설치 확인 (openjdk-11-jdk가 설치되었는지 확인)
result = subprocess.run(["dpkg-query", "-l", "openjdk-11-jdk"], capture_output=True, text=True)

# 출력 확인
print(result.stdout)



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