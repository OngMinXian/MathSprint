# Import libraries
from dash import dash, Dash, callback, Output, Input, State
import dash_bootstrap_components as dbc

# App config
theme = dbc.themes.BOOTSTRAP
icon_lib = dbc.icons.FONT_AWESOME
bs_icon_lib = dbc.icons.BOOTSTRAP

app = Dash(
    name=__name__,
    external_stylesheets=[theme, icon_lib, bs_icon_lib],
    use_pages=True,
    suppress_callback_exceptions=True,
)

# App layout
app.layout = dbc.Container(fluid=True, children=[

    # Username prompt
    dbc.Row([
        dbc.Label('Welcome to MathSprint!'),
        dbc.Input(
            id='input_username',
            placeholder='Enter your username',
        ),
        dbc.Button(
            'Submit',
            id='btn_username',
        ),
    ], id='username_prompt', style={'display': 'block'}),

    # Navigation bar
    dbc.Row([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink('Home', href='/')),
                dbc.NavItem(dbc.NavLink('Scoreboard', href='scoreboard')),
            ],
            brand=[
                dbc.Label('MathSprint'),
            ],
            id='navbar',
            color='primary',
            dark=True,
            fluid=True,
        ),
    ], id='navigation_bar', style={'display': 'none'}),

    # Page content
    dbc.Row([
        dash.page_container,
    ], id='page_content', style={'display': 'none'}),
    
])

# Callback functions
@callback(
    Output('username_prompt', 'style'),
    Output('navigation_bar', 'style'),
    Output('page_content', 'style'),
    Output('navbar', 'brand'),

    Input('input_username', 'n_submit'),
    Input('btn_username', 'n_clicks'),
    State('input_username', 'value'),
    State('navbar', 'brand'),
    
    prevent_initial_call=True,
)
def handle_username(n_enter: int, n_submit: int, username: str, brand: list) -> list:
    """
    Handles user input of username and displays it on navigation bar. The username is then retrieved
    from the navigation bar later to record score in database.
    """
    if username == '':
        username = 'anonymous'
        
    brand.append(
        dbc.Label(
            f'Welcome {username}'
        )
    )
    return [{'display': 'none'}, {'display': 'block'}, {'display': 'block'}, brand]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
