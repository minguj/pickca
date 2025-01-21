import streamlit as st
from konlpy.tag import Okt
import os
import jpype

# # JAVA_HOME 환경 변수 설정
# os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-17-openjdk-amd64'
# os.environ['PATH'] += os.pathsep + os.path.join(os.environ['JAVA_HOME'], 'bin')

# # JVM 시작 (필요 시 수동으로 시작)
# if not jpype.isJVMStarted():
#     jpype.startJVM(jpype.getDefaultJVMPath())

# Java 경로 출력
java_home = os.environ.get('JAVA_HOME', 'Not Set')
print(f"JAVA_HOME: {java_home}")

# JVM 경로 출력
try:
    import jpype
    jvm_path = jpype.getDefaultJVMPath()
    print(f"JVM Path: {jvm_path}")
except Exception as e:
    print(f"Error: {e}")

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