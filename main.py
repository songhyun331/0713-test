import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="도시 열섬 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 비교 및 전력수요 분석")

# 파일 존재 여부 먼저 확인
required_files = ["서울_기온.csv", "양평_기온.csv", "전력수요.csv"]
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    st.error(f"⚠️ 아래 파일이 누락되었습니다. 같은 폴더에 넣어주세요:\n{missing_files}")
    st.stop()  # 파일이 없으면 여기서 실행을 안전하게 중단 (앱 다운 방지)

# [데이터 로드 및 기본 전처리]
@st.cache_data
def load_data():
    seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
    power_df = pd.read_csv("전력수요.csv", encoding="cp949")
    
    seoul_df['일시'] = pd.to_datetime(seoul_df['일시'])
    yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'])
    power_df['일시'] = pd.to_datetime(power_df['일시'])
    
    return seoul_df, yangpyeong_df, power_df

seoul_raw, yangpyeong_raw, power_raw = load_data()

# 탭 구성
tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])

# [탭1: 열섬 분석]
with tab1:
    st.header("도시 열섬현상 분석 (서울 vs 양평)")
    df_temp = pd.merge(seoul_raw[['일시', '기온(°C)']], yangpyeong_raw[['일시', '기온(°C)']], on='일시', suffixes=('_서울', '_양평'))
    df_temp['시각'] = df_temp['일시'].dt.hour
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['기온차'] = df_temp['기온(°C)_서울'] - df_temp['기온(°C)_양평']
    
    st.subheader("① 1년간 두 지역 기온 변화 트렌드")
    df_line = df_temp.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
    df_line.columns = ['서울 기온', '양평 기온']
    st.line_chart(df_line)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        df_hour = df_temp.groupby('시각')['기온차'].mean().reset_index().set_index('시각')
        st.bar_chart(df_hour)
    with col2:
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        df_month = df_temp.groupby('월')['기온차'].mean().reset_index().set_index('월')
        st.bar_chart(df_month)

# [탭2: 전력 연결]
with tab2:
    st.header("서울 기온과 전력수요의 상관관계 분석")
    df_power = pd.merge(seoul_raw[['일시', '기온(°C)']], power_raw[['일시', '전력수요(MWh)']], on='일시')
    df_power['월'] = df_power['일시'].dt.month
    df_power['기온구간'] = pd.cut(df_power['기온(°C)'], bins=range(-20, 45, 5), labels=[f"{i}~{i+5}°C" for i in range(-20, 40, 5)])
    
    st.subheader("① 기온과 전력수요 산점도")
    st.scatter_chart(data=df_power, x='기온(°C)', y='전력수요(MWh)')
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("② 기온 구간별 평균 전력수요")
        df_bin = df_power.groupby('기온구간', observed=False)['전력수요(MWh)'].mean().reset_index().set_index('기온구간')
        st.bar_chart(df_bin)
    with col4:
        st.subheader("③ 월별 평균 전력수요")
        df_p_month = df_power.groupby('월')['전력수요(MWh)'].mean().reset_index().set_index('월')
        st.bar_chart(df_p_month)
