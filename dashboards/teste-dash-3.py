import base64
import json
from collections import Counter
from io import BytesIO
import time
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State, MATCH, ALL
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Load JSON data
with open('../trends-data/date_time_trends.json', 'r') as f:
    date_time_trends = json.load(f)

with open('../trends-data/trends_images.json', 'r') as f:
    images_dict = json.load(f)

available_dates = list(date_time_trends.keys())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return f'data:image/png;base64,{encoded.decode()}'

# Define the app layout
app.layout = html.Div([
    html.Div([
        html.Button(date, id={'type': 'date-button', 'index': i}, n_clicks=0) for i, date in enumerate(available_dates)
    ], id='date-buttons'),
    html.Div(id='time-buttons'),
    html.Div(id='graph'),
    html.Div("Select a trend name to see its color", id='trend-detail', style={'margin': '10px 0'}),
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

        ordered_list = html.Ol([html.Li(html.A(trend, id={'type': 'trend-link', 'index': i, 'date': selected_date}, href='#', style={'font-family': 'Arial, Helvetica, sans-serif'}))
                                for i, trend in enumerate(trends)])

        return ordered_list

@app.callback(
    Output('trend-detail', 'children'),
    Input({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'n_clicks'),
    State({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'children'),
    prevent_initial_call=True
)
def update_trend_detail(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_info = json.loads(button_id)
        selected_index = button_info['index']
        selected_date = button_info['date']
        selected_trend = labels[selected_index].strip("#")

        if selected_trend in images_dict:
            images = images_dict[selected_trend]['images']

            rows = []
            for i in range(0, len(images), 3):
                row_images = []
                row_charts = []
                for j in range(i, min(i + 3, len(images))):
                    image = images[j]
                    colors = image['dominant_colors']
                    color_names = list(colors.keys())
                    color_values = list(colors.values())

                    pie_chart = dcc.Graph(
                        figure=go.Figure(data=[go.Pie(labels=color_names, values=color_values, hole=0.3)]),
                        config={'displayModeBar': False}  # Hide the mode bar
                    )

                    image_col = dbc.Col(html.Img(src=encode_image(image['path']), height=400))
                    chart_col = dbc.Col([
                        dbc.Row(html.Div(pie_chart))
                    ], style={'textAlign': 'center'})

                    row_images.append(image_col)
                    row_charts.append(chart_col)

                row = dbc.Row(row_images)
                rows.append(row)
                row = dbc.Row(row_charts)
                rows.append(row)

            return dbc.Container(rows)
        else:
            return html.P("There is no image saved for this trend")

if __name__ == '__main__':
    app.run_server(debug=True)