import dash
from dash import html

dash.register_page(__name__, path='/', order=0,
                    name="Home")

layout = html.Div([
    html.H1('Welcome to the App Category Dashboard', style={'textAlign': 'center'}),
    html.P('This dashboard provides insights into app category trends, missing data, and more.'),
    html.P('Use the navigation menu to explore different analyses and visualizations.'),
])