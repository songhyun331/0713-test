import streamlit as stimport streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="기온 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 비교 및 전력수요 연계 분석 웹앱")
st.markdown("본 웹앱은 2025년 시간별 데이터를 바탕으로 도시 열섬현상과 기온에 따른 전력수요 변화를 분석합니다.")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_all_data():
    # 파일 읽기 (cp949 인코딩 반영)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    power['일시'] = pd.to_datetime(power['일시'])
    
    # 필요한 컬럼 정제
    seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
    yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
    power = power[['일시', '전력수요(MWh)']]
    
    # 데이터 병합
    # 탭1용: 서울 + 양평
    df_temp = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # 탭2용: 서울 + 전력수요
    df_power = pd.merge(seoul, power, on='일시', how='inner')
    df_power['월'] = df_power['일시'].dt.month
    
    # 기온 구간(5도 단위) 컬럼 추가
    # 예: -5도 이상 0도 미만 -> -5, 20도 이상 25도 미만 -> 20
    df_power['기온구간'] = (df_power['서울_기온'] // 5 * 5).astype(int)
    
    return df_temp, df_power

# 데이터 불러오기 공통 처리
try:
    df_temp, df_power = load_all_data()
    
    # 3. 탭 구성
    tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # --------------------------------------------------
    # [탭1: 열섬 분석]
    # --------------------------------------------------
    with tab1:
        st.header("도시 열섬현상 분석")
        st.markdown("서울(대도시)과 양평(교외)의 기온 차이를 통해 열섬현상을 관측합니다.")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        chart_data_line = df_temp.set_index('일시')[['서울_기온', '양평_기온']]
        st.line_chart(chart_data_line, y_label="기온 (°C)")
        
        # 레이아웃 분할
        col1, col2 = st.columns(2)
        
        # ② 시각별 평균 기온차 (막대그래프)
        with col1:
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hourly_diff = df_temp.groupby('시각')['기온차(서울-양평)'].mean()
            st.bar_chart(hourly_diff, y_label="평균 기온차 (°C)", x_label="시각 (시)")
            st.caption("💡 주로 야간과 새벽 시간에 서울의 기온이 높게 유지되는 열섬 특성이 관측됩니다.")
            
        # ③ 월별 평균 기온차 (막대그래프)
        with col2:
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            monthly_diff = df_temp.groupby('월')['기온차(서울-양평)'].mean()
            st.bar_chart(monthly_diff, y_label="평균 기온차 (°C)", x_label="월 (월)")
            st.caption("💡 계절 변화에 따른 대도시와 전원 지역 간의 열 축적 차이를 볼 수 있습니다.")

    # --------------------------------------------------
    # [탭2: 전력 연결]
    # --------------------------------------------------
    with tab2:
        st.header("기온과 전력수요의 상관관계 분석")
        st.markdown("서울의 기온 변화가 냉·난방 에너지(전력수요)에 미치는 영향을 분석합니다.")
        
        # ① 기온과 전력수요의 산점도 (Scatter Chart)
        st.subheader("① 기온 vs 전력수요 산점도")
        st.scatter_chart(
            df_power, 
            x='서울_기온', 
            y='전력수요(MWh)', 
            x_label='서울 기온 (°C)', 
            y_label='전력수요 (MWh)'
        )
        st.caption("💡 기온이 너무 낮거나(난방) 높은(냉방) 구간에서 전력수요가 급증하는 U자형 곡선이 나타나는 경향이 있습니다.")
        
        # 레이아웃 분할
        col3, col4 = st.columns(2)
        
        # ② 기온 구간별 평균 전력수요 (막대그래프)
        with col3:
            st.subheader("② 기온 구간별 평균 전력수요 (5°C 단위)")
            # 구간별 평균 계산 후 인덱스(기온구간) 정렬
            bin_power = df_power.groupby('기온구간')['전력수요(MWh)'].mean()
            st.bar_chart(bin_power, y_label="평균 전력수요 (MWh)", x_label="기온 구간 시작값 (°C)")
            st.caption("💡 특정 기온 임계점을 넘어설 때 전력수요가 얼마나 급증하는지 직관적으로 보여줍니다.")
            
        # ③ 월별 평균 전력수요 (막대그래프)
        with col4:
            st.subheader("③ 월별 평균 전력수요")
            monthly_power = df_power.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(monthly_power, y_label="평균 전력수요 (MWh)", x_label="월 (월)")
            st.caption("💡 여름철(7~8월) 냉방 및 겨울철(12~1월) 난방 수요의 크기를 비교할 수 있습니다.")

except FileNotFoundError:
    st.error("❌ '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일 중 찾을 수 없는 파일이 있습니다. 스크립트와 같은 폴더에 있는지 확인해주세요.")
except Exception as e:
    st.error(f"❌ 에러가 발생했습니다: {e}")
