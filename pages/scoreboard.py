# Import libraries
import dash
from dash import dcc, callback, Output, Input, State, dash_table
import dash_bootstrap_components as dbc

import plotly.express as px

from s3_client import get_scoreboard_from_s3

dash.register_page(__name__)

# Helper functions
def create_scoreboard(difficulty: str, operator: str) -> dash_table.DataTable:
    """
    Generates a scoreboard in the form of a Dash DataTable depending on the selected
    difficulty and operator. Scoreboard is sorted by descending score and limited to 10 scores.
    """
    # Retrieve scores from s3
    df_scoreboard = get_scoreboard_from_s3()

    # Filter df
    df_scoreboard = df_scoreboard[df_scoreboard['difficulty'] == difficulty]
    df_scoreboard = df_scoreboard[df_scoreboard['operator'] == operator]

    # Sort df
    df_scoreboard = df_scoreboard.sort_values(by=['score'], ascending=False)

    # Limit df
    df_scoreboard = df_scoreboard.head(10)

    # Add rank
    df_scoreboard['rank'] = [i for i in range(1, len(df_scoreboard)+1)]

    # Rename columns
    df_scoreboard = df_scoreboard.rename(
        columns={
            'rank': 'Rank',
            'timestamp': 'Date',
            'username': 'Username',
            'score': 'Score',
        }
    )

    # Create scoreboard component
    datatable = dash_table.DataTable(
        data=df_scoreboard.to_dict('records'),
        columns=[
            {'name': 'Rank', 'id': 'Rank'},
            {'name': 'Date', 'id': 'Date'},
            {'name': 'Username', 'id': 'Username'},
            {'name': 'Score', 'id': 'Score'},
        ],
        style_header={
            'borderLeft': '0px',
            'borderRight': '0px',
            # 'backgroundColor': '#ffffff',
            'font-family':'sans-serif',
            'font-weight': 'bold',
            'font-size': '250%',
            'color': '#595959',
            'height': '80px',
            'textAlign': 'center',
        },
        style_data={
            'borderLeft': '0px',
            'borderRight': '0px',
        },
        style_cell={
            'font-family':'sans-serif',
            'font-weight': 'bold',
            'font-size': '150%',
            'color': '#595959',
            'height': '55px',
            'textAlign': 'center',
        },
    )
    
    return datatable

def create_statistic(difficulty: str, operator: str) -> dcc.Graph:
    """
    Generates a histogram of scores of all users using plotly based on the selected
    difficulty and operator.
    """
    # Retrieve scores from s3
    df_scoreboard = get_scoreboard_from_s3()

    # Filter df
    df_scoreboard = df_scoreboard[df_scoreboard['difficulty'] == difficulty]
    df_scoreboard = df_scoreboard[df_scoreboard['operator'] == operator]

    # Create figure
    fig = px.histogram(df_scoreboard, 'score', nbins=len(df_scoreboard))

    return dcc.Graph(figure=fig)

# Page layout
layout = dbc.Container(fluid=True, children=[

    # Interval to update data every 5 mins
    dcc.Interval(
        id='interval_scoreboard_statistic',
        interval=1000*60*5,
        n_intervals=0,
    ),

    # Global scoreboard and statistics
    dbc.Col(
        dbc.Container(fluid=True, class_name='scoreboardcard', children=[

            # Select difficulty
            dbc.Tabs([

                # Normal difficulty
                dbc.Tab([

                    # Select operator
                    dbc.Tabs([
                        
                        # Addition scoreboard and statistics
                        dbc.Tab([
                            create_scoreboard('Normal', 'Addition'),
                            create_statistic('Normal', 'Addition'),
                        ], label='Addition', id='score_stats_addition'),

                        # Subtraction scoreboard and statistics
                        dbc.Tab([
                            create_scoreboard('Normal', 'Subtraction'),
                            create_statistic('Normal', 'Subtraction'),
                        ], label='Subtraction', id='score_stats_subtraction'),

                        # Multiplication scoreboard and statistics
                        dbc.Tab([
                            create_scoreboard('Normal', 'Multiplication'),
                            create_statistic('Normal', 'Multiplication'),
                        ], label='Multiplication', id='score_stats_multiplication'),

                        # Division scoreboard and statistics
                        dbc.Tab([
                            create_scoreboard('Normal', 'Division'),
                            create_statistic('Normal', 'Division'),
                        ], label='Division', id='score_stats_division'),

                    ])

                ], label='Normal'),

                # Hard difficulty
                dbc.Tab([
                    create_scoreboard('Hard', 'Invalid'),
                    create_statistic('Hard', 'Invalid'),
                ], label='Hard', id='score_stats_hard'),

            ])

        ]),
    ),

])

# Callback functions
@callback(
    Output('score_stats_addition', 'children'),
    Output('score_stats_subtraction', 'children'),
    Output('score_stats_multiplication', 'children'),
    Output('score_stats_division', 'children'),
    Output('score_stats_hard', 'children'),

    Input('interval_scoreboard_statistic', 'n_intervals'),

    prevent_initial_call=True,
)
def handle_update_data(n_interval: int) -> list[dash_table.DataTable]:
    """
    Updates scoreboard and statistics every 5 minutes.
    """
    return [
        [create_scoreboard('Normal', 'Addition'), create_statistic('Normal', 'Addition')],
        [create_scoreboard('Normal', 'Subtraction'), create_statistic('Normal', 'Subtraction')],
        [create_scoreboard('Normal', 'Multiplication'), create_statistic('Normal', 'Multiplication')],
        [create_scoreboard('Normal', 'Division'), create_statistic('Normal', 'Division')],
        [create_scoreboard('Hard', 'Invalid'), create_statistic('Hard', 'Invalid'),],
    ]
