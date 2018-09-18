import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.figure_factory as ff
import json
from model import Model

app = dash.Dash()
model = Model()
model.parseModel(10, 100, 100, isV=True)
rx_pos = model.get_rx_positions()
axis_list = [
    'Time (microsecond)',
    'dBx/dt (V)',
    'dBz/dt (V)',
    'Bx (nT)',
    'Bz (nT)'
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
        html.Div(
            dcc.Graph(id='quiver',
            style={'height': '1000px', 'width': '100%','display': 'inline-block'}
            )
        ),
        html.Div(
            dcc.Slider(
                id='rx_positions',
                min=0,
                max=len(rx_pos),
                value=0,
                step=None,
                marks={str(i): str(rx_pos[i]) for i in range(0, len(rx_pos))}
            ), 
        style={'height': '50px', 'width': '100%','display': 'inline-block'}
        )
    ]),

    html.Div([
        html.Div(
            dcc.Slider(
                id='h1',
                min=10,  #h1 = 10:5:70
                max=70,
                value=10,
                step=5,
                marks={str(h): str(h) for h in range(10, 70, 5)}
            ), 
        style={'height': '50px', 'width': '100%','display': 'inline-block'}
        ),

        html.Div(
            dcc.Slider(
                id='rho1',
                min=20,  #rho1 = 2:0.2:4.4
                max=46,
                value=20,
                step=2,
                marks={str(e): '{:6.0f}'.format(10**(e*0.1)) for e in range(20, 46, 2)}
            ),
        style={'height': '50px', 'width': '100%','display': 'inline-block'}
        ),
        html.Div(
            dcc.Slider(
                id='rho2',
                min=20,  #rho2 = 2:0.2:4.4
                max=46,
                value=20,
                step=2,
                marks={str(e): '{:6.0f}'.format(10**(e*0.1)) for e in range(20, 46, 2)}
            ),
        style={'height': '50px', 'width': '100%','display': 'inline-block'}
        )
    ],style={'width': '50%', 'display': 'inline-block'}),

    html.Div(id = 'modelHasChanged', style={'display': 'none'})
])

@app.callback(
    dash.dependencies.Output('graph', 'children'),
    [dash.dependencies.Input('rx_positions', 'value'),
    dash.dependencies.Input('xaxis-type', 'value'),
    dash.dependencies.Input('yaxis-type', 'value'),
    dash.dependencies.Input('xaxis-column', 'value'),
    dash.dependencies.Input('yaxis-column', 'value'),
    dash.dependencies.Input('modelHasChanged', 'children')]
    )
def update_graph(rx_pos_index, xaxis_type, yaxis_type, xaxis_col_val, yaxis_col_val, Output_dict):
    Output_dict_dser = json.loads(Output_dict)
    rx_pos_label = rx_pos[rx_pos_index]
    xisT = xaxis_col_val == axis_list[0]
    yisT = yaxis_col_val == axis_list[0]
    
    if yaxis_col_val != xaxis_col_val:
        dfy = pd.read_json(Output_dict_dser[yaxis_col_val], orient='split')
        dfx = pd.read_json(Output_dict_dser[xaxis_col_val], orient='split')
        dffy = dfy['time_us'] if yisT else dfy[dfy.columns[rx_pos_index]]
        dffx = dfx['time_us'] if xisT else dfx[dfx.columns[rx_pos_index]]
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

@app.callback(
    dash.dependencies.Output('quiver', 'figure'),
    [dash.dependencies.Input('modelHasChanged', 'children')]
)
def update_quiver(Output_dict):
    Output_dict_dser = json.loads(Output_dict)
    dft = pd.read_json(Output_dict_dser[axis_list[0]], orient='split')['time_us']
    dfx = pd.read_json(Output_dict_dser[axis_list[3]], orient='split')
    dfy = pd.read_json(Output_dict_dser[axis_list[4]], orient='split')

    xx = np.array([float(pos) for pos in rx_pos])
    yy = np.log(dft.values)
    x, y = np.meshgrid(xx, yy)
    scale = 1e3
    u = dfx.values 
    #u = u * scale
    #u = np.sign(u) * np.log(np.abs(u))
    v = dfy.values 
    #v = v * scale
    #v = np.sign(v) * np.log(np.abs(v))

    norm = (u ** 2 + v ** 2) * 0.5
    norm = np.log(norm)
    angle = np.arctan(v/u)
    u = norm * np.cos(angle)
    v = norm * np.sin(angle)

    fig = ff.create_quiver(x, y, u, v,
                        scale=1,
                        line=dict(width=1))
    return fig

@app.callback(
    dash.dependencies.Output('modelHasChanged', 'children'),
    [dash.dependencies.Input('h1', 'value'),
    dash.dependencies.Input('rho1', 'value'),
    dash.dependencies.Input('rho2', 'value'),]
    )
def update_model(h1, rho1, rho2):
    h1 = str(h1)
    rho1 = 10**(rho1*0.1)
    rho1 = '{:.0f}'.format(rho1) if rho1 % 100 == 0 else '{:6.4f}'.format(rho1)
    rho2 = 10**(rho2*0.1) 
    rho2 = '{:.0f}'.format(rho2) if rho2 % 100 == 0 else '{:6.4f}'.format(rho2)
    
    model.parseModel(h1, rho1, rho2, isV=True)
    time = model.get_timegates()
    rx_pos = model.get_rx_positions()
    sndgs_x = model.get_X_soundings()
    sndgs_z = model.get_Z_soundings()
    model.parseModel(h1, rho1, rho2, isV=False)
    sndgs_Bx = model.get_X_soundings()
    sndgs_Bz = model.get_Z_soundings()
    Output_dict= {
        axis_list[0]: time.to_json(orient='split', date_format='iso'),
        axis_list[1]: sndgs_x.to_json(orient='split', date_format='iso'),
        axis_list[2]: sndgs_z.to_json(orient='split', date_format='iso'),
        axis_list[3]: sndgs_Bx.to_json(orient='split', date_format='iso'),
        axis_list[4]: sndgs_Bz.to_json(orient='split', date_format='iso')
    }
    return json.dumps(Output_dict)

@app.callback(
    dash.dependencies.Output('yaxis-type', 'value'),
    [dash.dependencies.Input('yaxis-column', 'value'),
    dash.dependencies.Input('xaxis-column', 'value')]
    )
def force_linear_yaxis_type(yaxis_col_val, xaxis_col_val):
    if (xaxis_col_val != axis_list[0]) and (yaxis_col_val != axis_list[0]):
        return 'Linear'
    else:
        return 'Log'

@app.callback(
    dash.dependencies.Output('xaxis-type', 'value'),
    [dash.dependencies.Input('yaxis-column', 'value'),
    dash.dependencies.Input('xaxis-column', 'value')]
    )
def force_linear_xaxis_type(yaxis_col_val, xaxis_col_val):
    if (xaxis_col_val != axis_list[0]) and (yaxis_col_val != axis_list[0]):
        return 'Linear'
    else:
        return 'Log'


if __name__ == '__main__':
    app.run_server()