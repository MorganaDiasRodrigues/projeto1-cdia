from dash import dcc, html, Dash
import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
import json

# Load JSON data
json_data = {
    "08/05/2023": 
    {"14:42": ["#SpiderManAcrossTheSpiderVerse", "Anaheim", "#Mondaymorning", "Goku", "Oppenheimer", "Infowars", "Joe Milton", "#corpsetwtselfieday", "Mythra", "Sean Dyche", "Krypto", "Sean Connery", "The Weeknd", "#RaiseTheAge", "Adderall", "Purge", "Weather Channel", "Red Cross", "Seer", "#Mondaythoughts"], 
     "15:12": ["#SpiderManAcrossTheSpiderVerse", "#TeacherAppreciationWeek", "Anaheim", "Oppenheimer", "Goku", "#corpsetwtselfieday", "Krypto", "#RaiseTheAge", "Seer", "#Mondaymorning", "Joe Milton", "Dark Souls 2", "The Weeknd", "Sean Connery", "Weather Channel", "Pyra", "Juelz", "Ewers", "Bedard", "#Mondayvibes"], 
     "15:42": ["#teachers", "Goku", "#QueenCharlotteNetflix", "Purge", "#Mondaymorning", "Krypto", "Joe Milton", "#BehindYouSkipper", "Texas Tactical Border Force", "#corpsetwtselfieday", "Tombstone", "Sean Connery", "Infowars", "The Weather Channel", "#HaveACokeDay", "SLOOS", "#RaiseTheAge", "The Weeknd", "jack antonoff", "HB 2744"], 
     "16:12": ["Purge", "#corpsetwtselfieday", "Goku", "Robert Moses", "Sean Connery", "Sharpe", "#BehindYouSkipper", "The Weeknd", "Mythra", "Texas House", "#Pistons", "#WritingCommnunity", "Oppenheimer", "Weather Channel", "Tombstone", "#RaiseTheAge", "SLOOS", "luke hemmings", "HB 2744", "Lowering"]
    },
    
    "09/05/2023": 
    {"00:12": ['#TheVoice','San Andreas','Columbus','GetPoole','Kyla','#VegasBorn','Kane','#AdamKutnerPowerPlay','Night of Champions','Jacksonville','Goth IHOP','Meg 2','#NHLDraft','Anaheim','Bettman','Grimes','Huggins','Dylan Cease','Fantilli','Ducks'], 
     "15:12": ['lorde', 'Robo', 'Romney', 'KD and Book', '#FBIMostWanted', 'TD Garden', 'Tony Buckets', '#TuckerCarlson', 'Assad', 'Okogie', '#911LoneStar', '#CWGothamKnights', '#MNUFC', 'Buddy Holly', 'David Ross', 'Game 6', 'Vindman', 'Pritchard', 'Monty Williams', 'corey'], 
     "15:42": ['#BoycottCNN', 'Bron and AD', 'Damn AD', 'Babyface', 'Hope AD', 'AD and Bron', 'Hopefully AD', 'Now AD', 'Street Clothes', 'Dave Chappelle', '#MAFS', '#DoneWithCNN', '#ChicagoPD', '#LakersVsWarriors', 'Daily Caller', 'Steve Kerr', 'Corgi', 'Paul Pierce', 'Ratings', 'Bro AD'], 
     "16:12": ['TD Garden', '#TXT_ASM_TOUR_in_NY', 'KD and Book', 'Assad', 'Book and KD', '#ForTheLoveOfPhilly', 'corey', 'Tony Buckets', '#USOC2023', '#cowx', 'Hintz', 'Buddy Holly', 'Kodansha', '#MNUFC', 'Vindman', 'Soler', 'Michael Porter Jr.', 'Okogie', 'George Kirby', 'Deandre Ayton']
    }
}

available_dates = list(json_data.keys())

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Div(
        id='date-buttons', 
        children=[html.Button(date, id={'type': 'date-button', 'index': i}) for i, date in enumerate(available_dates)],
        style={'position': 'absolute', 'right': '10%', 'top': '10%'}
    ),
    html.Div(id='time-buttons', style={'position': 'absolute', 'right': '10%', 'top': '20%'}),
    html.Div(id='graph', children=[
        html.H2("Please select a time", id='message', style={'font-family': 'Arial, Helvetica, sans-serif'})
    ], style={'position': 'absolute', 'left': '50%', 'top': '50%', 'transform': 'translate(-50%, -50%)'}),
    dcc.Store(id='store', storage_type='session'),
], style={'position': 'relative', 'height': '100vh'})

@app.callback(
    Output('time-buttons', 'children'),
    Input({'type': 'date-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'date-button', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def update_time_buttons(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_index = json.loads(button_id)['index']
        selected_date = labels[button_index]

        times = list(json_data[selected_date].keys())
        time_buttons = html.Div([
            html.Button(time, id={'type': 'time-button', 'index': i, 'date': selected_date}, n_clicks=0)
            for i, time in enumerate(times)
        ], id={'type': 'time-buttons', 'date': selected_date})

        return time_buttons

@app.callback(
    Output('graph', 'children'),
    Input({'type': 'time-button', 'index': ALL, 'date': ALL}, 'n_clicks'),
    State({'type': 'time-button', 'index': ALL, 'date': ALL}, 'children'),
    prevent_initial_call=True
)
def update_figure(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_info = json.loads(button_id)
        selected_time = labels[button_info['index']]
        selected_date = button_info['date']

        trends = json_data[selected_date][selected_time]

        ordered_list = html.Ol([html.Li(trend, style={'font-family': 'Arial, Helvetica, sans-serif'}) for trend in trends])
        return ordered_list

if __name__ == '__main__':
    app.run_server(debug=True)
