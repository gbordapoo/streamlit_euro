"""
Make sure you have the following installed:
- streamlit
- mplsoccer
- pandas
"""
import json
import numpy as np
import pandas as pd
import streamlit as st
from mplsoccer import VerticalPitch

# Title and subtitle
st.title("Euros 2024 Shot Map")
st.subheader("Filter to any team/player to see all their shots taken!")

# Load data
df = pd.read_csv('euros_2024_shot_map.csv')
df = df[df['type'] == 'Shot'].reset_index(drop=True)
df['location'] = df['location'].apply(json.loads)

# Define a function to filter data
def filter_data(df: pd.DataFrame, team: str, player: str):
    if team and team != "Select":
        df = df[df['team'] == team]
    if player and player != "Select":
        df = df[df['player'] == player]
    return df

# Define a function to plot shots
def plot_shots(df, ax, pitch):
    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x=float(x['location'][0]),
            y=float(x['location'][1]),
            ax=ax,
            s=1000 * x['shot_statsbomb_xg'],
            color='green' if x['shot_outcome'] == 'Goal' else 'white',
            edgecolors='black',
            alpha=1 if x['shot_outcome'] == 'Goal' else .5,
            zorder=2 if x['shot_outcome'] == 'Goal' else 1
        )

# Set up team selection
teams = df['team'].dropna().sort_values().unique()
teams = np.insert(teams, 0, "Select")  # Add "Select" as the first option
team = st.selectbox("Select a team", teams)

# Set up player selection based on the chosen team
if team != "Select":
    players = df[df['team'] == team]['player'].dropna().sort_values().unique()
    players = np.insert(players, 0, "Select")  # Add "Select" as the first option
    player = st.selectbox("Select a player", players)
else:
    player = "Select"  # Default to "Select" if no team is chosen

# Filter the dataframe based on team and player selections
filtered_df = filter_data(df, team, player)

# Set up the pitch and plot shots
pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f0f0f0', line_color='black', half=True)
fig, ax = pitch.draw(figsize=(10, 10))
plot_shots(filtered_df, ax, pitch)

# Display the plot in Streamlit
st.pyplot(fig)
