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

axis_list = [
    ('time (microsecond)', 't'),
    ('X component (V)', 'x'),
    ('Z component (V)', 'z')
]

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''


app.layout = html.Div([

    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label': i, 'value': j} for i, j in axis_list],
            value='time'
        ),
        dcc.RadioItems(
            id='xaxis-type',
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value='Log',
            labelStyle={'display': 'inline-block'}
        )
    ],style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='yaxis-column',
            options=[{'label': i, 'value': j} for i, j in axis_list],
            value='z'
        ),
        dcc.RadioItems(
            id='yaxis-type',
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value='Log',
            labelStyle={'display': 'inline-block'}
        )
    ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

    html.Div([
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
])

@app.callback(
    dash.dependencies.Output('graph', 'children'),
    [dash.dependencies.Input('rx_positions', 'value'),
    dash.dependencies.Input('xaxis-type', 'value'),
    dash.dependencies.Input('yaxis-type', 'value')]
    )
def update_graph(rx_pos_index, xaxis_type, yaxis_type):
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
                    y= np.abs(dff) if yaxis_type == 'Log' else dff,
                    text=np.abs(dff),
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'},
                        'color': ['red' if i < 0 else 'blue' for i in dff]
                    },
                    name=label
                )
            ],
            'layout': go.Layout(
                xaxis={'type': 'linear' if xaxis_type == 'Linear' else 'log', 'title': 'Time (microseconds)'},
                yaxis={'type': 'linear' if yaxis_type == 'Linear' else 'log', 'title': 'Voltage (V)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )


if __name__ == '__main__':
    app.run_server()