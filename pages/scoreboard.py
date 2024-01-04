import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container(fluid=True, children=[
    dbc.Label('2'),
])
