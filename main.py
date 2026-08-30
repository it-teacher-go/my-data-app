import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 기온 데이터 분석",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    return df


st.title("🌡️ 서울의 연평균 기온 변화")
st.write("서울 기온 데이터를 이용해 100년 동안의 연평균 기온 변화를 살펴봅니다.")

try:
    df = load_data()

    # ---------------------------------------
    # 원본 데이터 요약통계
    # ---------------------------------------
    st.subheader("📊 원본 데이터 요약통계")

    # 원본 데이터의 평균기온에 대한 통계
    stats = df["평균기온"].describe()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("개수", f"{stats['count']:.0f}")

    with col2:
        st.metric("평균", f"{stats['mean']:.2f} ℃")

    with col3:
        st.metric("최소", f"{stats['min']:.2f} ℃")

    with col4:
        st.metric("최대", f"{stats['max']:.2f} ℃")

    # ---------------------------------------
    # 연도별 연평균 기온 계산
    # ---------------------------------------
    df["연도"] = df["날짜"].dt.year

    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
        .rename(columns={"평균기온": "연평균기온"})
        .sort_values("연도")
    )

    # ---------------------------------------
    # 연평균 기온 그래프
    # ---------------------------------------
    st.subheader("📈 연도별 연평균 기온")

    chart_data = yearly_temp.set_index("연도")

    st.line_chart(
        chart_data["연평균기온"],
        y_label="연평균 기온 (℃)",
        x_label="연도"
    )

    st.caption(
        "※ 원본 데이터의 일별 평균기온을 연도별로 평균하여 연평균 기온을 계산했습니다."
    )

    # ---------------------------------------
    # 원본 데이터 보기
    # ---------------------------------------
    with st.expander("📋 원본 데이터 보기"):
        st.dataframe(
            df.drop(columns=["연도"]),
            use_container_width=True,
            hide_index=True
        )

except Exception:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.info("잠시 후 다시 실행하거나 데이터 주소를 확인해 주세요.")

