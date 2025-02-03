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

# Player card function
def player_card(player, bg_color, text_color):
    return f"""
    <div style='border:2px solid {text_color}; border-radius:15px; padding:15px; margin:10px; background-color:{bg_color}; color:{text_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.5); font-family: Arial, sans-serif;'>
        <h2 style='margin:0; font-size:24px;'>{player['Name']}</h2>
        <p><strong>Team:</strong> {player['Team']}</p>
        <p><strong>Nationality:</strong> {player['Nation']}</p>
        <p><strong>Age:</strong> {player['Age']}</p>
        <p><strong>Height:</strong> {player['Height']} cm</p>
        <p><strong>Weight:</strong> {player['Weight']} kg</p>
    </div>
    """

# Radar chart function using Plotly
def plot_radar(player1_name, player2_name, selected_stats):
    df, _ = load_data()

    def get_player_stats(name):
        player = df[df['Name'] == name]
        if player.empty:
            raise ValueError(f"Player '{name}' not found in the dataset.")
        return player.iloc[0][selected_stats].values.astype(int), player.iloc[0]

    try:
        values1, player1_info = get_player_stats(player1_name)
        values2, player2_info = get_player_stats(player2_name)
    except ValueError as e:
        st.error(e)
        return

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values1,
        theta=selected_stats,
        fill='toself',
        name=player1_name,
        line=dict(color='#00FFFF', width=4),
        marker=dict(size=10)
    ))

    fig.add_trace(go.Scatterpolar(
        r=values2,
        theta=selected_stats,
        fill='toself',
        name=player2_name,
        line=dict(color='#FF00FF', width=4),
        marker=dict(size=10)
    ))

    fig.update_layout(
        paper_bgcolor='#0D0D0D',
        plot_bgcolor='#0D0D0D',
        polar=dict(
            bgcolor='#1A1A1A',
            radialaxis=dict(
                visible=False,
                showticklabels=False,
                gridcolor='#333',
                gridwidth=1
            ),
            angularaxis=dict(
                tickfont=dict(color='white')
            )
        ),
        showlegend=True,
        font=dict(size=14, color='white')
    )

    # Display player cards and radar chart
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(player_card(player1_info, '#1A1A1A', '#00FFFF'), unsafe_allow_html=True)
    with col2:
        st.markdown(player_card(player2_info, '#1A1A1A', '#FF00FF'), unsafe_allow_html=True)

    st.plotly_chart(fig, use_container_width=True)

# Streamlit app
st.markdown("""
    <style>
    body {
        background-color: #0D0D0D;
        color: white;
        font-family: Arial, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚽ Player Comparison Tool")
st.markdown("""
Compare football players using data from **EA FC 25**. Select two players and specific metrics to analyze their performance side by side with modern visuals.
""")

# Load data
df, stat_columns = load_data()

# Player selection
player_names = df['Name'].unique()
player1 = st.selectbox("Select First Player", player_names)
player2 = st.selectbox("Select Second Player", player_names)

# Metric selection
numerical_columns = df.select_dtypes(include=['number']).columns.tolist()
if 'Age' in numerical_columns:
    numerical_columns.remove('Age')
selected_stats = st.multiselect("Select Metrics to Compare (up to 6)", numerical_columns, default=numerical_columns[:6])

# Button to generate radar chart
if st.button("Compare Players") and len(selected_stats) == 6:
    plot_radar(player1, player2, selected_stats)
else:
    if len(selected_stats) != 6:
        st.warning("Please select exactly 6 metrics for comparison.")
