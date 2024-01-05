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

    # Create scoreboard component
    datatable = dash_table.DataTable(
        data=df_scoreboard.to_dict('records'),
        columns=[
            {'name': 'timestamp', 'id': 'timestamp'},
            {'name': 'username', 'id': 'username'},
            {'name': 'score', 'id': 'score'},
        ],
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

    # Global scoreboard
    dbc.Container(fluid=True, children=[

        # Select difficulty
        dbc.Tabs([

            # Normal difficulty
            dbc.Tab([

                # Select operator
                dbc.Tabs([
                    
                    # Addition scoreboard
                    dbc.Tab([
                        create_scoreboard('Normal', 'Addition'),
                    ], label='Addition', id='scoreboard_addition'),

                    # Subtraction scoreboard
                    dbc.Tab([
                        create_scoreboard('Normal', 'Subtraction'),
                    ], label='Subtraction', id='scoreboard_subtraction'),

                    # Multiplication scoreboard
                    dbc.Tab([
                        create_scoreboard('Normal', 'Multiplication'),
                    ], label='Multiplication', id='scoreboard_multiplication'),

                    # Division scoreboard
                    dbc.Tab([
                        create_scoreboard('Normal', 'Division'),
                    ], label='Division', id='scoreboard_division'),

                ])

            ], label='Normal'),

            # Hard difficulty
            dbc.Tab([
                create_scoreboard('Hard', 'Invalid'),
            ], label='Hard', id='scoreboard_hard'),

        ])

    ]),

    # Global statistics
    dbc.Container(fluid=True, children=[

        # Select difficulty
        dbc.Tabs([

            # Normal difficulty
            dbc.Tab([

                # Select operator
                dbc.Tabs([
                    
                    # Addition statistics
                    dbc.Tab([
                        create_statistic('Normal', 'Addition'),
                    ], label='Addition', id='statistics_addition'),

                    # Subtraction statistics
                    dbc.Tab([
                        create_statistic('Normal', 'Subtraction'),
                    ], label='Subtraction', id='statistics_subtraction'),

                    # Multiplication statistics
                    dbc.Tab([
                        create_statistic('Normal', 'Multiplication'),
                    ], label='Multiplication', id='statistics_multiplication'),

                    # Division statistics
                    dbc.Tab([
                        create_statistic('Normal', 'Division'),
                    ], label='Division', id='statistics_division'),

                ])

            ], label='Normal'),

            # Hard difficulty
            dbc.Tab([
                create_statistic('Hard', 'Invalid'),
            ], label='Hard', id='statistics_hard'),

        ])

    ]),

])

# Callback functions
@callback(
    Output('scoreboard_addition', 'children'),
    Output('scoreboard_subtraction', 'children'),
    Output('scoreboard_multiplication', 'children'),
    Output('scoreboard_division', 'children'),
    Output('scoreboard_hard', 'children'),

    Output('statistics_addition', 'children'),
    Output('statistics_subtraction', 'children'),
    Output('statistics_multiplication', 'children'),
    Output('statistics_division', 'children'),
    Output('statistics_hard', 'children'),

    Input('interval_scoreboard_statistic', 'n_intervals'),

    prevent_initial_call=True,
)
def handle_update_data(n_interval: int) -> list[dash_table.DataTable]:
    """
    Updates scoreboard and statistics every 5 minutes.
    """
    return [
        create_scoreboard('Normal', 'Addition'),
        create_scoreboard('Normal', 'Subtraction'),
        create_scoreboard('Normal', 'Multiplication'),
        create_scoreboard('Normal', 'Division'),
        create_scoreboard('Hard', 'Invalid'),
        create_statistic('Normal', 'Addition'),
        create_statistic('Normal', 'Subtraction'),
        create_statistic('Normal', 'Multiplication'),
        create_statistic('Normal', 'Division'),
        create_statistic('Hard', 'Invalid'),
    ]
