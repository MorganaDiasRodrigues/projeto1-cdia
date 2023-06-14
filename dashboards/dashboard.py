from dash import dcc, html, Dash
import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objects as go
import json

# JSON data
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

# Load the images data
with open('trends_images.json') as f:
    trends_images = json.load(f)

available_dates = list(json_data.keys())

app = Dash(__name__)

app.layout = html.Div([
    html.Div(id='date-buttons', children=[
        html.Button(date, id={'type': 'date-button', 'index': i}) for i, date in enumerate(available_dates)
    ]),
    html.Div(id='time-buttons'),
    dcc.Store(id='store', storage_type='session'),
    html.Div(id='graph', children=[
        html.H2("Please select a date")
    ]),
    dcc.Store(id='store-trend', storage_type='session'),
    html.Div(id='trend-images'),
    dcc.Graph(id='donut-chart'),
])

@app.callback(
    Output('time-buttons', 'children'),
    Input({'type': 'date-button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_time_buttons(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.dcc.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_index = json.loads(button_id)['index']
        selected_date = available_dates[button_index]

        # Store the selected date in dcc.Store
        app.clientside_callback(
            f"""
            function(n_clicks) {{
                return "{selected_date}";
            }}
            """,
            Output('store', 'data'),
            Input({'type': 'date-button', 'index': button_index}, 'n_clicks')
        )

        return [html.Button(time, id={'type': 'time-button', 'index': i}) for i, time in enumerate(json_data[selected_date].keys())]

@app.callback(
    Output('graph', 'children'),
    Input({'type': 'time-button', 'index': ALL}, 'n_clicks'),
    Input('store', 'data'),
    prevent_initial_call=True
)
def update_figure(n_clicks, selected_date):
    ctx = dash.callback_context
    if not ctx.triggered or not selected_date:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_index = json.loads(button_id)['index']
        time = list(json_data[selected_date].keys())[button_index]
        trends = json_data[selected_date][time]

        fig = go.Figure(data=[go.Table(
            header=dict(values=['Rank', 'Trending Topic']),
            cells=dict(values=[[i+1 for i in range(len(trends))], [html.Button(trend, id={'type': 'trend-button', 'index': i}) for i, trend in enumerate(trends)]])
        )])

        return dcc.Graph(figure=fig)

@app.callback(
    [Output('trend-images', 'children'), Output('donut-chart', 'figure')],
    [Input({'type': 'trend-button', 'index': ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def display_trend_info(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.dcc.no_update, dash.dcc.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_index = json.loads(button_id)['index']

        trend = trends[button_index]

        trend_image_data = trends_images.get(trend, {})
        image_files = trend_image_data.get('images', [])
        image_colours = trend_image_data.get('colours', [])

        image_div = html.Div([
            html.Img(src=f'/path/to/your/images/{image_file}') for image_file in image_files
        ])

        fig = go.Figure(data=[go.Pie(labels=[f'Color {i+1}' for i in range(len(image_colours))], values=image_colours, hole=.3)])

        return image_div, fig

if __name__ == '__main__':
    app.run_server(debug=True)
