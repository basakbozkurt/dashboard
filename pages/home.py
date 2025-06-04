import dash
from dash import html

dash.register_page(__name__, path='/', order=0,
                    name="Home")

layout = html.Div([
    html.H1('Welcome to the App Category Dashboard', style={'textAlign': 'center'}),
    html.P('This interactive dashboard supports the exploration of educational app trends across global marketplaces.'),
    html.P('Navigate through the dashboard to access visualizations and analyses focused on app type, ranking position and category composition.'),
])