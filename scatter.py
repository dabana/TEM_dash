import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from model import Model

app = dash.Dash()
model = Model()
model.parseModel(10, 100, 100, isV=True)

df = model.soundings

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''


app.layout = html.Div([
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                go.Scatter(
                    x=df['time_us'],
                    y=df[lbl],
                    text=df[lbl],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=lbl
                )for lbl in df.columns
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Time (microseconds)'},
                yaxis={'type': 'log', 'title': 'Voltage (V)'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
    dcc.Markdown(children=markdown_text)
])




if __name__ == '__main__':
    app.run_server()