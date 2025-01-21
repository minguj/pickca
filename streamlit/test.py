import streamlit as st
from konlpy.tag import Okt
import os
import jpype

# # JAVA_HOME 환경 변수 설정
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk-amd64'
os.environ['PATH'] += os.pathsep + os.path.join(os.environ['JAVA_HOME'], 'bin')

# JAVA_HOME 경로 출력
java_home = os.environ.get('JAVA_HOME', 'Not Set')
print(f"JAVA_HOME: {java_home}")


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