import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

import random

dash.register_page(__name__, path='/')

def generate_prompts(low=0, high=12):
    prompts = []
    answers = []
    for i in range(low, high + 1):
        for j in range(low, high + 1):
            prompts.append(dbc.Label(f'{i} x {j}'))
            answers.append(i * j)
    
    zipped = list(zip(prompts, answers))
    random.shuffle(zipped)
    prompts, answers = zip(*zipped)

    return list(prompts), list(answers)

layout = dbc.Container(fluid=True, children=[

    # Start game and settings
    dbc.Container(fluid=True, children=[

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


    ], id='container_game', style={'display':' none'}),

    # End game screen
    dbc.Container(fluid=True, children=[
        dbc.Label(
            '', 
            id='label_finalscore'
        ),
        dbc.Button(
            'Start new game',
            id='btn_newgame',
        )
    ], id='container_end', style={'display':' none'}),

    # Store
    dcc.Store(
        id='store_game',
        data={},
    ),

])

@callback(
    Output('container_start', 'style', allow_duplicate=True),
    Output('container_game', 'style', allow_duplicate=True),
    Output('store_game', 'data', allow_duplicate=True),
    Output('math_prompt', 'children', allow_duplicate=True),
    Output('interval_timer', 'n_intervals'),

    Input('btn_start', 'n_clicks'),
    State('store_game', 'data'),

    prevent_initial_call=True,
)
def start_game(n_start, store):
    prompts, answers = generate_prompts()
    first_prompt = prompts.pop(0)
    store['prompts'] = prompts
    store['answers'] = answers
    store['score'] = 0
    return {'display':' none'}, {'display':' block'}, store, first_prompt, 0

@callback(
    Output('math_prompt', 'children', allow_duplicate=True),
    Output('store_game', 'data', allow_duplicate=True),
    Output('input_ans', 'value'),
    Output('alert_correct', 'is_open'),
    Output('alert_wrong', 'is_open'),
    Output('label_score', 'children'),

    Input('input_ans', 'n_submit'),
    State('input_ans', 'value'),
    State('store_game', 'data'),
    State('math_prompt', 'children'),

    prevent_initial_call=True,
)
def handle_ans(n_submit, input_ans, store, curr_prompt):
    curr_ans = store['answers'][0]
    # Answered correctly
    if curr_ans == input_ans:
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
def handle_timer(n_interval):
    return f'{60 - n_interval} seconds left'

@callback(
    Output('container_end', 'style', allow_duplicate=True),
    Output('container_game', 'style', allow_duplicate=True),
    Output('label_finalscore', 'children'),

    Input('interval_timer', 'n_intervals'),
    State('store_game', 'data'),

    prevent_initial_call=True,
)
def handle_endgame(n_interval, store):
    if n_interval == 60 and 'score' in store:
        score = store['score']
        store['score'] = -1
        return {'display':' block'}, {'display':' none'}, f'Your final score is {score}'

    else:
        return no_update

@callback(
    Output('container_end', 'style', allow_duplicate=True),
    Output('container_start', 'style', allow_duplicate=True),

    Input('btn_newgame', 'n_clicks'),

    prevent_initial_call=True,
)
def handle_newgame(n_clicks):
    return {'display':' none'}, {'display':' block'}
