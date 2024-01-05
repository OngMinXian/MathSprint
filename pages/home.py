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
                    prompts.append(dbc.Label(f'{i} x {j}'))
                    answers.append(i * j)

        elif 'Addition' == operator:
            for i in range(1, 101):
                for j in range(1, 101):
                    prompts.append(dbc.Label(f'{i} + {j}'))
                    answers.append(i + j)

        elif 'Subtraction' == operator:
            for i in range(1, 101):
                for j in range(1, 101):
                    prompts.append(dbc.Label(f'{i} - {j}'))
                    answers.append(i - j)

        elif 'Division' == operator:
            for i in range(0, 13):
                for j in range(1, 13):
                    prompts.append(dbc.Label(f'{i * j} / {j}'))
                    answers.append(i)

    elif difficulty == 'Hard':
        for i in range(1000):
            # Generate 3 random operands
            i, j, k = random.randint(0, 12), random.randint(0, 12), random.randint(1, 100)
            
            # Generates random operator between * and /
            if random.randint(0, 1):
                prompt = f'{i} * {j}'
                answer = i * j
            else:
                if j == 0:
                    continue
                prompt = f'{i * j} / {j}'
                answer = i

            # Generates random operator between + and - and its relative position
            if random.randint(0, 1):
                if random.randint(0, 1):
                    prompt += f' + {k}'
                else:
                    prompt = f'{k} + ' + prompt
                answer += k
            else:
                if random.randint(0, 1):
                    prompt += f' - {k}'
                    answer -= k
                else:
                    prompt = f'{k} - ' + prompt
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

        # Difficulty setting
        dbc.Label('Select difficulty:'),
        dbc.RadioItems(
            options=[
                {'label': 'Normal', 'value': 'Normal'},
                {'label': 'Hard', 'value': 'Hard'},
            ],
            value='Normal',
            id='select_difficulty',
        ),

        # Operator setting
        dbc.Container(fluid=True, children=[
            dbc.Label('Select operator:'),
            dbc.RadioItems(
                options=[
                    {'label': 'Addition', 'value': 'Addition'},
                    {'label': 'Subtraction', 'value': 'Subtraction'},
                    {'label': 'Multiplication', 'value': 'Multiplication'},
                    {'label': 'Division', 'value': 'Division'},
                ],
                value='Multiplication',
                id='select_operator',
            ),
        ], id='container_operator', style={'display': 'block'}),

        # Start game button
        dbc.Button('Start game', id='btn_start'),


    ], id='container_start', style={'display':' block'}),

    # Game container
    dbc.Container(fluid=True, children=[
        # Timer
        dbc.Label(
            '60 seconds left',
            id='label_timer',
        ),
        dcc.Interval(
            id='interval_timer',
            interval=1000,
            n_intervals=0,
        ),

        # Score
        dbc.Label(
            'Score: 0',
            id='label_score',
        ),

        # Math prompt
        dbc.Container(
            id='math_prompt',
            children=[],
        ),

        # User input
        dbc.Input(
            id='input_ans',
            type='number',
        ),

        # Correct alert
        dbc.Alert(
            'Correct answer! +1',
            color='success',
            id='alert_correct',
            is_open=False,
            duration=2000,
        ),

        # Wrong alert
        dbc.Alert(
            'Wrong answer! -1',
            color='danger',
            id='alert_wrong',
            is_open=False,
            duration=2000,
        ),

        # End game
        dbc.Button(
            'End game',
            id='btn_endgame',
        ),

    ], id='container_game', style={'display':' none'}),

    # End game display
    dbc.Container(fluid=True, children=[
        dbc.Label(
            '', 
            id='label_finalscore'
        ),
        dbc.Button(
            'Start new game',
            id='btn_newgame',
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
    Output('math_prompt', 'children', allow_duplicate=True),
    Output('interval_timer', 'n_intervals'),

    Input('btn_start', 'n_clicks'),
    State('store_game', 'data'),
    State('select_difficulty', 'value'),
    State('select_operator', 'value'),

    prevent_initial_call=True,
)
def start_game(
    n_start: int, store: dict, difficulty: str, operator: str
) -> tuple[dict, dict, dict, str, int]:
    """
    Starts game by generating prompts and answers and storing them in dcc store.
    """
    # Generate prompts and answers
    prompts, answers = generate_prompts(operator=operator, difficulty=difficulty)
    first_prompt = prompts.pop(0)

    # Initialize store
    store['prompts'] = prompts
    store['answers'] = answers
    store['score'] = 0

    return {'display':' none'}, {'display':' block'}, store, first_prompt, 0

@callback(
    Output('math_prompt', 'children', allow_duplicate=True),
    Output('store_game', 'data', allow_duplicate=True),
    Output('input_ans', 'value', allow_duplicate=True),
    Output('alert_correct', 'is_open'),
    Output('alert_wrong', 'is_open'),
    Output('label_score', 'children'),

    Input('input_ans', 'n_submit'),
    State('input_ans', 'value'),
    State('store_game', 'data'),
    State('math_prompt', 'children'),

    prevent_initial_call=True,
)
def handle_ans(
    n_submit: int, input_ans: int, store: dict, curr_prompt: dbc.Label
) -> tuple[dbc.Label, dict, str, bool, bool, str]:
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
        return next_prompt, store, '', True, False, f'Score: {store["score"]}'

    # Answered wrongly
    else:
        store['score'] -= 1
        return curr_prompt, store, input_ans, False, True, f'Score: {store["score"]}'

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
        username = brand[1]['props']['children'].split(' ')[1]
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
    Output('container_operator', 'style'),
    Input('select_difficulty', 'value'),
)
def toggle_operators_display(difficulty: str) -> dict:
    """
    Show/hides operator options if difficulty is Normal/Hard
    """
    return {'display': 'block'} if difficulty == 'Normal' else {'display': 'none'}
