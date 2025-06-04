import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import dash
from dash import callback
# === Initialize Dash App ===

# === Load Data ===
data_dir = os.path.join(os.path.dirname(__file__), "../data")
daily_file = os.path.join(data_dir, "global_borda_daily.csv")
monthly_file = os.path.join(data_dir, "global_borda_monthly.csv")

daily_df = pd.read_csv(daily_file)
monthly_df = pd.read_csv(monthly_file)

daily_df["date"] = pd.to_datetime(daily_df["date"])
monthly_df["month"] = pd.to_datetime(monthly_df["month"])

daily_df["year"] = daily_df["date"].dt.year
monthly_df["year"] = monthly_df["month"].dt.year

# === Initialize App ===
dash.register_page(__name__ , path="/rq1",
                    name="RQ1: Global App Category Trends Over Time",
                    order=1)

# === Layout ===
layout = dbc.Container([
    html.H2("🌍 Global App Category Trends Over Time", className="my-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Granularity"),
            dcc.Dropdown(
                id="granularity-dropdown",
                options=[
                    {"label": "Daily", "value": "daily"},
                    {"label": "Monthly", "value": "monthly"},
                ],
                value="monthly",
                clearable=False
            )
        ], width=3),

        dbc.Col([
            html.Label("Select App Type"),
            dcc.Dropdown(
                id="app-type-dropdown",
                options=[{"label": t, "value": t} for t in sorted(daily_df['app_type'].unique())],
                value="Free",
                clearable=False
            )
        ], width=3),

        dbc.Col([
            html.Label("Select Year(s)"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(daily_df['year'].unique())],
                value=[2022],
                multi=True
            )
        ], width=6),
    ], className="mb-4"),
            html.P(
            "This graph shows the relative ranking of educational app categories over time, based on normalised Borda scores aggregated across countries.",
            className="text-muted"
            ),
    dcc.Graph(id="global-trend-graph")
])


# === Callback ===
@callback(
    Output("global-trend-graph", "figure"),
    Input("granularity-dropdown", "value"),
    Input("app-type-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_graph(granularity, app_type, selected_years):
    if not selected_years:
        return px.line(title="⚠️ Please select a year.")

    if not isinstance(selected_years, list):
        selected_years = [selected_years]

    df = daily_df if granularity == "daily" else monthly_df
    time_col = "date" if granularity == "daily" else "month"

    dff = df[
        (df["app_type"] == app_type) &
        (df["year"].isin(selected_years)) &
        (df["classification"] != "Unknown")
    ].copy()

    dff["time"] = dff[time_col]

    agg = dff.groupby(["time", "classification"])["score_borda"].sum().reset_index()
    agg["relative_score"] = agg.groupby("time")["score_borda"].transform(lambda x: x / x.sum()) * 100

    fig = px.line(
        agg,
        x="time",
        y="relative_score",
        color="classification",
        labels={"relative_score": "Relative Borda Share (%)", "time": granularity.capitalize()},
        title=f"Global Category Trends ({granularity.capitalize()})"
    )
    fig.update_layout(height=600, legend_title="Category")
    fig.update_yaxes(ticksuffix="%")
    return fig
