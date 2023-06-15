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

with open('../trends-data/ner_persons.json', 'r') as f:  # Change to the actual path of your JSON file
    trends_people_dict = json.load(f)

available_dates = list(date_time_trends.keys())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, assets_folder='assets')

def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return f'data:image/png;base64,{encoded.decode()}'

# Define the app layout
app.layout = html.Div([
    html.Div(id='date-buttons-container', children=[
        html.Button(date, id={'type': 'date-button', 'index': i}, n_clicks=0, className='date-button') for i, date in enumerate(available_dates)
    ]),
    html.Div(id='time-buttons'),
    html.Div(id='graph'),
    html.Div(id='trend-detail'),  # Added trend-detail id
    html.Div("Please select a date to start", id='date-message', style={'margin': '10px 0'}),
    html.Div(id='time-message', style={'margin': '10px 0'}),
    html.Div(id='trend-message', style={'margin': '10px 0'}),
])

@app.callback(
    Output('time-buttons', 'children'),
    Output('date-message', 'style'),
    Output('date-message', 'children'),
    Input({'type': 'date-button', 'index': ALL}, 'n_clicks'),
    State({'type': 'date-button', 'index': ALL}, 'children'),
    prevent_initial_call=True
)
def update_time_buttons(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, {'margin': '10px 0'}, "Please select a date to start"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_info = json.loads(button_id)
        selected_date = labels[button_info['index']]

        available_times = list(date_time_trends[selected_date].keys())

        time_buttons = [html.Button(time, id={'type': 'time-button', 'index': i, 'date': selected_date}, n_clicks=0) for i, time in
                enumerate(available_times)]

        date_message_style = {'display': 'none'}  # Hide the message

        return time_buttons, date_message_style, ""

@app.callback(
    Output('graph', 'children'),
    Output('time-message', 'style'),
    Output('time-message', 'children'),
    Input({'type': 'time-button', 'index': ALL, 'date': ALL}, 'n_clicks'),
    State({'type': 'time-button', 'index': ALL, 'date': ALL}, 'children'),
    prevent_initial_call=True
)
def update_figure(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, {'margin': '10px 0'}, "Please select a time"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_info = json.loads(button_id)
        selected_time = labels[button_info['index']]
        selected_date = button_info['date']

        trends = date_time_trends[selected_date][selected_time]

        ordered_list = html.Ol([html.Li(html.A(trend, id={'type': 'trend-link', 'index': i, 'date': selected_date}, href='#', style={'font-family': 'Arial, Helvetica, sans-serif'}))
                                for i, trend in enumerate(trends)])

        time_message_style = {'display': 'none'}  # Hide the message

        return ordered_list, time_message_style, ""

@app.callback(
    [Output({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'style'),
     Output('trend-detail', 'children'),
     Output('trend-message', 'style'),
     Output('trend-message', 'children')],
    [Input({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'n_clicks')],
    [State({'type': 'trend-link', 'index': ALL, 'date': ALL}, 'children')],
    prevent_initial_call=True
)
def update_trend_detail(n_clicks, labels):
    ctx = dash.callback_context
    if not ctx.triggered:
        return [{}]*len(n_clicks), dash.no_update, {'margin': '10px 0'}, "Select a trend to see the color palette"
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_info = json.loads(button_id)
        selected_index = button_info['index']
        selected_date = button_info['date']
        selected_trend = labels[selected_index]
        selected_trend_no_hash = selected_trend.lstrip('#')  # Strip the '#' from the trend name

        trend_link_styles = [{'color': 'pink'} if idx == selected_index else {} for idx in range(len(n_clicks))]

        if selected_trend_no_hash in images_dict:  # Use the no hash trend name for images_dict
            images = images_dict[selected_trend_no_hash]['images']

            rows = []
            for i in range(0, len(images), 3):
                row_images = []
                row_charts = []
                for j in range(i, min(i + 3, len(images))):
                    image = images[j]
                    colors = image['dominant_colors']
                    color_names = list(colors.keys())
                    color_percentages = [round(value * 100, 2) for value in colors.values()]

                    pie_chart = dcc.Graph(
                        figure=go.Figure(data=[go.Pie(
                            labels=color_names,
                            values=color_percentages,  # Add the color percentages
                            hoverinfo='label+percent',  # Show the label and percentage on hover
                            textinfo='none',
                            hole=0.3,
                            marker=dict(colors=color_names, line=dict(color='#FFFFFF', width=1))
                        )]),
                        config={'displayModeBar': False}  # Hide the mode bar
                    )

                    image_col = dbc.Col(html.Img(src=encode_image(image['path']), style={'maxHeight': '350px', 'width': 'auto'}))
                    chart_col = dbc.Col(html.Div(pie_chart), style={'textAlign': 'center', 'margin': '0 auto', 'font-size': '14px'})

                    row_images.append(image_col)
                    row_charts.append(chart_col)

                row = dbc.Row(row_images)
                rows.append(row)
                row = dbc.Row(row_charts)
                rows.append(row)
            
            # Show the associated person name if it exists in ner_persons.json
            if selected_trend in trends_people_dict:  # Use the trend name with hash for trends_people_dict
                rows.append(html.P(f"Most mentioned person: {trends_people_dict[selected_trend]}"))
            
            trend_message_style = {'display': 'none'}  # Hide the message

            return trend_link_styles, dbc.Container(rows), trend_message_style, ""
        else:
            return trend_link_styles, html.P("There is no image saved for this trend"), {'margin': '10px 0'}, ""


if __name__ == '__main__':
    app.run_server(debug=True)