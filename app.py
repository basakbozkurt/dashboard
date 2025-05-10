
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# === Load preprocessed CSV ===
df = pd.read_csv("missingness_by_rank.csv")
df["rank_bin"] = df["rank_bin"].astype(str)

# === Initialize Dash app ===
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Missing Category Dashboard"

app.layout = dbc.Container([
    html.H2("Missing Category Labels by App Rank"),
    html.P("Explore how the share of apps with unknown category classification varies by rank group, year, and country."),

    dbc.Row([
        dbc.Col([
            html.Label("Select Year(s):"),
            dcc.Dropdown(
                options=[{"label": str(y), "value": y} for y in sorted(df["year"].unique())],
                value=[df["year"].max()],
                multi=True,
                id="year-dropdown"
            )
        ], width=6),

        dbc.Col([
            html.Label("Select Country(ies):"),
            dcc.Dropdown(
                options=[{"label": c, "value": c} for c in sorted(df["country"].unique())],
                value=[df["country"].unique()[0]],
                multi=True,
                id="country-dropdown"
            )
        ], width=6)
    ], className="mb-3"),

    dcc.Graph(id="missingness-graph")
], fluid=True)


@app.callback(
    Output("missingness-graph", "figure"),
    Input("year-dropdown", "value"),
    Input("country-dropdown", "value")
)
def update_graph(selected_years, selected_countries):
    filtered = df[
        df["year"].isin(selected_years) &
        df["country"].isin(selected_countries)
    ]

    fig = px.bar(
        filtered,
        x="rank_bin",
        y="unknown_ratio",
        color="year",
        barmode="group",
        labels={
            "rank_bin": "App Rank (Grouped by 10)",
            "unknown_ratio": "Unknown Classification (%)"
        },
        title="Proportion of Unknown Category Apps by Rank Group"
    )
    fig.update_yaxes(ticksuffix="%")
    fig.update_layout(xaxis_tickangle=-45)

    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
