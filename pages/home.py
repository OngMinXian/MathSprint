import dash
from dash import Dash, html, dcc, callback, Output, Input, State, callback_context, ALL, MATCH, dash_table, no_update
import dash_bootstrap_components as dbc

import random

dash.register_page(__name__, path='/')

def generate_prompts(operator='Multiplication', mode='normal'):
    prompts = []
    answers = []

    if mode == 'Normal':
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

    elif mode == 'Hard':
        for i in range(1000):
            i, j, k = random.randint(0, 13), random.randint(0, 13), random.randint(1, 100)
            
            if random.randint(0, 1):
                prompt = f'{i} * {j}'
                answer = i * j
            else:
                if j == 0:
                    continue
                prompt = f'{i * j} / {j}'
                answer = i

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
        
    zipped = list(zip(prompts, answers))
    random.shuffle(zipped)
    prompts, answers = zip(*zipped)

    return list(prompts), list(answers)

layout = dbc.Container(fluid=True, children=[

    # Start game and settings
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

    # End game screen
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
def start_game(n_start, store, mode, operator):
    prompts, answers = generate_prompts(operator=operator, mode=mode)
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

        # Still have more prompts
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
def handle_timer(n_interval):
    return f'{60 - n_interval} seconds left'

@callback(
    Output('container_end', 'style', allow_duplicate=True),
    Output('container_game', 'style', allow_duplicate=True),
    Output('label_finalscore', 'children'),

    Input('interval_timer', 'n_intervals'),
    State('store_game', 'data'),
    Input('btn_endgame', 'n_clicks'),

    prevent_initial_call=True,
)
def handle_endgame(n_interval, store, n_clicks):
    if (n_interval == 60 and 'score' in store) or \
    store.get('answers') == [] or \
    callback_context.args_grouping[2]['triggered']:
        score = store['score']
        store['score'] = -1
        return {'display':' block'}, {'display':' none'}, f'Your final score is {score}'

    else:
        return no_update

@callback(
    Output('container_end', 'style', allow_duplicate=True),
    Output('container_start', 'style', allow_duplicate=True),
    Output('store_game', 'data', allow_duplicate=True),

    Input('btn_newgame', 'n_clicks'),

    prevent_initial_call=True,
)
def handle_newgame(n_clicks):
    return {'display':' none'}, {'display':' block'}, {}

@callback(
    Output('container_operator', 'style'),
    Input('select_difficulty', 'value'),
)
def toggle_operators_display(difficulty):
    return {'display': 'block'} if difficulty == 'Normal' else {'display': 'none'}

