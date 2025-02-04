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
        "Defending": ['Interceptions', 'HeadingAccuracy', 'DefAwareness', 'StandingTackle', 'SlidingTackle', 'Aggression'],
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

def summary_card(content):
    """
    Creates a styled card for the summary with a unique color scheme
    """
    return f"""
    <div style='
        background: linear-gradient(135deg, #2C3E50 0%, #3498DB 100%);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        color: white;
        font-family: "Roboto", sans-serif;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    '>
        <h2 style='
            color: #ECF0F1;
            font-size: 24px;
            margin-bottom: 20px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
        '>Analysis Summary</h2>
        <div style='
            line-height: 1.6;
            font-size: 16px;
        '>
            {content}
        </div>
    </div>
    """

def generate_comparison_summary(player1_info, player2_info, metric_groups):
    """
    Generates a simplified, readable summary comparing two players.
    """
    summary_parts = []
    
    # Compare each group and collect significant differences
    key_differences = []
    for group_name, metrics in metric_groups.items():
        valid_metrics = [m for m in metrics if m in player1_info.index and m in player2_info.index]
        if not valid_metrics:
            continue
            
        p1_scores = [player1_info[m] for m in valid_metrics]
        p2_scores = [player2_info[m] for m in valid_metrics]
        p1_avg = sum(p1_scores) / len(p1_scores)
        p2_avg = sum(p2_scores) / len(p2_scores)
        diff = p1_avg - p2_avg
        
        if abs(diff) > 10:  # Only show major differences
            better_player = player1_info['Name'] if diff > 0 else player2_info['Name']
            key_differences.append(f"<strong>{better_player}</strong> is stronger in {group_name.lower()} ({abs(diff):.0f} point difference)")

    # Create main comparison text
    summary_parts.append(f"Comparing <strong>{player1_info['Name']}</strong> and <strong>{player2_info['Name']}</strong>:<br><br>")
    
    if key_differences:
        summary_parts.append("<strong>Key Strengths:</strong><br>")
        summary_parts.append(", ".join(key_differences) + ".<br><br>")
    
    # Add play style summary
    summary_parts.append("<strong>Play Style Analysis:</strong><br>")
    summary_parts.append(f"• <strong>{player1_info['Name']}</strong>: {generate_play_style_suggestion(player1_info, metric_groups)}<br>")
    summary_parts.append(f"• <strong>{player2_info['Name']}</strong>: {generate_play_style_suggestion(player2_info, metric_groups)}")

    return summary_card("\n".join(summary_parts))

def generate_play_style_suggestion(player_info, metric_groups):
    """
    Generates play style suggestions based on player's strongest attributes.
    """
    group_averages = {}
    for group_name, metrics in metric_groups.items():
        valid_metrics = [m for m in metrics if m in player_info.index]
        if valid_metrics:
            group_averages[group_name] = sum(player_info[m] for m in valid_metrics) / len(valid_metrics)
    
    # Find top 2 strongest areas
    top_groups = sorted(group_averages.items(), key=lambda x: x[1], reverse=True)[:2]
    
    # Generate suggestion based on top attributes
    if 'Attacking' in [g[0] for g in top_groups] and 'Dribbling' in [g[0] for g in top_groups]:
        return "Best suited for an advanced attacking role, focusing on taking on defenders and creating chances"
    elif 'Passing' in [g[0] for g in top_groups] and 'Vision' in player_info.index and player_info['Vision'] > 80:
        return "Could excel in a playmaker role, dictating the tempo and creating opportunities"
    elif 'Defending' in [g[0] for g in top_groups] and 'Physical' in [g[0] for g in top_groups]:
        return "Well-suited for a defensive role, with good physical presence and defensive capabilities"
    elif 'Goalkeeping' in [g[0] for g in top_groups]:
        return "Specialized goalkeeper with strong fundamental skills"
    else:
        return f"Shows particular strength in {top_groups[0][0].lower()} and {top_groups[1][0].lower()}"

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

    # Create radar charts
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
    
    # Generate and display written summary after radar charts
    st.markdown(generate_comparison_summary(player1_info, player2_info, metric_groups), unsafe_allow_html=True)

def main():
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

if __name__ == "__main__":
    main()
