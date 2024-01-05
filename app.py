# Import libraries
from dash import dash, Dash, callback, Output, Input, State
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

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
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Row(
                            dbc.Label(
                                'MATHSPRINT',
                                style={
                                    'color': '#ffffff',
                                    'font-size': '8vw',
                                    'text-align': 'center',
                                    'font-weight': 'bold',
                                    'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.5)',
                                }
                            ),
                        ),
                        dbc.Row([
                            dbc.Input(
                                id='input_username',
                                placeholder='Enter username',
                                style={
                                    'width': '30vw',
                                    'border': '0px',
                                    'border-radius': '0px',
                                    'box-shadow': 'inset 0 0 8px rgba(0, 0, 0, 0.3)',
                                },
                            ),
                            dbc.Button(
                                'Submit',
                                id='btn_username',
                                style={
                                    'width': '5vw',
                                    'color': '#ffffff',
                                    'background-color': '#595959',
                                    'border': '0px',
                                    'border-radius': '0px',
                                },
                            ),
                        ], justify='center'),
                    ]),
                ], align='center', style={'height': '100vh'}),
            ],
            style={
                'background-color': '#00e6b8',
                'height': '100vh',
            },
        ),
    ], id='username_prompt', style={'display': 'block'}),

    # Navigation bar
    dbc.Row([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(
                    dbc.NavLink(
                        DashIconify(
                            icon='mingcute:game-2-fill', 
                            width=55,
                            height=55,
                        ),
                        href='/',
                        class_name='navi-colored',
                    )
                ),
                dbc.NavItem(
                    dbc.NavLink(
                        DashIconify(
                            icon='material-symbols:trophy', 
                            width=55,
                            height=55,
                        ), 
                        href='scoreboard',
                        class_name='navi-colored',
                    )
                ),
            ],
            brand=[],
            id='navbar',
            color='#00e6b8',
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
    if not username:
        username = 'anonymous'
        
    brand.append(
        dbc.Label(
            f'Welcome to MathSprint, {username}!',
            style={
                'color': '#ffffff',
                'font-size': '150%',
                'text-align': 'center',
                'font-weight': 'bold',
                'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.3)',
                'margin-left': '2vw',
            },
        )
    )
    return [{'display': 'none'}, {'display': 'block'}, {'display': 'block'}, brand]

# Run the app
if __name__ == '__main__':
    app.run(
        port=8050,
        host='0.0.0.0'
    )

'''
Todo:
    - Set focus onto input box upon starting game

'''