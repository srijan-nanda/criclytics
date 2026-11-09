import streamlit as st
import plotly.express as px
import pandas as pd

from analytics import (
    load_data,
    calculate_metrics,
    top_batters,
    top_bowlers,
    compare_players
)

st.set_page_config(
    page_title="Criclytics | Performance Intelligence",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0b1220;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background: #111c2e;
    }

    .hero {
        background: linear-gradient(120deg, #172c45, #123b37);
        padding: 30px;
        border-radius: 16px;
        border: 1px solid #29465a;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #ffffff;
        font-size: 36px;
        margin-bottom: 5px;
    }

    .hero p {
        color: #b8c8d8;
        margin-bottom: 0;
    }

    .metric-card {
        background: #152238;
        border: 1px solid #263951;
        border-radius: 14px;
        padding: 19px;
        min-height: 115px;
    }

    .metric-label {
        color: #9fb0c4;
        font-size: 13px;
        margin-bottom: 9px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 29px;
        font-weight: 700;
    }

    .section-heading {
        color: #f1f5f9;
        font-size: 22px;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 14px;
    }

    .info-text {
        color: #9fb0c4;
        font-size: 13px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #263951;
        border-radius: 10px;
    }

    .stButton button {
        border-radius: 9px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <h1>🏏 Criclytics</h1>
    <p>Cricket Performance Intelligence · Every statistic tells a story.</p>
</div>
""", unsafe_allow_html=True)


# ---------- DATA LOADING ----------
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.caption("Manage your cricket dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload player statistics",
    type=["csv"]
)

try:
    if uploaded_file:
        raw_data = load_data(uploaded_file)
        st.sidebar.success("Custom dataset loaded")
    else:
        raw_data = load_data("data/cricket_stats.csv")
        st.sidebar.info("Demo dataset active")

    df = calculate_metrics(raw_data)

except Exception as error:
    st.error(f"Unable to process the dataset: {error}")
    st.stop()


# ---------- FILTERS ----------
st.sidebar.divider()
st.sidebar.subheader("Filters")

teams = ["All Teams"] + sorted(df["team"].unique().tolist())

selected_team = st.sidebar.selectbox(
    "Select team",
    teams
)

filtered = (
    df.copy()
    if selected_team == "All Teams"
    else df[df["team"] == selected_team].copy()
)

if filtered.empty:
    st.warning("No players found for the selected filter.")
    st.stop()


# ---------- KPI CARDS ----------
st.markdown('<div class="section-heading">Performance Overview</div>',
            unsafe_allow_html=True)

total_runs = int(filtered["runs"].sum())
total_wickets = int(filtered["wickets"].sum())
player_count = len(filtered)
total_matches = int(filtered["matches"].max())

kpis = [
    ("PLAYERS", player_count),
    ("TOTAL RUNS", f"{total_runs:,}"),
    ("TOTAL WICKETS", total_wickets),
    ("MAX MATCHES PLAYED", max_matches_played)
]

cols = st.columns(4)

for col, (label, value) in zip(cols, kpis):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------- BATTING ANALYTICS ----------
st.markdown('<div class="section-heading">🏏 Batting Analytics</div>',
            unsafe_allow_html=True)

batting = top_batters(filtered)

left, right = st.columns([1, 1.3])

with left:
    st.markdown("**Top Run Scorers**")

    st.dataframe(
        batting[
            ["player", "team", "runs", "batting_average", "strike_rate"]
        ].rename(columns={
            "player": "Player",
            "team": "Team",
            "runs": "Runs",
            "batting_average": "Average",
            "strike_rate": "Strike Rate"
        }),
        use_container_width=True,
        hide_index=True
    )

with right:
    fig = px.bar(
        batting.sort_values("runs"),
        x="runs",
        y="player",
        color="team",
        orientation="h",
        text="runs",
        title="Leading Run Scorers",
        color_discrete_sequence=["#32b8a6", "#e7b75b"]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        height=350,
        legend_title_text="Team"
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------- BOWLING ANALYTICS ----------
st.markdown('<div class="section-heading">🎯 Bowling Analytics</div>',
            unsafe_allow_html=True)

bowling = top_bowlers(filtered)

left, right = st.columns([1, 1.3])

with left:
    st.markdown("**Top Wicket Takers**")

    st.dataframe(
        bowling[
            ["player", "team", "wickets", "economy", "bowling_average"]
        ].rename(columns={
            "player": "Player",
            "team": "Team",
            "wickets": "Wickets",
            "economy": "Economy",
            "bowling_average": "Bowling Average"
        }),
        use_container_width=True,
        hide_index=True
    )

with right:
    if not bowling.empty:
        fig = px.bar(
            bowling.sort_values("wickets"),
            x="wickets",
            y="player",
            color="team",
            orientation="h",
            text="wickets",
            title="Leading Wicket Takers",
            color_discrete_sequence=["#e7b75b", "#32b8a6"]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=50, b=10),
            height=350,
            legend_title_text="Team"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bowling records available for this selection.")


# ---------- PLAYER COMPARISON ----------
st.markdown('<div class="section-heading">⚖️ Player Comparison</div>',
            unsafe_allow_html=True)

player_names = sorted(filtered["player"].unique().tolist())

if len(player_names) >= 2:
    selected_players = st.multiselect(
        "Choose players to compare",
        player_names,
        default=player_names[:2],
        max_selections=4
    )

    if selected_players:
        comparison = compare_players(filtered, selected_players)

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                comparison,
                x="player",
                y="runs",
                color="player",
                title="Batting Comparison",
                text="runs"
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                comparison,
                x="player",
                y="wickets",
                color="player",
                title="Bowling Comparison",
                text="wickets"
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            comparison[
                ["player", "runs", "batting_average",
                 "strike_rate", "wickets", "economy"]
            ].rename(columns={
                "player": "Player",
                "runs": "Runs",
                "batting_average": "Batting Average",
                "strike_rate": "Strike Rate",
                "wickets": "Wickets",
                "economy": "Economy"
            }),
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("At least two players are required for comparison.")


# ---------- FULL DATASET ----------
with st.expander("📋 View Complete Player Statistics"):
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )


# ---------- DOWNLOAD REPORT ----------
st.markdown('<div class="section-heading">📥 Export Report</div>',
            unsafe_allow_html=True)

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Player Analytics CSV",
    data=csv_data,
    file_name="criclytics_player_report.csv",
    mime="text/csv"
)


# ---------- FOOTER ----------
st.divider()

st.markdown("""
<p class="info-text" style="text-align:center;">
    Criclytics · Cricket Performance Analytics<br>
    Built with Python, Pandas, Streamlit and Plotly.
</p>
""", unsafe_allow_html=True)
