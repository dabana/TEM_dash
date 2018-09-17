import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from model import Model

app = dash.Dash()
model = Model()
model.parseModel(10, 100, 100, isV=True)

sndgs_x = model.get_X_soundings()
sndgs_Z = model.get_Z_soundings()
rx_pos = model.get_rx_positions()
inloop = model.get_inloop_sounding()
time = model.get_timegates()

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''


app.layout = html.Div([
    html.Div(id = 'graph'),

    dcc.Slider(
        id='rx_positions',
        min=0,
        max=len(rx_pos),
        value=0,
        step=None,
        marks={str(i): str(rx_pos[i]) for i in range(0, len(rx_pos))}
    )
])

@app.callback(
    dash.dependencies.Output('graph', 'children'),
    [dash.dependencies.Input('rx_positions', 'value')]
    )
def update_graph(rx_pos_index):
    label = rx_pos[rx_pos_index]
    print("THIS IS LABEL: " + label)
    df = sndgs_x
    dff = df[df.columns[rx_pos_index]]

    return dcc.Graph(
        id='soundings',
        figure={
            'data': [
                go.Scatter(
                    x=time,
                    y=np.abs(dff),
                    text=np.abs(dff),
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=label
                )
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Time (microseconds)'},
                yaxis={'type': 'log', 'title': 'Voltage (V)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )


if __name__ == '__main__':
    app.run_server()