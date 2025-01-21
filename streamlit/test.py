import streamlit as st
from konlpy.tag import Okt
import os
import jpype

# # JAVA_HOME 환경 변수 설정
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk-amd64'
os.environ['PATH'] += os.pathsep + os.path.join(os.environ['JAVA_HOME'], 'bin')

# # JVM 시작 (필요 시 수동으로 시작)
if not jpype.isJVMStarted():
    jpype.startJVM(jpype.getDefaultJVMPath())



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