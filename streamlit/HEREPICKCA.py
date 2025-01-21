import streamlit as st
import pandas as pd
import numpy as np
#from konlpy.tag import Okt
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import ast
import time
import random
import streamlit.components.v1 as components
import os
import jpype
from soynlp.tokenizer import LTokenizer

# Streamlit 페이지 기본 설정
st.set_page_config(page_title="PickCa", layout="wide", page_icon='♥')

# 상태 관리 초기화
if "centered" not in st.session_state:
    st.session_state.centered = True

if "selected_colors" not in st.session_state:
    st.session_state.selected_colors = []

# CSS 스타일 적용
st.markdown(
    """
    <style>
    /* Google Fonts에서 Jua 폰트 가져오기 */
    @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

    /* 페이지 전체에 폰트 적용 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: 'Jua', sans-serif !important;
    }

    /* 최상위 배경색 */
    .st-emotion-cache-1r4qj8v {
        background-color: rgb(244, 234, 219) !important;
        height: 100% !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 컨테이너 배경 및 중앙 정렬 */
    [data-testid="stAppViewContainer"] {
        max-width: 1000px !important;
        margin: auto !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background-color: rgb(244, 234, 219) !important;
    }

    /* 사이드바 배경 */
    [data-testid="stSidebar"] {
        background-color: rgb(245, 225, 205) !important;
    }

    /* 텍스트 박스 스타일 */
    textarea {
        background-color: rgb(255, 251, 241) !important;
        color: rgb(79, 28, 8) !important;
        font-size: 16px !important;
        border: 2px solid rgb(255, 243, 226) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* 특정 텍스트 스타일 설정 */
    .custom-header {
        color: rgb(166, 105, 76) !important;
        font-size: 20px !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 20px !important;
    }

    /* 버튼 스타일 */
    [data-testid="stButton"] button {
        background-color: rgba(244, 197, 25, 0.69) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        cursor: pointer !important;
    }
    [data-testid="stButton"] button:hover {
        background-color: rgb(122, 68, 32) !important;
    }

    /* 애니메이션 스타일 */
    .center-text {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 5em;
        font-weight: bold;
        color: rgb(79, 28, 8);
        animation: fadeInOut 4s forwards;
    }

    @keyframes fadeInOut {
        0% { opacity: 0; transform: translate(-50%, -50%) translateX(-50%); color: rgb(255, 216, 198); }
        25% { opacity: 1; transform: translate(-50%, -50%) translateX(0); color: rgb(171, 127, 106); }
        75% { opacity: 1; transform: translate(-50%, -50%) translateX(0); color: rgb(122, 68, 32); }
        100% { opacity: 0; transform: translate(-50%, -50%) translateX(50%); color: rgb(79, 28, 8); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 애니메이션 구현
if st.session_state.centered:
    st.markdown(
        """
        <div class="center-text">PickCa</div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(4)
    st.session_state.centered = False

# 타이틀과 설명
if not st.session_state.centered:
    st.markdown(
        """
        <h1 style='text-align: center; color:rgb(79, 28, 8);'>PickCa</h1>
        <h3 style='text-align: center; color:rgb(166, 105, 76);'>당신만을 위한 카페 PICK!</h3>
        """,
        unsafe_allow_html=True
    )

# 계절 이모지 생성 함수
def get_season_emojis(seasonal_value):
    # seasonal_value가 None이거나 NaN인 경우 빈 문자열 반환
    if pd.isna(seasonal_value):
        return ""

    # seasonal_value를 문자열로 변환 후 쉼표로 분리
    if isinstance(seasonal_value, str):
        seasonal_list = [s.strip() for s in seasonal_value.split(",")]
    elif isinstance(seasonal_value, list):
        seasonal_list = seasonal_value
    else:
        return ""

    # 계절별 스타일 정의
    season_styles = {
        "Spring": "background-color:#FFC0CB;color:white;padding:5px 10px;border-radius:5px;font-size:12px;font-weight:bold;",
        "Summer": "background-color:#1E90FF;color:white;padding:5px 10px;border-radius:5px;font-size:12px;font-weight:bold;",
        "Fall": "background-color:#FFD700;color:black;padding:5px 10px;border-radius:5px;font-size:12px;font-weight:bold;",
        "Winter": "background-color:#FFFFFF;color:black;padding:5px 10px;border:1px solid #CCCCCC;border-radius:5px;font-size:12px;font-weight:bold;",
    }

    # HTML 컨테이너 생성
    html_emojis = '<div style="display:flex;gap:5px;align-items:center;">'
    for season, style in season_styles.items():
        if season in seasonal_list:
            html_emojis += f'<span style="{style}">{season}</span>'
    html_emojis += '</div>'
    return html_emojis

# Okt 객체 초기화
#okt = Okt()
tokenizer = LTokenizer()

# 데이터 로드 함수
@st.cache_data
def load_merged_data(data_path, file_name):
    try:
        # 데이터 로드
        df = pd.read_csv(f"{data_path}{file_name}")
        df = df[["id","cafe", "degree_of_fit", "keyword", "colors", "pop", "seasonal", "review_count", "nagativereview", "sentiment_0_count"]].dropna()

        # degree_of_fit 열을 안전하게 변환
        df["degree_of_fit"] = df["degree_of_fit"].apply(ast.literal_eval)

        # seasonal 컬럼이 비어 있거나 예기치 못한 형식인 경우 처리
        def safe_get_season_emojis(seasonal_value):
            if pd.isna(seasonal_value):
                return ""  # 값이 비어 있으면 빈 문자열 반환
            return get_season_emojis(seasonal_value)

        # 'seasonal_emojis' 컬럼에 계절 이모지 추가
        df['seasonal_emojis'] = df['seasonal'].apply(safe_get_season_emojis)

        # sentiment_0_count 열을 안전하게 정수로 변환
        df["sentiment_0_count"] = df["sentiment_0_count"].apply(
            lambda x: int(x) if pd.notna(x) and str(x).isdigit() else 0
        )

        # colors 컬럼 처리 (리스트 또는 튜플 유지)
        df["colors"] = df["colors"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        return df
    except Exception as e:
        st.error(f"데이터를 로드하는 데 실패했습니다: {e}")
        return pd.DataFrame()

# 사용자 입력에서 명사와 형용사만 추출
def extract_nouns_and_adjectives(input_text):
    pos_tags = tokenizer.tokenize(input_text)
    #okt.pos(input_text)
    return ' '.join(word for word, tag in pos_tags if tag in ['Noun', 'Adjective'])

# 사용자 입력을 벡터화
def get_weighted_tfidf(input_text, vectorizer):
    noun_adj_text = extract_nouns_and_adjectives(input_text)
    return vectorizer.transform([noun_adj_text])

# 사용자 입력 문장의 주제별 적합도 계산
def get_topic_distribution(input_text, lda_model, vectorizer, boost_factor=2.0, log_transform=True):
    tfidf_matrix = get_weighted_tfidf(input_text, vectorizer)
    topic_distribution = lda_model.transform(tfidf_matrix).flatten()
    if log_transform:
        topic_distribution = np.log1p(topic_distribution)
    adjusted_distribution = topic_distribution ** boost_factor
    adjusted_distribution /= adjusted_distribution.sum()
    return adjusted_distribution


# 추천 카페 리스트 출력
def display_recommendations(recommendations, message):
    st.markdown(f"<h4 style='color: rgb(81, 36, 15);'>{message}</h4>", unsafe_allow_html=True)
    symbols = ["🍨", "🍩", "🍰", "🧁", "🍦", "🍮", "🍭", "🍵", "☕", "🍫", "🍯", "🥞", "🥨", "🥯", "🧇", "🧀", "🥐", "🥖", "🥛", "🍪", "🎂", "🍡"]
    for cafe, similarity, keyword, id, colors, pop, review_count, seasonal, nagativereview, sentiment_0_count in recommendations[:5]:
        random_symbol = random.choice(symbols)
        place_url = f"https://map.naver.com/p/smart-around/place/{id}"
        hot_place_text = "<p style='color: red; font-weight: bold;'>최근 3개월간 HOT PLACE🔥</p>" if str(pop).strip().lower() == "hot" else ""
        seasonal_html = f"<p style='color: rgb(81, 128, 190); font-weight: bold;'>이 계절에 인기 있어요! :</p>{get_season_emojis(seasonal)}" if seasonal.strip().lower() != "none" else ""
        negative_html = (
            f"<p style='margin: 0; font-weight: bold; color: rgb(79, 28, 8);'>🤔 부정 리뷰 개수 : {sentiment_0_count}</p>"
            f"<p style='margin: 0; color: rgb(122, 68, 32);'>👀 최근 부정 리뷰 : {nagativereview}</p>" if sentiment_0_count > 0 else ""
        )
        color_boxes = ''.join(f"<div style='width: 20px; height: 20px; background-color: rgb{tuple(color)}; margin-right: 3px; display: inline-block;'></div>" for color in colors)
        cafe_html = f"""
        <div style='padding: 15px; border: 1px solid rgb(245, 225, 205); border-radius: 10px; margin-bottom: 20px; background-color: rgb(255, 251, 241); min-height: 300px;'>
            <b>{random_symbol} <a href="{place_url}" target="_blank" style="text-decoration: none; color: rgb(79, 28, 8); font-size: 18px;" title="해당 URL로 이동합니다">{cafe}</a></b>
            <p style="color: rgb(237, 169, 0);"><strong>대표 키워드:</strong> {keyword}</p>
            {hot_place_text}
            <p style="color: rgb(122, 68, 32); font-weight: bold;">최근 한달 등록된 리뷰 개수: {review_count}</p>
            {negative_html}
            {seasonal_html}
            <p style="color: rgb(122, 68, 32); font-weight: bold;">카페 색상 테마:</p>
            <div style="display: flex; gap: 3px;">
                {color_boxes}
            </div>
            
        </div>
        """
        components.html(cafe_html, height=400)

# LDA 모델 및 벡터라이저 로드
try:
    lda_model = joblib.load('lda_model.pkl')
except Exception as e:
    st.error(f"LDA 모델 로드 실패: {e}")

try:
    vectorizer = joblib.load('vectorizer.pkl')
except Exception as e:
    st.error(f"벡터라이저 로드 실패: {e}")

# 데이터 로드
data_path = "e:/pickca/streamlit/"
merged_file_name = "merged_cafe_data.csv"
naver_map_url = "https://map.naver.com/p/smart-around/place/"
data = load_merged_data(data_path, merged_file_name)

mood_list = [
    "혼자 가기 좋은 카페",
    "혼자 공부하기 좋은 카페",
    "조용하고 혼자 가기 좋은 카페",
    "좌석 간격이 넓은 카페",
    "아늑한 카페",
    "좌석이 편안한 카페",
    "가성비 좋은 카페",
    "인스타 감성 카페",
    "20대가 데이트하기 좋은 카페",
    "30대가 데이트하기 좋은 카페",
    "데이트하기 좋은 카페",
    "배경 음악 좋은 카페",
    "가족과 함께 가기 좋은 카페",
    "아이들이 가기 좋은 카페",
    "오래 머물기 좋은 카페",
]

if not data.empty:
    # 사용자 입력 필드
    user_input = st.text_area("원하는 카페 분위기를 입력해주세요! :", placeholder="새로운 카페를 탐험하고 싶다면 RandomPICK 버튼을 눌러보세요!")
    
    # 색상 선택 기능 추가
    unique_colors = sorted(set(color for color_list in data["colors"] for color in color_list))
    st.markdown("<span style='color: rgb(122, 68, 32); font-size: 14px;'><b>원하는 카페 색상도 고를 수 있어요(옵션):</b></span>", unsafe_allow_html=True)
    
    cols_per_row = 10
    rows = (len(unique_colors) + cols_per_row - 1) // cols_per_row
    color_idx = 0
    
    for _ in range(rows):
        cols = st.columns(cols_per_row)
        for col in cols:
            if color_idx >= len(unique_colors):
                break
            color = unique_colors[color_idx]
            r, g, b = color
            color_hex = f'#{r:02x}{g:02x}{b:02x}'
            is_selected = color in st.session_state.selected_colors
            
            col.markdown(f"<div style='width: 40px; height: 40px; background-color: {color_hex};'></div>", unsafe_allow_html=True)
            if col.checkbox('', key=f'color_{color_idx}', help=f"RGB{color}"):
                if color not in st.session_state.selected_colors:
                    st.session_state.selected_colors.append(color)
            else:
                if color in st.session_state.selected_colors:
                    st.session_state.selected_colors.remove(color)
            color_idx += 1
    
    selected_colors = st.session_state.selected_colors

    # 버튼 배치
    col1, col2 = st.columns([1, 1])
    pick_button = col1.button("PICK")
    random_button = col2.button(
    "RandomPICK", 
    help="입력 텍스트와 색상 선택과 무관하게 무작위로 추천됩니다!")
    
    recommendations = []  # 결과를 저장할 리스트
    mood_used = ""  # RandomPick 사용 시 선택된 분위기

    if pick_button and user_input.strip():
        # PICK 버튼 클릭 시
        user_topic_dist = get_topic_distribution(user_input, lda_model, vectorizer)
        for row in data.itertuples(index=False):
            # 색상 필터링 조건 추가
            if selected_colors:
                if not set(row.colors).intersection(set(selected_colors)):
                    continue  # 선택한 색상과 겹치지 않으면 건너뜀
            
            similarity = cosine_similarity(
                np.array(user_topic_dist).reshape(1, -1),
                np.array(row.degree_of_fit).reshape(1, -1)
            )[0][0]
            recommendations.append((
                row.cafe, similarity, row.keyword, row.id, row.colors,
                row.pop, row.review_count, row.seasonal, row.nagativereview, row.sentiment_0_count
            ))

        recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    elif random_button:
        # RandomPick 버튼 클릭 시
        mood_used = random.choice(mood_list)
        st.info(f"랜덤으로 선택된 분위기: **{mood_used}**")
        user_topic_dist = get_topic_distribution(mood_used, lda_model, vectorizer)

        for row in data.itertuples(index=False):
            similarity = cosine_similarity(
                np.array(user_topic_dist).reshape(1, -1),
                np.array(row.degree_of_fit).reshape(1, -1)
            )[0][0]
            recommendations.append((
                row.cafe, similarity, row.keyword, row.id, row.colors,
                row.pop, row.review_count, row.seasonal, row.nagativereview, row.sentiment_0_count
            ))

        recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    # 결과 출력
    if recommendations:
        message = "오늘의 카페를 추천드릴게요😊" if not mood_used else f"모험을 떠날 준비가 되셨나요👩🏻‍🚀"
        display_recommendations(recommendations, message)
    elif pick_button or random_button:
        st.warning("조건에 맞는 카페를 찾을 수 없습니다😫")
else:
    st.error("데이터를 로드하는 데 실패했습니다.")
