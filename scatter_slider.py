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
rx_pos = model.get_rx_positions()
time = model.get_timegates()

sndgs_x = model.get_X_soundings()
sndgs_z = model.get_Z_soundings()

model.parseModel(10, 100, 100, isV=False)
sndgs_Bx = model.get_X_soundings()
sndgs_Bz = model.get_Z_soundings()

axis_list = [
    'Time (microsecond)',
    'dBx/dt (V)',
    'dBz/dt (V)',
    'Bx (nT)',
    'Bz (nT)'
]

Output_dict= {
    axis_list[0]: time,
    axis_list[1]: sndgs_x, 
    axis_list[2]: sndgs_z,
    axis_list[3]: sndgs_Bx,
    axis_list[4]: sndgs_Bz
}



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
            options=[{'label': i, 'value': i} for i in axis_list],
            value=axis_list[0]
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
            options=[{'label': i, 'value': i} for i in axis_list],
            value=axis_list[1]
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
    dash.dependencies.Input('yaxis-type', 'value'),
    dash.dependencies.Input('xaxis-column', 'value'),
    dash.dependencies.Input('yaxis-column', 'value')]
    )
def update_graph(rx_pos_index, xaxis_type, yaxis_type, xaxis_col_val, yaxis_col_val):

    rx_pos_label = rx_pos[rx_pos_index]
    xisT = xaxis_col_val == axis_list[0]
    yisT = yaxis_col_val == axis_list[0]
    if yaxis_col_val != xaxis_col_val:
        dfy = Output_dict[yaxis_col_val]
        dfx = Output_dict[xaxis_col_val]
        dffy = dfy if yisT else dfy[dfy.columns[rx_pos_index]]
        dffx = dfx if xisT else dfx[dfx.columns[rx_pos_index]]
        return dcc.Graph(
            id='soundings',
            figure={
                'data': [
                    go.Scatter(
                        x= np.abs(dffx) if xaxis_type == 'Log' else dffx,
                        y= np.abs(dffy) if yaxis_type == 'Log' else dffy,
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 15,
                            'line': {'width': 0.5, 'color': 'white'},
                            'color': ['red' if i < 0 else 'blue' for i in dffy]
                        }
                    )
                ],
                'layout': go.Layout(
                    xaxis={'type': 'linear' if xaxis_type == 'Linear' else 'log', 'title': xaxis_col_val},
                    yaxis={'type': 'linear' if yaxis_type == 'Linear' else 'log', 'title': yaxis_col_val},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }
        )


if __name__ == '__main__':
    app.run_server()