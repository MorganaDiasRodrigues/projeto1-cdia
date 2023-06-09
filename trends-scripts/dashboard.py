import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import base64
import io
import cv2
import numpy as np
from sklearn.cluster import KMeans
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# function to convert RGB to HEX
def rgb2hex(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select an Image')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        accept='image/*'
    ),
    html.Div(id='output')
])

@app.callback(Output('output', 'children'),
              [Input('upload-image', 'contents')])
def update_output(contents):
    if contents is not None:
        # read and decode the uploaded image
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        nparr = np.fromstring(decoded, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # reshape the image to be a list of pixels
        pixels = image.reshape(-1, 3)

        # perform kmeans to find the most dominant colors
        kmeans = KMeans(n_clusters=5) # you can change the number of clusters to get more or less colors
        kmeans.fit(pixels)

        # get the RGB values of the cluster centers
        colors = kmeans.cluster_centers_

        # get the number of pixels in each cluster
        hist = np.histogram(kmeans.labels_, bins=np.arange(0, len(np.unique(kmeans.labels_)) + 1))

        # percentage of pixels in each cluster
        colors_percentage = hist[0] / sum(hist[0])

        # colors in hex format
        colors_hex = [rgb2hex(color) for color in colors]

        # create subplots
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'xy'}]])

        # add pie chart to subplot
        fig.add_trace(go.Pie(labels=colors_hex,
                             values=colors_percentage,
                             hole=.3,
                             sort=False,
                             marker=dict(colors=colors_hex,
                                         line=dict(color='#000000', width=1))),
                      row=1, col=1)

        # add rectangles with color codes to subplot
        fig.add_trace(go.Bar(x=[1]*len(colors_hex),
                             y=colors_percentage,
                             marker_color=colors_hex,
                             orientation='h',
                             text=colors_hex,
                             textposition='auto',
                             showlegend=False),
                      row=1, col=2)

        # formatting subplots
        fig.update_layout(height=600, width=800, title_text="Dominant Colors in the Uploaded Image")
        fig.update_yaxes(showticklabels=False)

        return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)
