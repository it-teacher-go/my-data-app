import streamlit as st
import pandas as pd
import plotly.express as px

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

    # 날짜와 평균기온이 없는 데이터 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


# 데이터 불러오기
df = load_data()

# 제목
st.title("🌡️ 서울의 연평균 기온 변화")
st.write(
    "서울의 기온 데이터를 이용하여 100년 동안 "
    "연평균 기온이 어떻게 변해 왔는지 살펴봅니다."
)


# ---------------------------------------
# 원본 데이터 요약통계
# ---------------------------------------
st.subheader("📊 원본 데이터 요약통계")

st.write(
    "원본 데이터의 평균기온, 최저기온, 최고기온에 대한 요약통계입니다."
)

summary = df[["평균기온", "최저기온", "최고기온"]].describe()

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


# ---------------------------------------
# 연도별 연평균 기온 계산
# ---------------------------------------
df["연도"] = df["날짜"].dt.year

yearly_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
    .reset_index()
)

yearly_temp.columns = ["연도", "연평균기온"]
yearly_temp = yearly_temp.sort_values("연도")


# ---------------------------------------
# 그래프
# ---------------------------------------
st.subheader("📈 연도별 연평균 기온")

fig = px.line(
    yearly_temp,
    x="연도",
    y="연평균기온",
    markers=True,
    labels={
        "연도": "연도",
        "연평균기온": "연평균 기온 (℃)"
    },
    title="서울 연도별 연평균 기온"
)

# 데이터가 없는 구간은 선으로 연결하지 않음
fig.update_traces(
    connectgaps=False,
    hovertemplate="연도: %{x}<br>연평균 기온: %{y:.2f} ℃<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    height=550
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.info(
    "💡 그래프에서 마우스로 원하는 구간을 드래그하면 확대할 수 있습니다."
)


# ---------------------------------------
# 연도별 데이터
# ---------------------------------------
with st.expander("📋 연도별 연평균 기온 데이터 보기"):
    display_data = yearly_temp.copy()
    display_data["연평균기온"] = display_data["연평균기온"].round(2)

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ---------------------------------------
# 원본 데이터
# ---------------------------------------
with st.expander("📄 원본 데이터 보기"):
    st.dataframe(
        df.drop(columns=["연도"]),
        use_container_width=True,
        hide_index=True
    )
