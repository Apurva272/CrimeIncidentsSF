import numpy as np
import pandas as pd
import scipy.stats as st
import plotly.graph_objects as go
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


#accessing dateset stored on github
filepath = "https://raw.githubusercontent.com/dannygarcia193/dashPoliceIncidents/master/is2017Grouped.csv"
incidents2017 = pd.read_csv(filepath)

# San Francisco Neighborhoods
toMap = requests.get(
    "https://data.sfgov.org/api/geospatial/pty2-tcw4?method=export&format=GeoJSON").json()

# retrive the names of the neighborhoods and their respective index
maps = {x+1: toMap['features'][x]['properties']['name']
        for x in range(len(toMap['features']))}

# 2017 incidents grouped by neighborhoods (total count of incidents an most common incident
grouped2017 = incidents2017.groupby(
    'neighborhood').agg(
    {'incidentCount': "count", 'mostCommonIncident': lambda x: st.mode(x)[0][0]}).reset_index()

# defining the layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets)
server = app.server # isn't needed when not using Heroku
#element
app.layout = html.Div(children=[

        # creating a header with an HTML tag
    html.H1(children='Police Incidents 2017'),

    # selecting the most common incident
    html.Label('Most Common Incident Filter:'),
    dcc.Dropdown(
        options = [{'label': x, 'value': x} for x in grouped2017['mostCommonIncident'].unique()],

        value = grouped2017['mostCommonIncident'].unique().tolist(),
        multi = True,
        id = 'incident_selector'
    ),
    dcc.Graph(
        id='launches_by_year',style={"height" :'100vh', "width" : "100%"}),
])


@app.callback(
    [Output('launches_by_year', 'figure'),
     ],
    [Input('incident_selector', 'value'),
     ])
def update_figures(selected_incident):
    filtered_data = grouped2017.query('mostCommonIncident in @selected_incident')

    return (
        {
            'data': [go.Choroplethmapbox(geojson=toMap, locations=filtered_data['neighborhood'], z=filtered_data['incidentCount'],
                                                featureidkey="properties.name",  colorscale="Viridis",
                                                marker_opacity=0.5, marker_line_width=0.2)],
            'layout': go.Layout(mapbox_style="carto-positron",mapbox_zoom=10.5, mapbox_center = {"lat": 37.7749, "lon": -122.4194})
        },
    )


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run_server(debug=True)