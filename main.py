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

# 지점을 포함한 요약통계
summary = df[
    ["지점", "평균기온", "최저기온", "최고기온"]
].describe()

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

yearly_temp = df.groupby("연도")["평균기온"].mean()

# 전체 연도 범위를 만들고,
# 데이터가 없는 연도는 NaN으로 남김
all_years = range(
    int(df["연도"].min()),
    int(df["연도"].max()) + 1
)

yearly_temp = yearly_temp.reindex(all_years)
yearly_temp.index.name = "연도"


# ---------------------------------------
# 연평균 기온 그래프
# ---------------------------------------
st.subheader("📈 연도별 연평균 기온")

st.line_chart(
    yearly_temp,
    y_label="연평균 기온 (℃)",
    x_label="연도"
)

st.caption(
    "※ 데이터가 없는 연도는 그래프에서 선으로 연결하지 않습니다."
)


# ---------------------------------------
# 연도별 데이터
# ---------------------------------------
with st.expander("📋 연도별 연평균 기온 데이터 보기"):
    display_data = yearly_temp.reset_index()
    display_data["연평균기온"] = display_data["평균기온"].round(2)
    display_data = display_data[["연도", "연평균기온"]]

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
