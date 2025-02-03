import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv('male_players.csv')
    stat_columns = df.select_dtypes(include=['number']).columns.tolist()
    df = df[df[stat_columns].sum(axis=1) != 0]
    return df, stat_columns

# Grouping football metrics
def group_football_metrics():
    return {
        "Attacking": ['Positioning', 'Finishing', 'ShotPower', 'LongShots', 'Volleys', 'Penalties'],
        "Passing": ['Vision', 'Crossing', 'FKAccuracy', 'ShortPassing', 'LongPassing', 'Curve'],
        "Dribbling": ['Dribbling', 'Agility', 'Balance', 'Reactions', 'BallControl', 'Composure'],
        "Defending": ['Interceptions', 'HeadingAccuracy', 'DefensiveAwareness', 'StandingTackle', 'SlidingTackle', 'Aggression'],
        "Physical": ['Jumping', 'Stamina', 'Strength', 'Acceleration', 'SprintSpeed', 'Aggression'],
        "Goalkeeping": ['GKDiving', 'GKHandling', 'GKKicking', 'GKPositioning', 'GKReflexes', 'GKComposure']
    }

# Player Card Function
def player_card(player, bg_color, text_color):
    return f"""
    <div style='border: 3px solid {text_color}; border-radius: 20px; padding: 20px; margin: 15px; background-color: {bg_color}; color: {text_color}; box-shadow: 0 6px 20px rgba(0,0,0,0.7); font-family: "Roboto", sans-serif;'>
        <h2 style='margin: 0 0 15px 0; font-size: 28px; text-align: center;'>{player['Name']}</h2>
        <p><strong>Team:</strong> {player['Team']}</p>
        <p><strong>Nationality:</strong> {player['Nation']}</p>
        <p><strong>Age:</strong> {player['Age']}</p>
        <p><strong>Position:</strong> {player.get('Position', 'N/A')}</p>
        <p><strong>Height:</strong> {player.get('Height', 'N/A')} cm</p>
        <p><strong>Weight:</strong> {player.get('Weight', 'N/A')} kg</p>
    </div>
    """

# Radar Chart Function
def plot_player_comparison(player1_name, player2_name):
    df, _ = load_data()
    metric_groups = group_football_metrics()

    def get_player_stats(name):
        player = df[df['Name'] == name]
        if player.empty:
            raise ValueError(f"Player '{name}' not found in the dataset.")
        return player.iloc[0]

    try:
        player1_info = get_player_stats(player1_name)
        player2_info = get_player_stats(player2_name)
    except ValueError as e:
        st.error(e)
        return

    # Display Player Cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(player_card(player1_info, '#1A1A1A', '#00FFFF'), unsafe_allow_html=True)
    with col2:
        st.markdown(player_card(player2_info, '#1A1A1A', '#FF00FF'), unsafe_allow_html=True)

    # Create a radar chart for each metric group
    for group_name, metrics in metric_groups.items():
        # Find available metrics for this group
        available_metrics = [metric for metric in metrics if metric in df.columns]

        # Ensure each group has 6 metrics
        if len(available_metrics) < 6:
            available_metrics += [m for m in metrics if m not in available_metrics][:6 - len(available_metrics)]

        # Extract values for both players
        values1 = [player1_info.get(metric, 0) for metric in available_metrics]
        values2 = [player2_info.get(metric, 0) for metric in available_metrics]

        # Create the radar chart
        fig = go.Figure()

        # Add trace for player 1
        fig.add_trace(go.Scatterpolar(
            r=values1,
            theta=available_metrics,
            fill='toself',
            name=player1_name,
            line=dict(color='#00FFFF', width=2)
        ))

        # Add trace for player 2
        fig.add_trace(go.Scatterpolar(
            r=values2,
            theta=available_metrics,
            fill='toself',
            name=player2_name,
            line=dict(color='#FF00FF', width=2)
        ))

        # Update layout
        fig.update_layout(
            polar=dict(
                bgcolor='#1A1A1A',
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                ),
                angularaxis_tickfont_color='white'
            ),
            showlegend=True,
            paper_bgcolor='#0D0D0D',
            plot_bgcolor='#0D0D0D',
            font=dict(color='white'),
            title=f"{group_name} Comparison"
        )

        # Display the radar chart
        st.plotly_chart(fig, use_container_width=True)

# Streamlit App Configuration
st.set_page_config(page_title="Ultimate Player Comparison", page_icon="⚽", layout="wide")

st.title("⚽ Ultimate Player Comparison Tool")
st.markdown("""
Compare football players using comprehensive metrics from **EA FC 25**. Explore players' skills across Attacking, Passing, Dribbling, Defending, Physical, and Goalkeeping attributes.
""")

# Load data
df, _ = load_data()

# Player selection
player_names = sorted(df['Name'].unique())
player1 = st.selectbox("Select First Player", player_names)
player2 = st.selectbox("Select Second Player (Different from First)", [name for name in player_names if name != player1])

# Compare button
if st.button("Compare Players"):
    plot_player_comparison(player1, player2)
else:
    st.info("Select two different players and click 'Compare Players' to generate comprehensive analysis.")
