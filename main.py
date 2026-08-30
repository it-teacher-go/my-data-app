import streamlit as st
import pandas as pd
import altair as alt


# =======================================
# 페이지 설정
# =======================================
st.set_page_config(
    page_title="서울 기온 변화",
    page_icon="🌡️",
    layout="wide"
)


# =======================================
# 데이터 주소
# =======================================
DATA_URL = (
    "https://raw.githubusercontent.com/"
    "greatsong/modudata/main/data/seoul.csv"
)


# =======================================
# 데이터 불러오기
# =======================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 기온 열을 숫자 형식으로 변환
    for column in [
        "평균기온",
        "최저기온",
        "최고기온"
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# =======================================
# 데이터 불러오기
# =======================================
df = load_data()


# =======================================
# 제목
# =======================================
st.title("🌡️ 서울의 연평균 기온 변화")

st.write(
    "서울의 기온 데이터를 이용하여 "
    "100년 동안 연평균 기온이 어떻게 변해 왔는지 "
    "살펴봅니다."
)


# =======================================
# 원본 데이터 요약통계
# =======================================
st.subheader("📊 원본 데이터 요약통계")

st.write(
    "원본 데이터의 지점, 평균기온, 최저기온, "
    "최고기온에 대한 요약통계입니다."
)

summary = df[
    [
        "지점",
        "평균기온",
        "최저기온",
        "최고기온"
    ]
].describe()

# 통계 항목을 한국어로 변경
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


# =======================================
# 연도별 연평균 기온 계산
# =======================================
df["연도"] = df["날짜"].dt.year

yearly_temp = (
    df.groupby("연도")["평균기온"]
    .mean()
)

# 데이터에 존재하는 전체 연도 범위 생성
all_years = range(
    int(df["연도"].min()),
    int(df["연도"].max()) + 1
)

# 존재하지 않는 연도는 NaN으로 처리
yearly_temp = yearly_temp.reindex(all_years)

yearly_temp.index.name = "연도"


# =======================================
# 유난히 낮은 연도 기준 계산
# =======================================
valid_temp = yearly_temp.dropna()

mean_temp = valid_temp.mean()
std_temp = valid_temp.std()

# 평균보다 2표준편차 이상 낮은 연도
low_threshold = mean_temp - (2 * std_temp)


# =======================================
# 그래프
# =======================================
st.subheader("📈 연도별 연평균 기온")


# ---------------------------------------
# 표시 옵션
# ---------------------------------------
col1, col2 = st.columns(2)

with col1:
    show_missing = st.checkbox(
        "⚠️ 결측 연도 표시",
        value=True
    )

with col2:
    show_low = st.checkbox(
        "🔵 유난히 낮은 연도 표시",
        value=True
    )


# ---------------------------------------
# 그래프용 데이터
# ---------------------------------------
chart_df = yearly_temp.reset_index()

chart_df = chart_df.rename(
    columns={
        "평균기온": "연평균기온"
    }
)

# 결측 여부
chart_df["결측"] = (
    chart_df["연평균기온"].isna()
)

# 유난히 낮은 연도 여부
chart_df["유난히 낮음"] = (
    chart_df["연평균기온"] < low_threshold
)


# ---------------------------------------
# 기본 연평균 기온 선
# ---------------------------------------
line = (
    alt.Chart(chart_df)
    .mark_line(
        point=True
    )
    .encode(
        x=alt.X(
            "연도:Q",
            title="연도"
        ),
        y=alt.Y(
            "연평균기온:Q",
            title="연평균 기온 (℃)"
        ),
        tooltip=[
            alt.Tooltip(
                "연도:Q",
                title="연도"
            ),
            alt.Tooltip(
                "연평균기온:Q",
                title="연평균 기온",
                format=".2f"
            )
        ]
    )
)


charts = [line]


# ---------------------------------------
# 유난히 낮은 연도 표시
# ---------------------------------------
if show_low:

    low_df = chart_df[
        chart_df["유난히 낮음"]
    ].dropna(
        subset=["연평균기온"]
    )

    if not low_df.empty:

        low_points = (
            alt.Chart(low_df)
            .mark_point(
                size=180
            )
            .encode(
                x=alt.X("연도:Q"),
                y=alt.Y("연평균기온:Q"),
                tooltip=[
                    alt.Tooltip(
                        "연도:Q",
                        title="유난히 낮은 연도"
                    ),
                    alt.Tooltip(
                        "연평균기온:Q",
                        title="연평균 기온",
                        format=".2f"
                    )
                ]
            )
        )

        charts.append(low_points)


# ---------------------------------------
# 결측 연도 표시
# ---------------------------------------
if show_missing:

    missing_df = chart_df[
        chart_df["결측"]
    ].copy()

    if not missing_df.empty:

        # 결측 연도는 실제 기온값이 없으므로
        # 그래프 하단에 표시
        missing_points = (
            alt.Chart(missing_df)
            .mark_point(
                size=180
            )
            .encode(
                x=alt.X("연도:Q"),
                y=alt.value(0),
                tooltip=[
                    alt.Tooltip(
                        "연도:Q",
                        title="결측 연도"
                    )
                ]
            )
        )

        charts.append(missing_points)


# ---------------------------------------
# 그래프 합치기
# ---------------------------------------
chart = charts[0]

for extra_chart in charts[1:]:
    chart = chart + extra_chart


chart = (
    chart
    .properties(
        height=500
    )
    .interactive()
)


# 그래프 출력
st.altair_chart(
    chart,
    use_container_width=True
)


st.caption(
    "💡 체크박스를 이용하여 결측 연도와 "
    "유난히 낮은 연도의 표시를 켜거나 끌 수 있습니다."
)


# =======================================
# 연도별 데이터
# =======================================
with st.expander(
    "📋 연도별 연평균 기온 데이터 보기"
):

    display_data = (
        yearly_temp
        .reset_index()
    )

    display_data = display_data.rename(
        columns={
            "평균기온": "연평균기온"
        }
    )

    display_data["연평균기온"] = (
        display_data["연평균기온"]
        .round(2)
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# =======================================
# 원본 데이터
# =======================================
with st.expander(
    "📄 원본 데이터 보기"
):

    st.dataframe(
        df.drop(
            columns=["연도"]
        ),
        use_container_width=True,
        hide_index=True
    )
