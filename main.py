import streamlit as st
import pandas as pd
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울-양평 기온 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 비교 및 전력수요 분석")
st.markdown("본 웹앱은 2025년 시간별 데이터를 바탕으로 도시 열섬현상과 기온에 따른 전력수요 변화를 분석합니다.")

# 2. 파일 존재 여부 검사 (에러 방지 안전장치)
required_files = ["서울_기온.csv", "양평_기온.csv", "전력수요.csv"]
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    st.error("⚠️ 현재 폴더에 데이터 파일이 없습니다! 아래 파일들을 같은 폴더에 업로드해 주세요.")
    for f in missing_files:
        st.write(f"- `{f}`")
    st.info("💡 파일들을 업로드하면 자동으로 분석이 시작됩니다.")
    st.stop()

# 3. 데이터 로드 및 전처리 함수
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
    
    # 필요한 컬럼 정제 및 이름 변경
    seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
    yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
    power = power[['일시', '전력수요(MWh)']]
    
    # [탭1용 데이터] 서울 기온 + 양평 기온 병합
    df_temp = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # [탭2용 데이터] 서울 기온 + 전력수요 병합
    df_power = pd.merge(seoul, power, on='일시', how='inner')
    df_power['월'] = df_power['일시'].dt.month
    # 5도 단위 기온 구간 생성 (예: 23.5도 -> 20도 구간)
    df_power['기온구간'] = (df_power['서울_기온'] // 5 * 5).astype(int)
    
    return df_temp, df_power

# 데이터 불러오기 실행
try:
    df_temp, df_power = load_all_data()
    
    # 4. 탭 구성
    tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # --------------------------------------------------
    # [탭1: 열섬 분석]
    # --------------------------------------------------
    with tab1:
        st.header("도시 열섬현상 분석 (서울 vs 양평)")
        st.markdown("서울(대도시)과 양평(교외)의 기온 차이를 통해 도시 열섬현상을 관측합니다.")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        chart_data_line = df_temp.set_index('일시')[['서울_기온', '양평_기온']]
        st.line_chart(chart_data_line, y_label="기온 (°C)")
        
        # 시각별, 월별 그래프 레이아웃 분할
        col1, col2 = st.columns(2)
        
        # ② 시각(0~23시)별 평균 기온차 (막대그래프)
        with col1:
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hourly_diff = df_temp.groupby('시각')['기온차(서울-양평)'].mean()
            st.bar_chart(hourly_diff, y_label="평균 기온차 (°C)", x_label="시각 (시)")
            st.caption("💡 야간과 새벽 시간에 서울의 기온이 인공열과 콘크리트 축열로 인해 높게 유지되는 경향이 있습니다.")
            
        # ③ 월(1~12월)별 평균 기온차 (막대그래프)
        with col2:
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            monthly_diff = df_temp.groupby('월')['기온차(서울-양평)'].mean()
            st.bar_chart(monthly_diff, y_label="평균 기온차 (°C)", x_label="월 (월)")
            st.caption("💡 계절 변화와 계절풍, 대기 상태에 따른 두 지역 간의 열 집적 차이를 보여줍니다.")

    # --------------------------------------------------
    # [탭2: 전력 연결]
    # --------------------------------------------------
    with tab2:
        st.header("기온과 전력수요의 상관관계 분석")
        st.markdown("서울의 기온 변화가 냉·난방 에너지 소비(전력수요)에 미치는 영향을 분석합니다.")
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온 vs 전력수요 산점도")
        st.scatter_chart(
            df_power, 
            x='서울_기온', 
            y='전력수요(MWh)', 
            x_label='서울 기온 (°C)', 
            y_label='전력수요 (MWh)'
        )
        st.caption("💡 기온이 매우 낮거나(난방 수요) 매우 높을 때(냉방 수요) 전력수요가 상승하는 구조적인 변화를 확인할 수 있습니다.")
        
        # 구간별, 월별 그래프 레이아웃 분할
        col3, col4 = st.columns(2)
        
        # ② 기온 구간별 평균 전력수요 (막대그래프)
        with col3:
            st.subheader("② 기온 구간별 평균 전력수요 (5°C 단위)")
            bin_power = df_power.groupby('기온구간')['전력수요(MWh)'].mean()
            st.bar_chart(bin_power, y_label="평균 전력수요 (MWh)", x_label="기온 구간 시작값 (°C)")
            st.caption("💡 특정 기온 임계점(예: 25°C 이상 또는 0°C 이하)을 넘어설 때 전력량이 급증하는 구간이 한눈에 보입니다.")
            
        # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
        with col4:
            st.subheader("③ 월별 평균 전력수요")
            monthly_power = df_power.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(monthly_power, y_label="평균 전력수요 (MWh)", x_label="월 (월)")
            st.caption("💡 여름철(7~8월) 폭염 시 냉방과 겨울철(12~1월) 한파 시 난방에 따른 월별 수요 변화입니다.")

except Exception as e:
    st.error(f"❌ 데이터를 처리하는 중 에러가 발생했습니다: {e}")
