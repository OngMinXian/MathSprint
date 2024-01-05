# Import libraries
import random
import datetime
import pandas as pd

import dash
from dash import dcc, callback, Output, Input, State, callback_context, no_update
import dash_bootstrap_components as dbc

from s3_client import get_scoreboard_from_s3, write_scoreboard_to_s3

dash.register_page(__name__, path='/')

# Helper functions
def generate_prompts(
    operator: str='Multiplication', difficulty: str='Normal'
) -> tuple[list, list]:
    """
    Generates math prompts and answers based on difficulty and operator. Then, prompts and
    answers are shuffled. Normal prompts consists of 2 operands and 1 operator.
    Hard prompts consist of 3 operands and 2 operators (+ or - and * or /).
    Inputs:
        operator (str): Addition, Subtraction, Multiplication, Division
        difficulty (str): Normal, Hard
    """
    prompts = []
    answers = []

    if difficulty == 'Normal':
        if 'Multiplication' == operator:
            for i in range(0, 13):
                for j in range(0, 13):
                    prompts.append([i, 'x', j])
                    answers.append(i * j)

        elif 'Addition' == operator:
            for i in range(1, 101):
                for j in range(1, 101):
                    prompts.append([i, '+', j])
                    answers.append(i + j)

        elif 'Subtraction' == operator:
            for i in range(1, 101):
                for j in range(1, 101):
                    prompts.append([i, '-', j])
                    answers.append(i - j)

        elif 'Division' == operator:
            for i in range(0, 13):
                for j in range(1, 13):
                    prompts.append([i * j, '/', j])
                    answers.append(i)

    elif difficulty == 'Hard':
        for i in range(1000):
            # Generate 3 random operands
            i, j, k = random.randint(0, 12), random.randint(0, 12), random.randint(1, 100)
            
            # Generates random operator between * and /
            if random.randint(0, 1):
                prompt = [i, 'x', j]
                answer = i * j
            else:
                if j == 0:
                    continue
                prompt = [i * j, '/', j]
                answer = i

            # Generates random operator between + and - and its relative position
            if random.randint(0, 1):
                if random.randint(0, 1):
                    prompt += ['+', k]
                else:
                    prompt = [k, '+'] + prompt
                answer += k
            else:
                if random.randint(0, 1):
                    prompt += ['-', k]
                    answer -= k
                else:
                    prompt = [k, '-'] + prompt
                    answer = k - answer
                
            prompts.append(prompt)
            answers.append(answer)
    
    # Randomly shuffles prompts and answers
    zipped = list(zip(prompts, answers))
    random.shuffle(zipped)
    prompts, answers = zip(*zipped)

    return list(prompts), list(answers)

# Page layout
layout = dbc.Container(fluid=True, children=[

    # Start game and settings display
    dbc.Container(fluid=True, children=[

        # Styling container
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Row([

                            dbc.Col([
                                # Description
                                dbc.Row([], id='game_description')
                            ], width=4),

                            dbc.Col([
                                # Difficulty setting
                                dbc.Row(
                                    [
                                        dbc.Label(
                                            'Select difficulty:',
                                            style={
                                                'width': '15vw',
                                                'color': '#ffffff',
                                                'text-align': 'center',
                                                'font-weight': 'bold',
                                                'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.2)',
                                            },
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {'label': 'Normal', 'value': 'Normal'},
                                                {'label': 'Hard', 'value': 'Hard'},
                                            ],
                                            value='Normal',
                                            id='select_difficulty',
                                            inline=True,
                                            style={
                                                'width': '40vw',
                                            },
                                            labelStyle={
                                                'color': '#ffffff',
                                                'text-align': 'center',
                                                'font-weight': 'bold',
                                                'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.2)',
                                            },
                                        ),
                                    ], 
                                    justify='center', 
                                    style={
                                        'font-size': '1.3vw',
                                        'margin': '2%',
                                    },
                                ),

                                # Operator setting
                                dbc.Row(
                                    [
                                        dbc.Label(
                                            'Select operator:',
                                            style={
                                                'width': '15vw',
                                                'color': '#ffffff',
                                                'text-align': 'center',
                                                'font-weight': 'bold',
                                                'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.2)',
                                            },
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {'label': 'Addition', 'value': 'Addition'},
                                                {'label': 'Subtraction', 'value': 'Subtraction'},
                                                {'label': 'Multiplication', 'value': 'Multiplication'},
                                                {'label': 'Division', 'value': 'Division'},
                                            ],
                                            value='Addition',
                                            id='select_operator',
                                            inline=True,
                                            style={
                                                'width': '40vw',
                                            },
                                            labelStyle={
                                                'color': '#ffffff',
                                                'text-align': 'center',
                                                'font-weight': 'bold',
                                                'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.2)',
                                            },
                                        ),
                                    ], 
                                    justify='center', 
                                    style={
                                        'font-size': '1.3vw',
                                        'margin': '2%',
                                    },
                                ),

                                # Start game button
                                dbc.Row(
                                    [
                                        dbc.Button(
                                            'Start game',
                                            id='btn_start',
                                            size='lg',
                                            style={
                                                'width': '10vw',
                                                'color': '#ffffff',
                                                'text-align': 'center',
                                                'background-color': '#595959',
                                                'border': '0px',
                                                'border-radius': '0px',
                                            },
                                        ),
                                    ], 
                                    justify='center',
                                ),
                            ], width=8, align='center'),

                        ]),
                    ],
                    style={
                        'background-color': '#00e6b8',
                        'height': '60vh',
                        'margin': '1% 0%',
                        'padding': '2% 2% 2% 2%',
                        'border': '0px',
                        'box-shadow': 'rgba(50, 50, 93, 0.35) 0px 20px 50px -20px, rgba(0, 0, 0, 0.5) 0px 10px 20px -10px',
                    },
                ),
            ],
            align='center',
            style={
                'height': '70vh'
            },
        ),

    ], id='container_start', style={'display':' block'}),

    # Game container
    dbc.Container(fluid=True, children=[

        # Styling container
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Row(
                            children=[
                                # Score
                                dbc.Col([
                                    dbc.Label(
                                        'Score: 0',
                                        id='label_score',
                                        style={
                                            'font-size': '2vw',
                                            'color': '#ffffff',
                                            'text-align': 'center',
                                            'font-weight': 'bold',
                                            'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.2)',
                                        },
                                    )
                                ]),
                                
                                # Timer
                                dbc.Col([
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label(
                                                '60 seconds left',
                                                id='label_timer',
                                                style={
                                                    'font-size': '2vw',
                                                    'color': '#ffffff',
                                                    'text-align': 'center',
                                                    'font-weight': 'bold',
                                                    'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.2)',
                                                },
                                            ),
                                            dcc.Interval(
                                                id='interval_timer',
                                                interval=1000,
                                                n_intervals=0,
                                            ),
                                        ], width=4),
                                    ], justify='end'),
                                ]),
                            ],
                        ),

                        dbc.Row(
                            children=[

                                # Normal math prompts
                                dbc.Container(
                                    id='math_prompt_normal',
                                    children=[
                                        dbc.Row([

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='normal_operand_1',
                                                        
                                                    ),
                                                    class_name='operand-card',
                                                )
                                            ),

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='normal_operator_1',
                                                    ),
                                                    class_name='operator-card',
                                                )
                                            ),

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='normal_operand_2',
                                                    ),
                                                    class_name='operand-card',
                                                )
                                            ),

                                        ])
                                    ],
                                    style={
                                        'display': 'none',
                                    },
                                ),

                                # Hard math prompts
                                dbc.Container(
                                    id='math_prompt_hard',
                                    children=[
                                        dbc.Row([

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='hard_operand_1',
                                                    ),
                                                    class_name='operand-card',
                                                )
                                            ),

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='hard_operator_1',
                                                    ),
                                                    class_name='operator-card',
                                                )
                                            ),

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='hard_operand_2',
                                                    ),
                                                    class_name='operand-card',
                                                )
                                            ),

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='hard_operator_2',
                                                    ),
                                                    class_name='operator-card',
                                                )
                                            ),

                                            dbc.Col(
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        '',
                                                        id='hard_operand_3',
                                                    ),
                                                    class_name='operand-card',
                                                )
                                            ),

                                        ])
                                    ],
                                    style={
                                        'display': 'none',
                                    },
                                ),

                            ],
                        ),

                        dbc.Row(
                            children=[
                                # Correct alert
                                dbc.Col(
                                    dbc.Alert(
                                        'Correct answer! +1',
                                        color='primary',
                                        id='alert_correct',
                                        is_open=False,
                                        duration=2000,
                                        style={
                                            'text-align': 'center',
                                            'font-size': '2vw',
                                        },
                                    ),
                                    style={
                                        'height': '20vh',
                                    },
                                ),

                                # User input
                                dbc.Col(
                                    dbc.Input(
                                        id='input_ans',
                                        type='number',
                                        autofocus=True,
                                        autocomplete=False,
                                        style={
                                            'text-align': 'center',
                                            'font-size': '6vw',
                                            'color': '#595959',
                                            'height': '90%',
                                            'border': '0px',
                                            'border-radius': '0px',
                                            'box-shadow': 'inset 0 0 8px rgba(0, 0, 0, 0.3)',
                                        },
                                    ),
                                    style={
                                        'height': '20vh',
                                    },
                                ),

                                # Wrong alert
                                dbc.Col(
                                    dbc.Alert(
                                        'Wrong answer! -1',
                                        color='danger',
                                        id='alert_wrong',
                                        is_open=False,
                                        duration=2000,
                                        style={
                                            'text-align': 'center',
                                            'font-size': '2vw',
                                        },
                                    ),
                                    style={
                                        'height': '20vh',
                                    },
                                ),
                            ],
                        ),

                        dbc.Row(
                            children=[
                                # End game
                                dbc.Button(
                                    'End game',
                                    id='btn_endgame',
                                    size='lg',
                                    style={
                                        'width': '10vw',
                                        'color': '#ffffff',
                                        'background-color': '#595959',
                                        'border': '0px',
                                        'border-radius': '0px',
                                    },
                                ),
                            ],
                            justify='center', 
                        ),

                    ],
                    style={
                        'background-color': '#00e6b8',
                        'height': '76vh',
                        'margin': '1% 0%',
                        'padding': '2% 2% 2% 2%',
                        'border': '0px',
                        'box-shadow': 'rgba(50, 50, 93, 0.35) 0px 20px 50px -20px, rgba(0, 0, 0, 0.5) 0px 10px 20px -10px',
                    },
                ),
            ],
            align='center',
            style={
                'height': '88vh'
            },
        ),

    ], id='container_game', style={'display':' none'}),

    # End game container
    dbc.Container(fluid=True, children=[

        # Styling container
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        
                        # Final score
                        dbc.Row([
                            dbc.Label(
                                '', 
                                id='label_finalscore',
                                style={
                                    'font-size': '6vw',
                                    'color': '#ffffff',
                                    'text-align': 'center',
                                    'font-weight': 'bold',
                                    'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.5)',
                                },
                            ),
                        ]),

                        # Start new game button
                        dbc.Row([
                            dbc.Button(
                                'Start new game',
                                id='btn_newgame',
                                size='lg',
                                style={
                                    'width': '10vw',
                                    'color': '#ffffff',
                                    'background-color': '#595959',
                                    'border': '0px',
                                    'border-radius': '0px',
                                },
                            ),
                        ], justify='center'),

                    ],
                    style={
                        'background-color': '#00e6b8',
                        'height': '40vh',
                        'margin': '1% 0%',
                        'padding': '2% 2% 2% 2%',
                        'border': '0px',
                        'box-shadow': 'rgba(50, 50, 93, 0.35) 0px 20px 50px -20px, rgba(0, 0, 0, 0.5) 0px 10px 20px -10px',
                    },
                )
            ],
            align='center',
            style={
                'height': '88vh'
            },
        ),

    ], id='container_end', style={'display':' none'}),

    # Store
    dcc.Store(
        id='store_game',
        data={},
    ),

])

# Callback functions
@callback(
    Output('container_start', 'style', allow_duplicate=True),
    Output('container_game', 'style', allow_duplicate=True),
    Output('store_game', 'data', allow_duplicate=True),
    Output('interval_timer', 'n_intervals'),
    Output('label_score', 'children', allow_duplicate=True),

    Output('math_prompt_normal', 'style', allow_duplicate=True),
    Output('math_prompt_hard', 'style', allow_duplicate=True),

    Output('normal_operand_1', 'children', allow_duplicate=True),
    Output('normal_operator_1', 'children', allow_duplicate=True),
    Output('normal_operand_2', 'children', allow_duplicate=True),

    Output('hard_operand_1', 'children', allow_duplicate=True),
    Output('hard_operator_1', 'children', allow_duplicate=True),
    Output('hard_operand_2', 'children', allow_duplicate=True),
    Output('hard_operator_2', 'children', allow_duplicate=True),
    Output('hard_operand_3', 'children', allow_duplicate=True),

    Input('btn_start', 'n_clicks'),
    State('store_game', 'data'),
    State('select_difficulty', 'value'),
    State('select_operator', 'value'),

    prevent_initial_call=True,
)
def start_game(
    n_start: int, store: dict, difficulty: str, operator: str
) -> list[dict, dict, dict, str, int]:
    """
    Starts game by generating prompts and answers and storing them in dcc store.
    Displays the first prompt.
    """
    # Generate prompts and answers
    prompts, answers = generate_prompts(operator=operator, difficulty=difficulty)
    first_prompt = prompts.pop(0)

    # Initialize store
    store['prompts'] = prompts
    store['answers'] = answers
    store['score'] = 0

    # Checks which card display to show
    if difficulty == 'Normal':
        return [
            {'display':' none'}, {'display':' block'}, store, 0, 'Score: 0',
            {'display':' block'}, {'display':' none'},
            first_prompt[0], first_prompt[1], first_prompt[2],
            '', '', '', '', ''
        ]

    else:
        return [
            {'display':' none'}, {'display':' block'}, store, 0, 'Score: 0',
            {'display':' none'}, {'display':' block'},
            '', '', '',
            first_prompt[0], first_prompt[1], first_prompt[2], first_prompt[3], first_prompt[4]
        ] 

@callback(
    Output('store_game', 'data', allow_duplicate=True),
    Output('input_ans', 'value', allow_duplicate=True),
    Output('alert_correct', 'is_open'),
    Output('alert_wrong', 'is_open'),
    Output('label_score', 'children', allow_duplicate=True),

    Output('normal_operand_1', 'children', allow_duplicate=True),
    Output('normal_operator_1', 'children', allow_duplicate=True),
    Output('normal_operand_2', 'children', allow_duplicate=True),

    Output('hard_operand_1', 'children', allow_duplicate=True),
    Output('hard_operator_1', 'children', allow_duplicate=True),
    Output('hard_operand_2', 'children', allow_duplicate=True),
    Output('hard_operator_2', 'children', allow_duplicate=True),
    Output('hard_operand_3', 'children', allow_duplicate=True),

    Input('input_ans', 'n_submit'),
    State('input_ans', 'value'),
    State('store_game', 'data'),
    State('select_difficulty', 'value'),

    State('normal_operand_1', 'children'),
    State('normal_operator_1', 'children'),
    State('normal_operand_2', 'children'),

    State('hard_operand_1', 'children'),
    State('hard_operator_1', 'children'),
    State('hard_operand_2', 'children'),
    State('hard_operator_2', 'children'),
    State('hard_operand_3', 'children'),

    prevent_initial_call=True,
)
def handle_ans(
    n_submit: int, input_ans: int, store: dict, difficulty: str,
    n_operand_1: str, n_operator_1: str, n_operand_2: str,
    h_operand_1: str, h_operator_1: str, h_operand_2: str, h_operator_2: str, h_operand_3: str,
) -> list[dbc.Label, dict, str, bool, bool, str]:
    """
    Handles user input of answer, triggered when user types results and hits enter key. 
    Increment score if correct and decrement score if wrong and displays appropriate alert.
    If answered correctly, check whether there are more prompts.
    """
    curr_ans = store['answers'][0]

    # Answered correctly
    if curr_ans == input_ans:
        # There are more prompts
        next_prompt = dbc.Label('')
        if store['prompts'] != []:
            next_prompt = store['prompts'][0]
            store['prompts'] = store['prompts'][1:]

        store['answers'] = store['answers'][1:]
        store['score'] += 1

        # Checks which card display to show
        if difficulty == 'Normal':
            return [
                store, '', True, False, f'Score: {store["score"]}',
                next_prompt[0], next_prompt[1], next_prompt[2],
                '', '', '', '', ''
            ]
        else:
            return [
                store, '', True, False, f'Score: {store["score"]}',
                '', '', '',
                next_prompt[0], next_prompt[1], next_prompt[2], next_prompt[3], next_prompt[4]
            ]

    # Answered wrongly
    else:
        store['score'] -= 1

        return [
            store, input_ans, False, True, f'Score: {store["score"]}',
            n_operand_1, n_operator_1, n_operand_2,
            h_operand_1, h_operator_1, h_operand_2, h_operator_2, h_operand_3,
        ]

@callback(
    Output('label_timer', 'children'),
    Input('interval_timer', 'n_intervals'),
)
def handle_timer(n_interval: int) -> str:
    """
    Changes 1 minute timer display of game.
    """
    return f'{60 - n_interval} seconds left'

@callback(
    Output('container_end', 'style', allow_duplicate=True),
    Output('container_game', 'style', allow_duplicate=True),
    Output('label_finalscore', 'children'),
    Output('input_ans', 'value'),

    Input('interval_timer', 'n_intervals'),
    State('store_game', 'data'),
    Input('btn_endgame', 'n_clicks'),

    State('navbar', 'brand'),
    State('select_difficulty', 'value'),
    State('select_operator', 'value'),

    prevent_initial_call=True,
)
def handle_end_game(
    n_interval: int, store: dict, n_clicks: int, brand: dict, difficulty: str, operator: str
) -> tuple[dict, dict, str, str]:
    """
    Check if game ended due to 1 minute timer is up or all prompts have been answered or
    user clicked on end game button. Score is recorded in a csv in S3 along with timestamp,
    username, difficulty and operator. The function is triggered by dcc Interval on a per second basis.
    """
    # Check if game ended due to timer or no more prompts or user clicked on end game
    if (n_interval == 60 and 'score' in store) or \
    store.get('answers') == [] or \
    callback_context.args_grouping[2]['triggered']:
        score = store['score']
        store['score'] = -1

        # Records score into S3
        timestamp = datetime.datetime.now()
        username = brand[0]['props']['children'].split(' ')[1]
        df_scoreboard = get_scoreboard_from_s3()
        df_scoreboard = pd.concat([df_scoreboard, pd.DataFrame({
            'timestamp': [timestamp],
            'username': [username],
            'difficulty': [difficulty],
            'operator': [operator] if difficulty == 'Normal' else ['Invalid'],
            'score': [score],
        })], axis=0, ignore_index=True)
        write_scoreboard_to_s3(df_scoreboard)

        return {'display':' block'}, {'display':' none'}, f'Your final score is {score}', ''

    else:
        return no_update

@callback(
    Output('container_end', 'style', allow_duplicate=True),
    Output('container_start', 'style', allow_duplicate=True),
    Output('store_game', 'data', allow_duplicate=True),

    Input('btn_newgame', 'n_clicks'),

    prevent_initial_call=True,
)
def handle_new_game(n_clicks: int) -> tuple[dict, dict, dict]:
    """
    Resets page back to original new game display
    """
    return {'display':' none'}, {'display':' block'}, {}

@callback(
    Output('select_operator', 'options'),
    Input('select_difficulty', 'value'),
)
def toggle_operators_display(difficulty: str) -> dict:
    """
    Enable/Disables operator options if difficulty is Normal/Hard
    """
    if difficulty == 'Normal':
        return [
            {'label': 'Addition', 'value': 'Addition'},
            {'label': 'Subtraction', 'value': 'Subtraction'},
            {'label': 'Multiplication', 'value': 'Multiplication'},
            {'label': 'Division', 'value': 'Division'},
        ]
    else:
        return [
            {'label': 'Addition', 'value': 'Addition', 'disabled': True},
            {'label': 'Subtraction', 'value': 'Subtraction', 'disabled': True},
            {'label': 'Multiplication', 'value': 'Multiplication', 'disabled': True},
            {'label': 'Division', 'value': 'Division', 'disabled': True},
        ]

@callback(
    Output('game_description', 'children'),
    Input('select_difficulty', 'value'),
    Input('select_operator', 'value'),
)
def toggle_game_description(difficulty: str, operator: str) -> str:
    """
    Changes game description (html component) based on difficulty.
    """
    # Default text style
    default_style = {
        'font-size': '140%',
        'font-weight': '500',
        'color': '#ffffff',
        'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.4)',
        'text-align': 'center',
    }
    example_style = {
        'font-size': '255%',
        'font-weight': '500',
        'color': '#ffffff',
        'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.4)',
        'text-align': 'center',
    }

    # Default description that does not change
    description = [
        dbc.Label(
            'Game Description',
            style={
                'font-size': '400%',
                'text-align': 'center',
                'font-weight': 'bold',
                'color': '#ffffff',
                'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.4)',
                'text-decoration': 'underline',
            },
        ),
        dbc.Label(
            '''
            You will be presented with math equations with a 1 minute timer.
            Type in your answer and hit enter to submit your answer.
            1 point will be awarded for a correct answer and 1 point will be deducted for a wrong answer.
            ''',
            style=default_style,
        ),
        dbc.Label(' ', style={'margin': '2%'}),
    ]

    # Add description based on difficulty and operator
    if difficulty == 'Normal':
        description += [
            dbc.Label(
                '''
                In normal mode, you can select an operator. Equations will contain 2 operands.
                ''',
                style=default_style,
            )
        ]
        
        if operator == 'Addition':
            description += [
                dbc.Label(
                    '''
                    Example: 24 + 52
                    ''',
                    style=example_style,
                )
            ]

        elif operator == 'Subtraction':
            description += [
                dbc.Label(
                    '''
                    Example: 89 - 14
                    ''',
                    style=example_style,
                )
            ]

        elif operator == 'Multiplication':
            description += [
                dbc.Label(
                    '''
                    Example: 3 * 2
                    ''',
                    style=example_style,
                )
            ]

        elif operator == 'Division':
            description += [
                dbc.Label(
                    '''
                    Example: 24 / 6
                    ''',
                    style=example_style,
                )
            ]
    
    elif difficulty == 'Hard':
        description += [
            dbc.Label(
                '''
                In hard mode, all operators can appear. Each equation will contain 3 operands and
                2 operators.
                ''',
                style=default_style,
            )
        ]
        description += [
            dbc.Label(
                '''
                Example: 5 x 3 + 25
                ''',
                style=example_style,
            )
        ]

    return description