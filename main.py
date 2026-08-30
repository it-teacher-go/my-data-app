import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 기온 열을 숫자 형식으로 변환
    for column in ["평균기온", "최저기온", "최고기온"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


# -----------------------------
# 데이터 불러오기
# -----------------------------
df = load_data()

st.title("🌡️ 서울의 기온 변화")
st.write("서울의 기온 데이터를 이용하여 100년 동안 연평균 기온이 어떻게 변해 왔는지 살펴봅니다.")


# -----------------------------
# 원본 데이터 요약통계
# -----------------------------
st.subheader("📊 원본 데이터 요약통계")

st.write(
    "원본 데이터의 수치형 열에 대한 요약통계입니다."
)

# 수치형 데이터의 요약통계
summary = df[["평균기온", "최저기온", "최고기온"]].describe()

# 보기 좋게 행과 열을 변경
summary = summary.rename(
    index={
        "count": "개수",
        "mean": "평균",
        "std": "표준편차",
        "min": "최소",
        "25%": "25%",
        "50%": "50% (중앙값)",
        "75%": "75%",
        "max": "최대"
    }
)

summary = summary.round(2)

st.dataframe(
    summary,
    use_container_width=True
)


# -----------------------------
# 연도별 연평균 기온 계산
# -----------------------------
df["연도"] = df["날짜"].dt.year

yearly_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

yearly_temp.columns = ["연도", "연평균기온"]

yearly_temp = yearly_temp.sort_values("연도")


# -----------------------------
# 연평균 기온 그래프
# -----------------------------
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


# -----------------------------
# 연도별 데이터
# -----------------------------
with st.expander("📋 연도별 연평균 기온 데이터 보기"):
    display_data = yearly_temp.copy()
    display_data["연평균기온"] = display_data["연평균기온"].round(2)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# 원본 데이터
# -----------------------------
with st.expander("📄 원본 데이터 보기"):
    st.dataframe(
        df.drop(columns=["연도"]),
        use_container_width=True,
        hide_index=True
    )
