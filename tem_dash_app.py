import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.figure_factory as ff
import json
from myquiver import create_quiver
from model import Model

app = dash.Dash() # Instentiate a Dash app
model = Model() # Instentiate a TEM model


model.parseModel(10, 100, 100, isV=True)
rx_pos = model.get_rx_positions()
axis_list = [
    'Time (microsecond)',
    'dBx/dt (V)',
    'dBz/dt (V)',
    'Bx (nT)',
    'Bz (nT)',
    'Btotal (nT)'
]

# Just an exemple of markdown text
markdown_text = '''
### Dash and Markdown

This is a plot.
'''

# Layout of the application
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
        html.Div(
            dcc.Graph(id = 'soundings'),
            id = 'graph', 
            style={'width': '98%', 'float': 'right', 'display': 'inline-block'}
        ),
        html.Div(
            dcc.Graph(id = 'quiver_plot'),
            id='quiver',
            style={'width': '98%','display': 'inline-block'}
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


# Updates the graph when axis columns or axis types or model data change. 
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


# Updates the quiver plot when model data changes
@app.callback(
    dash.dependencies.Output('quiver', 'children'),
    [dash.dependencies.Input('modelHasChanged', 'children')]
)
def update_quiver(Output_dict):
    # Parse the output data dictonary
    Output_dict_dser = json.loads(Output_dict) 
    dft = pd.read_json(# time
        Output_dict_dser[axis_list[0]], orient='split') 
    dfBx = pd.read_json(# x-compnent of B-field 
        Output_dict_dser[axis_list[3]], orient='split')
    dfBz = pd.read_json(# z-component of B-field
        Output_dict_dser[axis_list[4]], orient='split')
    dfn = pd.read_json(# Norm of the B-field (intensity)
        Output_dict_dser[axis_list[5]], orient='split')

    # Generate the grid on which arrows are plotted
    #selected_idx = range(0, len(dft.index), 10) #sub-sample the time
    selected_idx = range(0, len(dft.index), 10)
    xx = np.array([float(pos) for pos in rx_pos])
    yy = dft.iloc[selected_idx].values  
    x, y = np.meshgrid(xx, yy)

    # Scale the arrow lengths for plotting
    norm = dfn.iloc[selected_idx].values
    norm_sc = norm / np.amin(norm)
    norm = np.sign(norm) * np.log(np.abs(norm_sc))

    # Compute the u and v vectors defining each arrow
    u = dfBx.iloc[selected_idx].values 
    v = dfBz.iloc[selected_idx].values
    angle = np.arctan(v/u)
    u = norm * np.cos(angle)
    v = norm * np.sin(angle)

    # Create B-field quiver plot
    fig = create_quiver(x, y, u, v, 
                        scale = 1,
                        scaleratio = 1.25,
                        name='B-field in X-Z plane')

    # Compute the zero-crossing move-out (ZCMO) of Bz
    # ZCMO: Time at which Bz changes sign for each rx positions
    Bz = dfBz.values
    t = dft.values
    range_rx_pos = range(0, len(rx_pos))
    signflip = np.array(np.sign(Bz[:-2, :]) * np.sign(Bz[2:, :]))
    signflip = np.append(np.ones((1, len(rx_pos))), signflip, 0)

    # Linear interpolation of the zero-crossing time    
    i_maxneg = np.argmin(signflip, 0)
    i_minpos = np.array(i_maxneg)
    for i in range_rx_pos:
        if Bz[i_maxneg[i], i] < 0:
            i_minpos[i] = i_maxneg[i] + 1
        else:
            i_minpos[i] = 0
    Bz_maxneg = np.array([Bz[i_maxneg[i], i] for i in range_rx_pos])
    Bz_minpos = np.array([Bz[i_minpos[i], i] for i in range_rx_pos])
    delta_Bz = Bz_minpos - Bz_maxneg
    delta_t = t[i_minpos].flatten() - t[i_maxneg].flatten()
    slope = delta_Bz / delta_t
    zcmo = t[i_maxneg].flatten() - Bz_maxneg / slope

    # Create ZCMO scatter plot
    zcmo_scat = go.Scatter(x=xx, y=zcmo,
                        mode='markers',
                        marker=dict(size=12),
                        name='Bz zero-crossing')

    # Add ZCMO points to the quiver plot
    fig.add_trace(zcmo_scat)

    # Specify additionnal options to the figure layout
    fig.layout.xaxis['title'] = 'Spacing (m)'
    fig.layout.yaxis['title'] = 'Time (us)'
    fig.layout.yaxis['autorange'] = 'reversed'

    # Return the figure as a Graph
    return dcc.Graph(id = 'quiver_plot', figure = fig)


# Updates the rx position slider when points are clicked in 
# the quiver plot.
@app.callback(
    dash.dependencies.Output('rx_positions', 'value'),
    [dash.dependencies.Input('quiver_plot', 'clickData')]
)
def update_slider_from_quiver(click_data):
    # `click_data` contains the data of the point that has been clicked
    if click_data is None:
        return 0
    else:
        # Return the index of the element in rx_pos which is closest
        # to the x coordinate of the point that has been clicked
        v = click_data['points'][0]['x']
        a = [float(i) for i in rx_pos]
        closest_i = np.searchsorted(a, v)
        return closest_i


# Updates the data when model sliders are moves
@app.callback(
    dash.dependencies.Output('modelHasChanged', 'children'),
    [dash.dependencies.Input('h1', 'value'),
    dash.dependencies.Input('rho1', 'value'),
    dash.dependencies.Input('rho2', 'value'),]
    )
def update_model(h1, rho1, rho2):

    # Parse modelized data for a specific resistivity model
    h1 = str(h1)
    rho1 = 10**(rho1*0.1)
    rho1 = '{:.0f}'.format(rho1) if rho1 % 100 == 0 else '{:6.4f}'.format(rho1)
    rho2 = 10**(rho2*0.1) 
    rho2 = '{:.0f}'.format(rho2) if rho2 % 100 == 0 else '{:6.4f}'.format(rho2)
    model.parseModel(h1, rho1, rho2, isV=False)

    # Retrieve indenpendent variables
    time = model.get_timegates()
    rx_pos = model.get_rx_positions()

    # Retrieve modelized data for dB-field
    sndgs_x = model.get_X_soundings()
    sndgs_z = model.get_Z_soundings()

    # Retrieve modelized data for B-field (reparse modelized data)
    model.parseModel(h1, rho1, rho2, isV=False)
    sndgs_Bx = model.get_X_soundings()
    sndgs_Bz = model.get_Z_soundings()

    # Compute the norm of the B-field
    norm_B = sndgs_Bx.pow(2).values
    norm_B2 = sndgs_Bz.pow(2).values
    norm_B += norm_B2
    norm_B = pd.DataFrame(norm_B ** 0.5)

    # Return the output data dictonary
    Output_dict= {
        axis_list[0]: time.to_json(orient='split', date_format='iso'),
        axis_list[1]: sndgs_x.to_json(orient='split', date_format='iso'),
        axis_list[2]: sndgs_z.to_json(orient='split', date_format='iso'),
        axis_list[3]: sndgs_Bx.to_json(orient='split', date_format='iso'),
        axis_list[4]: sndgs_Bz.to_json(orient='split', date_format='iso'),
        axis_list[5]: norm_B.to_json(orient='split', date_format='iso')
    }
    return json.dumps(Output_dict)


# Changes the Y axis type to Linear when a z-x plane plot is displayed 
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


# Changes the X axis type to Linear when a z-x plane plot is displayed 
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