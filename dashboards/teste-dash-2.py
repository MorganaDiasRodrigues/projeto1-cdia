import base64
import json
from collections import Counter
from io import BytesIO
from PIL import Image

import cv2
import dash
import dash_bootstrap_components as dbc
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output, State, MATCH, ALL
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from urllib.request import urlopen


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

images_dict = {
    "#SpiderManAcrossTheSpiderVerse": {
        "images": [
            {"path": "assets/spider1.jpg"},
            {"path": "assets/spider2.jpg"},
            {"path": "assets/spider3.jpg"}
        ]
    },
    # your other trends with image paths
}

available_dates = list(json_data.keys())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return f'data:image/png;base64,{encoded.decode()}'

def rgb2hex(rgb):
    hex = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return hex

def find_image_colors(image_path, n_colors):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    kmeans = KMeans(n_clusters=n_colors)
    labels = kmeans.fit_predict(image)

    counts = Counter(labels)

    center_colors = kmeans.cluster_centers_
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [rgb2hex(ordered_colors[i]) for i in counts.keys()]
    hex_colors = [hex_colors[i] for i in counts.keys()]

    return hex_colors


# Define the app layout
app.layout = html.Div([
    html.Div([
        html.Button(date, id={'type': 'date-button', 'index': i}, n_clicks=0) for i, date in enumerate(available_dates)
    ], id='date-buttons'),
    html.Div(id='time-buttons'),
    html.Div(id='graph'),
    html.Div(id='trend-detail')
])


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

        available_times = list(json_data[selected_date].keys())
        return [html.Button(time, id={'type': 'time-button', 'index': i, 'date': selected_date}, n_clicks=0) for i, time in
                enumerate(available_times)]


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

        ordered_list = html.Ol([html.Li(dcc.Link(trend, id={'type': 'trend-link', 'index': i, 'date': selected_date},
                                                 href='#', style={'font-family': 'Arial, Helvetica, sans-serif'}))
                                for i, trend in enumerate(trends)])
        return ordered_list


@app.callback(
    Output('trend-detail', 'children'),
    Input({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'n_clicks'),
    State({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'children'),
    prevent_initial_call=True
)
def display_trend_detail(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_info = json.loads(button_id)
        selected_trend = labels[button_info['index']]

        image_data = images_dict[selected_trend]['images']

        images = []
        pie_data = []
        for img in image_data:
            image_path = img['path']
            hex_codes = find_image_colors(image_path, 5)
            pie_data.extend(hex_codes)
            encoded_image = encode_image(image_path)
            images.append(html.Img(src=encoded_image, style={'width': '200px', 'height': '200px'}))

        pie_chart = dcc.Graph(figure={
            'data': [{
                'values': [1]*len(pie_data),
                'labels': pie_data,
                'type': 'pie',
                'marker': {'colors': pie_data}
            }],
            'layout': {
                'title': 'Dominant Colors in Images'
            }
        })

        return images + [pie_chart]


if __name__ == '__main__':
    app.run_server(debug=True)
