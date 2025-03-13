from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import plotly.express as px

DATABASE_URL = "mssql+pyodbc://@DESKTOP-9UVAEME\\SQLEXPRESS/FootballData?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)

@st.cache_data
def get_standings():
    query = """ 
    SELECT Standings.position, Teams.name, Standings.points, Standings.playedGames, 
           Standings.won, Standings.lost, Standings.draw, Standings.goalsFor, 
           Standings.goalsAgainst, Standings.goalDifference
    FROM Standings
    INNER JOIN Teams ON Standings.team_id = Teams.id
    """
    df = pd.read_sql(query, engine)
    return df.set_index("position")

st.set_page_config(page_title="Bundesliga Dashboard", layout="wide")
st.title("⚽ Bundesliga Dashboard")

st.subheader("📊 League Standings")
standings_df = get_standings()
st.dataframe(standings_df, height=340)
