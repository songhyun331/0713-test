import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")
st.title("🏙️ 서울 vs 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("본 웹앱은 서울(대도시)과 양평(교외)의 2025년 시간별 기온 데이터를 비교하여 도시 열섬현상을 시각화합니다.")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 파일 읽기 (cp949 인코딩 반영)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    
    # 필요한 컬럼만 추출 및 이름 변경
    seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울'})
    yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평'})
    
    # 일시 기준으로 데이터 병합
    df = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    
    # 기온 차이 계산 (서울 - 양평)
    df['기온차(서울-양평)'] = df['서울'] - df['양평']
    
    # 분석을 위한 월, 시각 컬럼 추출
    df['월'] = df['일시'].dt.month
    df['시각'] = df['일시'].dt.hour
    
    return df

# 데이터 불러오기
try:
    df = load_data()
    
    # --------------------------------------------------
    # ① 1년간 두 지역의 기온 변화 (선그래프)
    # --------------------------------------------------
    st.subheader("① 1년간 두 지역의 기온 변화 트렌드")
    
    # 시각화를 위해 일시를 인덱스로 설정한 선그래프용 데이터프레임 생성
    chart_data_line = df.set_index('일시')[['서울', '양평']]
    st.line_chart(chart_data_line, y_label="기온 (°C)")
    
    
    # 레이아웃 분할 (시간별, 월별 그래프를 나란히 배치)
    col1, col2 = st.columns(2)
    
    # --------------------------------------------------
    # ② 시각(0~23시)별 평균 기온차 (막대그래프)
    # --------------------------------------------------
    with col1:
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        # 시각별 평균 계산
        hourly_diff = df.groupby('시각')['기온차(서울-양평)'].mean()
        st.bar_chart(hourly_diff, y_label="기온차 (°C)", x_label="시각 (시)")
        st.caption("💡 주로 야간과 새벽 시간에 서울의 기온이 양평보다 확연히 높은 열섬현상이 두드러집니다.")

    # --------------------------------------------------
    # ③ 월(1~12월)별 평균 기온차 (막대그래프)
    # --------------------------------------------------
    with col2:
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        # 월별 평균 계산
        monthly_diff = df.groupby('월')['기온차(서울-양평)'].mean()
        st.bar_chart(monthly_diff, y_label="기온차 (°C)", x_label="월 (월)")
        st.caption("💡 계절별로 대도시와 교외 지역 간의 평균적인 기온 차이를 확인할 수 있습니다.")

    # --------------------------------------------------
    # 데이터 요약 정보 제공
    # --------------------------------------------------
    st.markdown("---")
    st.subheader("📊 데이터 요약 통계")
    
    mean_seoul = df['서울'].mean()
    mean_yp = df['양평'].mean()
    mean_diff = df['기온차(서울-양평)'].mean()
    max_diff = df['기온차(서울-양평)'].max()
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("서울 평균 기온", f"{mean_seoul:.1f} °C")
    m_col2.metric("양평 평균 기온", f"{mean_yp:.1f} °C")
    m_col3.metric("연평균 기온차", f"{mean_diff:.1f} °C", help="서울 기온 - 양평 기온")
    m_col4.metric("최대 기온차", f"{max_diff:.1f} °C")

except FileNotFoundError:
    st.error("❌ '서울_기온.csv' 또는 '양평_기온.csv' 파일을 찾을 수 없습니다. 파이썬 스크립트와 같은 폴더에 파일이 있는지 확인해주세요.")
except Exception as e:
    st.error(f"❌ 에러가 발생했습니다: {e}")
