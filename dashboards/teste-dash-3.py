import base64
import json
from collections import Counter
from io import BytesIO

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State, MATCH, ALL
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Load JSON data
with open('../trends-data/date_time_trends.json', 'r') as f:
    date_time_trends = json.load(f)

with open('trends_images.json', 'r') as f:
    images_dict = json.load(f)

available_dates = list(date_time_trends.keys())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return f'data:image/jpeg;base64,{encoded.decode()}'

# Define the app layout
app.layout = html.Div([
    html.Div([
        html.Button(date, id={'type': 'date-button', 'index': i}, n_clicks=0) for i, date in enumerate(available_dates)
    ], id='date-buttons'),
    html.Div(id='time-buttons'),
    html.Div(id='graph'),
    html.Div(id='trend-detail', children=html.Div(style={'height': '400px'}))  # added empty space
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

        available_times = list(date_time_trends[selected_date].keys())
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

        trends = date_time_trends[selected_date][selected_time]

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

        image_and_chart = []
        for i, img in enumerate(image_data):
            image_path = img['path']
            dominant_colors = img['dominant_colors']
            hex_codes = list(dominant_colors.keys())
            color_proportions = list(dominant_colors.values())
            encoded_image = encode_image(image_path)
            image = html.Img(src=encoded_image, style={'width': '200px', 'height': '200px'})

            fig = go.Figure(
                go.Pie(labels=hex_codes, values=color_proportions, name=f"Image {i+1}", hoverinfo='label', hole=.4, 
                       showlegend=False, pull=[0.2]*len(hex_codes))
            )

            fig.update_layout(
                autosize=True,
                margin=dict(t=10, b=10, l=10, r=10)
            )

            pie_chart = dcc.Graph(figure=fig)

            image_and_chart.append(html.Div([image, pie_chart], style={'display': 'inline-block', 'margin': '10px'}))

        return html.Div(image_and_chart, style={'display': 'flex', 'justify-content': 'space-around'})


if __name__ == '__main__':
    app.run_server(debug=True)