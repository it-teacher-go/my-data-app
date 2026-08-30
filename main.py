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


# ---------------------------------------
# 데이터 불러오기
# ---------------------------------------
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


# ---------------------------------------
# 제목
# ---------------------------------------
st.title("🌡️ 서울의 연평균 기온 변화")

st.write(
    "서울의 기온 데이터를 이용하여 100년 동안 "
    "연평균 기온이 어떻게 변해 왔는지 살펴봅니다."
)


# ---------------------------------------
# 원본 데이터 요약통계
# ---------------------------------------
st.subheader("📊 원본 데이터 요약통계")

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

# 전체 연도 범위 생성
all_years = range(
    int(df["연도"].min()),
    int(df["연도"].max()) + 1
)

# 데이터가 없는 연도는 NaN
yearly_temp = yearly_temp.reindex(all_years)
yearly_temp.index.name = "연도"


# ---------------------------------------
# 유난히 낮은 연도 찾기
# ---------------------------------------
valid_temp = yearly_temp.dropna()

mean_temp = valid_temp.mean()
std_temp = valid_temp.std()

# 평균보다 2표준편차 이상 낮은 연도
low_threshold = mean_temp - (2 * std_temp)

low_years = yearly_temp[
    yearly_temp < low_threshold
].dropna()


# ---------------------------------------
# 그래프용 데이터
# ---------------------------------------
chart_df = yearly_temp.to_frame("연평균기온")

# 결측 연도 표시용
chart_df["결측"] = chart_df["연평균기온"].isna()

# 유난히 낮은 연도 표시용
chart_df["유난히 낮음"] = chart_df["연평균기온"] < low_threshold


# ---------------------------------------
# 연평균 기온 그래프
# ---------------------------------------
st.subheader("📈 연도별 연평균 기온")

st.line_chart(
    chart_df[["연평균기온"]],
    y_label="연평균 기온 (℃)",
    x_label="연도"
)


# 이상 연도 표시
st.markdown("### 🔎 이상 구간 확인")

col1, col2 = st.columns(2)

with col1:
    st.write("⚠️ **연평균 기온 데이터가 없는 연도**")

    missing_years = chart_df[
        chart_df["결측"]
    ].index.tolist()

    if missing_years:
        st.write(
            ", ".join(f"{year}년" for year in missing_years)
        )
    else:
        st.write("결측 연도가 없습니다.")

with col2:
    st.write("🔵 **유난히 낮은 연도**")

    if len(low_years) > 0:
        st.write(
            ", ".join(
                f"{int(year)}년 ({temp:.2f}℃)"
                for year, temp in low_years.items()
            )
        )
    else:
        st.write("기준에 해당하는 연도가 없습니다.")


st.caption(
    f"※ '유난히 낮은 연도'는 전체 연평균 기온의 평균({mean_temp:.2f}℃)보다 "
    f"2표준편차 이상 낮은 연도로 정했습니다. "
    f"(기준: {low_threshold:.2f}℃ 미만)"
)


# ---------------------------------------
# 연도별 데이터
# ---------------------------------------
with st.expander("📋 연도별 연평균 기온 데이터 보기"):

    display_data = yearly_temp.reset_index()

    display_data = display_data.rename(
        columns={"평균기온": "연평균기온"}
    )

    display_data["연평균기온"] = display_data[
        "연평균기온"
    ].round(2)

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
