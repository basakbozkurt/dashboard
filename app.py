import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div([
    html.H1('Dashboard Navigation', style={'textAlign': 'center'}),
    html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        dcc.Link(
                            f"{page['name']}",
                            href=page["relative_path"],
                            style={
                                'textDecoration': 'none',
                                'color': '#007bff',
                                'fontWeight': 'bold',
                                'fontSize': '18px'
                            }
                        )
                    ),
                    style={
                        'margin': '10px',
                        'textAlign': 'center',
                        'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',
                        'transition': 'transform 0.2s, box-shadow 0.2s',
                        'border': '1px solid #ddd',
                        'borderRadius': '8px'
                    },
                    className="hover-card"
                )
            )  for page in dash.page_registry.values() if not page["path"] == '/'
        ])
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=False, port=8080)