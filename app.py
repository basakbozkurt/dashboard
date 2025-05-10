
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# === Load preprocessed CSV ===
df = pd.read_csv("missingness_by_rank.csv")
df["year"] = df["year"].astype(int)
df["rank_bin"] = df["rank_bin"].astype(str)
df["country"] = df["country"].str.lower()

# === Initialize Dash app ===
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Missing Category Dashboard"

# === Layout ===
app.layout = dbc.Container([
    html.H2("Missing Category Labels by App Rank", className="mt-3"),
    html.P("Explore how the share of apps with unknown category classification varies by rank group, year, and country."),

    dbc.Row([
        dbc.Col([
            html.Label("Select App Type:", className="small"),
            dcc.Dropdown(
                options=[
                    {"label": "Free", "value": "Free"},
                    {"label": "Paid", "value": "Paid"}
                ],
                value="Free",
                multi=False,
                id="type-dropdown",
                style={"fontSize": "13px"}
            )
        ], width=4),

        dbc.Col([
            html.Label("Select Year(s):", className="small"),
            dcc.Dropdown(
                options=[{"label": str(y), "value": y} for y in sorted(df["year"].unique())],
                value=[df["year"].max()],
                multi=True,
                id="year-dropdown",
                style={"fontSize": "13px"}
            )
        ], width=4),

        dbc.Col([
            html.Label("Select Country(ies):", className="small"),
            dcc.Dropdown(
                options=[{"label": c.upper(), "value": c} for c in sorted(df["country"].unique())],
                value=[df["country"].unique()[0]],
                multi=True,
                id="country-dropdown",
                style={"fontSize": "13px"}
            )
        ], width=4)
    ], className="mb-3"),

    dcc.Graph(id="missingness-graph")
], fluid=True)


# === Callback ===
@app.callback(
    Output("missingness-graph", "figure"),
    Input("type-dropdown", "value"),
    Input("year-dropdown", "value"),
    Input("country-dropdown", "value")
)
def update_graph(selected_type, selected_years, selected_countries):
    filtered = df[
        (df["app_type"] == selected_type) &
        (df["year"].isin(selected_years)) &
        (df["country"].isin(selected_countries))
    ].copy()

    filtered["year"] = filtered["year"].astype(str)

    fig = px.bar(
        filtered,
        x="rank_bin",
        y="unknown_ratio",
        color="year",
        barmode="group",
        hover_data=["country", "year", "unknown_ratio"],
        labels={
            "rank_bin": "App Rank (Grouped by 10)",
            "unknown_ratio": "Unknown Classification (%)",
            "year": "Year",
            "country": "Country"
        },
        title="Unknown Classification by Rank Group and Year"
    )

    fig.update_yaxes(ticksuffix="%")
    fig.update_layout(xaxis_tickangle=-45)

    return fig


# === Run App ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
