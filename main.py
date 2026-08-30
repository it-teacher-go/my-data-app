```python
import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 제목
st.title("🌡️ 서울의 연평균 기온 변화")
st.write("서울의 기온 데이터를 이용해 연도별 평균 기온이 어떻게 변해 왔는지 살펴봅니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자 형식으로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 유효하지 않은 데이터 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


try:
    df = load_data()

    # 날짜에서 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균 기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
        .rename(columns={"평균기온": "연평균기온"})
    )

    # 100년 범위로 표시
    yearly_temp = yearly_temp.sort_values("연도")

    # 주요 정보
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("관측 시작 연도", f"{yearly_temp['연도'].min()}년")

    with col2:
        st.metric("관측 종료 연도", f"{yearly_temp['연도'].max()}년")

    with col3:
        st.metric("연도별 데이터 수", f"{len(yearly_temp)}년")

    st.subheader("연도별 연평균 기온")

    # 그래프용 데이터
    chart_data = yearly_temp.set_index("연도")

    st.line_chart(
        chart_data["연평균기온"],
        y_label="연평균 기온 (℃)",
        x_label="연도"
    )

    st.caption("※ 연평균 기온은 해당 연도의 일평균 기온 자료를 평균하여 계산합니다.")

    # 원하면 원본 데이터를 확인할 수 있도록 제공
    with st.expander("연도별 평균 기온 데이터 보기"):
        display_data = yearly_temp.copy()
        display_data["연평균기온"] = display_data["연평균기온"].round(2)
        st.dataframe(display_data, use_container_width=True)

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.info("잠시 후 다시 실행하거나 데이터 주소를 확인해 주세요.")
```
