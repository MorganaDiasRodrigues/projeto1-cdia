import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import json

# Load the json data
with open('../trends-data/date_time_trends.json', 'r') as file:
    data = json.load(file)
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(id='buttons-date'),
    html.Div(id='buttons-hour'),
    html.Div(id='output')
])

@app.callback(
    Output('buttons-date', 'children'),
    [Input('buttons-date', 'n_clicks')]
)
def set_date_buttons(n):
    return [html.Button(date, id={'type': 'date-button', 'index': date}) for date in data.keys()]

@app.callback(
    Output('buttons-hour', 'children'),
    [Input({'type': 'date-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State({'type': 'date-button', 'index': dash.dependencies.ALL}, 'id')]
)
def set_hour_buttons(n, ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        selected_date = json.loads(button_id.replace("'", "\""))['index']
        return [html.Button(hour, id={'type': 'hour-button', 'index': hour}) for hour in data.get(selected_date, {})]

@app.callback(
    Output('output', 'children'),
    [Input({'type': 'hour-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State({'type': 'hour-button', 'index': dash.dependencies.ALL}, 'id'),
     State({'type': 'date-button', 'index': dash.dependencies.ALL}, 'id')]
)
def update_output(n, hour_ids, date_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        selected_hour = json.loads(button_id.replace("'", "\""))['index']
        selected_date = [i['index'] for i in date_ids if i['index'] in data and selected_hour in data[i['index']]][0]
        if selected_date is not None and selected_hour is not None:
            trending_topics = data[selected_date][selected_hour]
            return html.Ul([html.Li(topic) for topic in trending_topics])

if __name__ == '__main__':
    app.run_server(debug=True)
