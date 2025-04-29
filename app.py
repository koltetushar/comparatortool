import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(
    page_title="Football Player Analysis System",
    page_icon="⚽",
    layout="wide"
)

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
        "Defending": ['Interceptions', 'HeadingAccuracy', 'DefAwareness', 'StandingTackle', 'SlidingTackle', 'Aggression'],
        "Physical": ['Jumping', 'Stamina', 'Strength', 'Acceleration', 'SprintSpeed', 'Aggression'],
        "Goalkeeping": ['GKDiving', 'GKHandling', 'GKKicking', 'GKPositioning', 'GKReflexes', 'GKComposure']
    }

# Player Card Function
def player_card(player, bg_color, text_color):
    return f"""
    <div style='border: 3px solid {text_color}; border-radius: 20px; padding: 20px; margin: 15px; background-color: {bg_color}; color: {text_color}; box-shadow: 0 6px 20px rgba(0,0,0,0.7); font-family: \"Roboto\", sans-serif;'>
        <h2 style='margin: 0 0 15px 0; font-size: 28px; text-align: center;'>{player['Name']}</h2>
        <p><strong>Team:</strong> {player['Team']}</p>
        <p><strong>Nationality:</strong> {player['Nation']}</p>
        <p><strong>Age:</strong> {player['Age']}</p>
        <p><strong>Position:</strong> {player.get('Position', 'N/A')}</p>
        <p><strong>Height:</strong> {player.get('Height', 'N/A')} cm</p>
        <p><strong>Weight:</strong> {player.get('Weight', 'N/A')} kg</p>
    </div>
    """

# Prediction tab functionality
def predict_best_positions(df):
    st.subheader("🔍 Predict Best Position for a Player")
    player_names = df["Name"].unique()
    selected_player = st.selectbox("Select Player for Position Prediction", player_names)

    valid_positions = ['GK', 'LB', 'CB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST']
    features = ['PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY', 'Agility', 'Reactions', 'BallControl', 'Vision']

    df_clean = df[df['Position'].isin(valid_positions)].dropna(subset=features)
    X = df_clean[features]
    y = df_clean['Position']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, stratify=y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    player_row = df[df["Name"] == selected_player]
    if not player_row.empty:
        player_features = scaler.transform(player_row[features])
        probs = model.predict_proba(player_features)[0]
        class_probs = list(zip(model.classes_, probs))
        top3 = sorted(class_probs, key=lambda x: x[1], reverse=True)[:3]

        st.markdown(f"### Top 3 Positions for **{selected_player}**")
        for i, (pos, p) in enumerate(top3, 1):
            st.write(f"{i}. **{pos}** — Confidence: {p:.1%}")

        show_pitch_visual(top3, selected_player)

# Pitch visual for prediction
def show_pitch_visual(predicted_positions, player_name):
    import plotly.graph_objects as go
    from PIL import Image
    import base64
    from io import BytesIO

    # Position coordinates on the pitch for a 4-3-3 formation with two CBs
    # Adjusted to ensure visibility
    POS_COORDS = {
        'GK': (50, 10),
        'LB': (20, 25), 
        'CB': (35, 25),
        'CB2': (65, 25),
        'RB': (80, 25),
        'CDM': (50, 40),
        'CM': (35, 50),
        'CAM': (65, 50),
        'LW': (20, 70),
        'ST': (50, 70),
        'RW': (80, 70)
    }

    # Load the pitch image
    pitch_img = Image.open("pitch.png")
    buffer = BytesIO()
    pitch_img.save(buffer, format="PNG")
    encoded_img = base64.b64encode(buffer.getvalue()).decode()

    fig = go.Figure()

    # Add background image with stretch to accommodate all positions
    fig.add_layout_image(
        dict(
            source=f"data:image/png;base64,{encoded_img}",
            xref="paper", yref="paper",  # Changed to paper coordinates
            x=0, y=1,
            sizex=1, sizey=1,  # Stretch to fit all the coordinates
            sizing="stretch",  # Changed to stretch
            layer="below"
        )
    )

    # Create a wider coordinate system that includes all players
    x_range = [-10, 110]  # Extended beyond 0-100 to include players
    y_range = [-5, 105]   # Extended beyond 0-100 to include players

    # For handling the second CB position in predictions
    def get_position_prob(pos):
        if pos == 'CB2':
            # If second CB, check for CB in predictions
            prob = next((p for p in predicted_positions if p[0] == 'CB'), None)
        else:
            prob = next((p for p in predicted_positions if p[0] == pos), None)
        return prob

    # Draw all positions on the pitch
    for pos, (x, y) in POS_COORDS.items():
        prob = get_position_prob(pos)
        
        if prob:
            conf = prob[1]
            shade = int(255 * conf)
            color = f'rgba(0,{shade},0,0.9)'
        else:
            color = 'rgba(255,0,0,0.6)'
        
        # Display "CB" for both center back positions
        display_text = "CB" if pos == "CB2" else pos
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(size=25, color=color, line=dict(color='white', width=2)),
            text=display_text, textposition='middle center',
            textfont=dict(size=12, color='white'),
            showlegend=False
        ))

    # Set up the layout with fixed dimensions
    fig.update_layout(
        width=600,  # Wider
        height=800,  # Taller
        xaxis=dict(
            visible=False, 
            range=x_range,
            fixedrange=True  # Prevent zooming/panning
        ),
        yaxis=dict(
            visible=False, 
            range=y_range,
            scaleanchor="x", 
            scaleratio=1,
            fixedrange=True  # Prevent zooming/panning
        ),
        title=dict(text=f"⚽ Best Positions for {player_name}", x=0.5, font=dict(color='white')),
        paper_bgcolor='black',
        plot_bgcolor='black',
        margin=dict(l=0, r=0, t=40, b=0),  # Minimal margins
        autosize=False
    )

    # Use full page width to ensure all content is visible
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
# Main player comparison UI
def main():
    st.title("⚽ Ultimate Player Comparison Tool")
    st.markdown("""
    Compare football players using comprehensive metrics from **EA FC 25**. Explore players' skills across Attacking, Passing, Dribbling, Defending, Physical, and Goalkeeping attributes.
    """)

    df, _ = load_data()
    player_names = sorted(df['Name'].unique())
    player1 = st.selectbox("Select First Player", player_names)
    player2 = st.selectbox("Select Second Player (Different from First)", [name for name in player_names if name != player1])

    if st.button("Compare Players"):
        plot_player_comparison(player1, player2)
    else:
        st.info("Select two different players and click 'Compare Players' to generate comprehensive analysis.")

# Comparison logic
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(player_card(player1_info, '#1A1A1A', '#00FFFF'), unsafe_allow_html=True)
    with col2:
        st.markdown(player_card(player2_info, '#1A1A1A', '#FF00FF'), unsafe_allow_html=True)

    for group_name, metrics in metric_groups.items():
        available_metrics = [metric for metric in metrics if metric in df.columns]
        if len(available_metrics) < 6:
            available_metrics += [m for m in metrics if m not in available_metrics][:6 - len(available_metrics)]

        values1 = [player1_info.get(metric, 0) for metric in available_metrics]
        values2 = [player2_info.get(metric, 0) for metric in available_metrics]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values1, theta=available_metrics, fill='toself', name=player1_name, line=dict(color='#00FFFF', width=2)))
        fig.add_trace(go.Scatterpolar(r=values2, theta=available_metrics, fill='toself', name=player2_name, line=dict(color='#FF00FF', width=2)))

        fig.update_layout(
            polar=dict(bgcolor='#1A1A1A', radialaxis=dict(visible=True, range=[0, 100]), angularaxis_tickfont_color='white'),
            showlegend=True,
            paper_bgcolor='#0D0D0D',
            plot_bgcolor='#0D0D0D',
            font=dict(color='white'),
            title=f"{group_name} Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)

# Streamlit Tabs
if __name__ == '__main__':
    df, _ = load_data()
    tab1, tab2 = st.tabs(["Player Comparison", "Position Prediction"])
    with tab1:
        main()
    with tab2:
        predict_best_positions(df)
