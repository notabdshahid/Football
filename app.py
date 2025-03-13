import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import pyodbc
import streamlit as st
import plotly.express as px

# Connect to the SQL Server database
def get_data():
    conn = pyodbc.connect(
    "DRIVER={SQL Server};SERVER=DESKTOP-9UVAEME\SQLEXPRESS;DATABASE=FootballData;Trusted_Connection=yes;"
    
)
    return conn
    

@st.cache_data
def get_standings():
    conn = get_data()
    query = """ SELECT Standings.position,  Teams.name, Standings.points , Standings.playedGames, 
           Standings.won, Standings.lost, Standings.draw, Standings.goalsFor, 
           Standings.goalsAgainst, Standings.goalDifference
    FROM Standings
    INNER JOIN Teams ON Standings.team_id = Teams.id"""
    df = pd.read_sql(query, conn, index_col="position")
    conn.close()
    return df

@st.cache_data
def get_top_scoring_team():
    query = """
    SELECT TOP 1 t.name AS team_name, SUM(s.goalsFor) AS total_goals
    FROM Standings s
    JOIN Teams t ON s.team_id = t.id
    WHERE s.season_id = 2308
    GROUP BY t.name
    ORDER BY total_goals DESC;
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

@st.cache_data
def get_top_defensive_team():
    query = """
    SELECT TOP 1 t.name AS team_name, SUM(s.goalsAgainst) AS goals_conceded
    FROM Standings s
    JOIN Teams t ON s.team_id = t.id
    WHERE s.season_id = 2308
    GROUP BY t.name
    ORDER BY goals_conceded ASC;
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else None

@st.cache_data
def get_total_games():
    query = """
    SELECT COUNT(*) AS total_games
    FROM Matches
    WHERE season_id = 2308 AND status = 'FINISHED';
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df["total_games"].values[0] if not df.empty else 0

@st.cache_data
def get_home_win_percentage():
    query = """
    SELECT 
    (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM Matches WHERE season_id = 2308 AND status = 'FINISHED') AS home_win_percentage
    FROM Matches
    WHERE season_id = 2308 AND status = 'FINISHED' AND winner = 'HOME_TEAM';
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df["home_win_percentage"].values[0] if not df.empty else 0

@st.cache_data
def get_away_win_percentage():
    query = """
    SELECT 
    (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM Matches WHERE season_id = 2308 AND status = 'FINISHED') AS away_win_percentage
    FROM Matches
    WHERE season_id = 2308 AND status = 'FINISHED' AND winner = 'AWAY_TEAM';
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df["away_win_percentage"].values[0] if not df.empty else 0

@st.cache_data
def get_draw_percentage():
    query = """
    SELECT 
    (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM Matches WHERE season_id = 2308 AND status = 'FINISHED') AS draw_percentage
    FROM Matches
    WHERE season_id = 2308 AND status = 'FINISHED' AND winner = 'DRAW';
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df["draw_percentage"].values[0] if not df.empty else 0

@st.cache_data
def get_avg_goals_per_match():
    query = """
    SELECT 
    AVG(score_home + score_away) AS avg_goals_per_match
    FROM Matches
    WHERE season_id = 2308 AND status = 'FINISHED';
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df["avg_goals_per_match"].values[0] if not df.empty else 0

@st.cache_data
def get_total_goals():
    query = """
    SELECT 
    sum(score_home + score_away) AS avg_goals_per_match
    FROM Matches
    WHERE season_id = 2308
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df["avg_goals_per_match"].values[0] if not df.empty else 0

@st.cache_data
def get_top_scorer():
    query = """
    SELECT top 3
    p.name AS player_name, 
    s.goals
    FROM Scorers s
    JOIN Players p ON s.player_id = p.id
    WHERE s.season_id = 2308
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@st.cache_data
def get_cumulative_points():
    query = """
    WITH MatchPoints AS (
        SELECT 
            m.matchday,
            t.id AS team_id,
            t.name AS team_name,
            CASE 
                WHEN m.winner = 'HOME_TEAM' AND m.home_team_id = t.id THEN 3
                WHEN m.winner = 'AWAY_TEAM' AND m.away_team_id = t.id THEN 3
                WHEN m.winner = 'DRAW' THEN 1
                ELSE 0
            END AS points
        FROM Matches m
        JOIN Teams t ON t.id = m.home_team_id OR t.id = m.away_team_id
        WHERE m.status = 'FINISHED'
    )
    SELECT 
        mp1.matchday,
        mp1.team_name,
        SUM(mp2.points) AS cumulative_points
    FROM MatchPoints mp1
    JOIN MatchPoints mp2 
        ON mp1.team_id = mp2.team_id 
        AND mp1.matchday >= mp2.matchday  
    GROUP BY mp1.matchday, mp1.team_name, mp1.team_id
    ORDER BY mp1.matchday, cumulative_points DESC;
    """
    conn = get_data()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Bundesliga Dashboard", layout="wide")
st.title("⚽ Bundesliga Dashboard")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📊 League Standings")
    standings_df = get_standings()
    st.dataframe(standings_df, height=340)

total_games = get_total_games()
home_win_pct = f"{get_home_win_percentage():.2f}"
away_win_pct = f"{get_away_win_percentage():.2f}"
draw_pct = f"{get_draw_percentage():.2f}"
avg_goals_per_match = f"{get_total_goals()/get_total_games():.2f}"
total_goals = get_total_goals()
top_scoring_team = get_top_scoring_team()["team_name"]
best_defensive_team = get_top_defensive_team()["team_name"]
with col2:
    st.subheader("📈 Key Metrics")
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric(label="⚽ Total Games Played", value=total_games)
        st.metric(label="🏠 Home Win %", value=f"{home_win_pct}%")
        st.metric(label="🛫 Away Win %", value=f"{away_win_pct}%")
        st.metric(label="🔄 Draw %", value=f"{draw_pct}%")
    with metric_col2:
        st.metric(label="⚽ Avg. Goals Per Match", value=avg_goals_per_match)
        top_team = get_top_scoring_team()
        if top_scoring_team is not None:
            st.metric(label="🔥 Top Scoring Team", value=top_scoring_team)

        best_defense = get_top_defensive_team()
        if best_defensive_team is not None:
            st.metric(label="🛡️ Best Defense", value=best_defensive_team)

df_top_scorer = get_top_scorer()
if df_top_scorer is not None:
    fig = px.bar(
    df_top_scorer, 
    x="player_name", 
    y="goals", 
    text="goals", 
    title="⚽ Torjägerkanone  Race",
    labels={"player_name": "Player", "goals": "Goals"},
    color="goals",  
    color_continuous_scale="reds",
)
fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis=dict(title="Player"),
    yaxis=dict(title="Goals"),
    showlegend=False
)

col1, col2 = st.columns([3, 7])  
with col1:
    st.plotly_chart(fig,use_container_width=True)

df_cumulative = get_cumulative_points()
latest_matchday = df_cumulative["matchday"].max()
latest_standings = df_cumulative[df_cumulative["matchday"] == latest_matchday]
top_teams = latest_standings.nlargest(4, "cumulative_points")["team_name"].tolist()


with col2:
    selected_teams = st.multiselect(
    "Select teams to display", options=df_cumulative["team_name"].unique(), default=top_teams
)
df_filtered = df_cumulative[df_cumulative["team_name"].isin(selected_teams)]
team_order = latest_standings.sort_values("cumulative_points", ascending=False)["team_name"].tolist()
df_filtered["team_name"] = pd.Categorical(df_filtered["team_name"], categories=team_order, ordered=True)
fig = px.line(
    df_filtered, 
    x="matchday", 
    y="cumulative_points", 
    color="team_name", 
    markers=True,
    title="🏆 Bundesliga Meisterschale Race",
    labels={"matchday": "Matchday", "cumulative_points": "Points", "team_name": "Team"},
    category_orders={"team_name": team_order},
    custom_data=["team_name"]
)

fig.update_traces(
    line=dict(width=3),
    marker=dict(size=8, symbol="circle"),
    hovertemplate="<b>%{customdata[0]}</b><br>Matchday: %{x}<br>Points: %{y}"
)

fig.update_layout(
    xaxis=dict(tickmode="linear", dtick=1, rangeslider=dict(visible=True), type="linear"),
    yaxis=dict(title="Points", range=[0, df_cumulative["cumulative_points"].max() + 5]),
    colorway=px.colors.qualitative.Bold,
    hovermode="x unified"
)
with col2:
    st.plotly_chart(fig, use_container_width=True)


