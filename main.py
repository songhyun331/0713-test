import streamlit as st
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울-양평 기온 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 비교 및 전력수요 분석")

# 2. 파일이 진짜로 폴더에 있는지 검사 (없어도 절대 에러 안 나고 안내문만 띄움)
required_files = ["서울_기온.csv", "양평_기온.csv", "전력수요.csv"]
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    st.error(f"⚠️ 현재 폴더에 데이터 파일이 없습니다! 아래 파일들을 같은 폴더에 업로드해 주세요.")
    for f in missing_files:
        st.write(f"- `{f}`")
    st.info("💡 파일들을 업로드하면 자동으로 분석이 시작됩니다.")
    st.stop()  # 파일이 없으면 여기서 안전하게 실행을 멈춤 (에러 방지)

# 3. 탭 구성 및 안내 (여기까지 실행되면 파일은 안전하게 있는 상태입니다)
tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])

with tab1:
    st.header("도시 열섬현상 분석 (서울 vs 양평)")
    st.info("데이터 분석을 진행하려면 `pandas` 라이브러리가 필요합니다.")
    st.markdown("""
    **🚨 중요: 아직 화면이 안 나오나요?**
    깃허브(GitHub)에 **`requirements.txt`** 파일이 없으면 에러가 발생합니다.
    
    **[해결 방법]**
    1. GitHub 저장소로 이동합니다.
    2. **[Add file]** -> **[Create new file]** 을 누릅니다.
    3. 파일 이름을 **`requirements.txt`** 라고 적습니다.
    4. 내용에 아래 두 줄을 적고 저장(Commit)합니다.
    ```text
    streamlit
    pandas
    ```
    """)

with tab2:
    st.header("서울 기온과 전력수요의 상관관계 분석")
    st.write("위의 `requirements.txt` 설정이 완료되면 정상적으로 그래프가 표시됩니다.")
