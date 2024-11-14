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
import hmac

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


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
