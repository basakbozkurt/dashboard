import pandas as pd
import os
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import dash



base_path = "data/by_country_year"  # adjust if needed

# === Helper: Load list of available countries and years from filenames ===
def get_available_files():
    files = os.listdir(base_path)
    entries = [f.replace(".csv", "").split("_") for f in files if f.endswith(".csv")]
    return sorted(set([e[0] for e in entries])), sorted(set(int(e[1]) for e in entries if len(e) == 2))

all_countries, all_years = get_available_files()

# === Initialize App ===
dash.register_page(__name__, path="/rq2",
                   name="RQ2: App Category Trends Over Time", order=2)

# === Layout ===
layout = dbc.Container([
    html.H2("📱 App Category Trends Over Time", className="my-3"),

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
            dcc.Dropdown(id="app-type-dropdown", clearable=False)  # dynamic
        ], width=2),

        dbc.Col([
            html.Label("Select Country"),
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c.upper(), "value": c} for c in all_countries],
                value=all_countries[0],
                clearable=False
            )
        ], width=2),

        dbc.Col([
            html.Label("Select Year(s)"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in all_years],
                value=[all_years[-1]],
                multi=True
            )
        ], width=3),
    ], className="mb-4"),
        html.P(
        "This line chart visualizes the temporal distribution of Borda scores across educational app categories.",
        "For each country and time point, category-level Borda scores are computed from national app rankings.",
        "The resulting relative shares capture each category’s prominence within the marketplace over time.",
        className="text-muted"),
    dcc.Graph(id="trend-graph")
])

# === Callback to update app-type dropdown dynamically ===
@callback(
    Output("app-type-dropdown", "options"),
    Output("app-type-dropdown", "value"),
    Input("country-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_app_type_dropdown(country, selected_years):
    if not isinstance(selected_years, list):
        selected_years = [selected_years]

    dfs = []
    for y in selected_years:
        file_path = os.path.join(base_path, f"{country}_{y}.csv")
        if os.path.exists(file_path):
            dfs.append(pd.read_csv(file_path))
    if not dfs:
        return [], None

    df = pd.concat(dfs, ignore_index=True)
    app_types = sorted(df['app_type'].dropna().unique())
    return [{"label": a, "value": a} for a in app_types], app_types[0] if app_types else None

# === Main Graph Callback ===
@callback(
    Output("trend-graph", "figure"),
    Input("granularity-dropdown", "value"),
    Input("app-type-dropdown", "value"),
    Input("country-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_graph(granularity, app_type, country, selected_years):
    if not selected_years or not app_type:
        return px.line(title="⚠️ Please select valid filters.")

    if not isinstance(selected_years, list):
        selected_years = [selected_years]

    # Load only the needed data
    dfs = []
    for year in selected_years:
        file_path = os.path.join(base_path, f"{country}_{year}.csv")
        if os.path.exists(file_path):
            dfs.append(pd.read_csv(file_path))

    if not dfs:
        return px.line(title="⚠️ No data found for selection.")

    df = pd.concat(dfs, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["month"].astype(str)
    df = df[df["app_type"] == app_type]
    df = df[df["classification"] != "Unknown"]

    if granularity == "daily":
        df["time"] = df["date"]
    else:
        df["time"] = pd.to_datetime(df["month"])

    group_cols = ["time", "classification"]
    agg = df.groupby(group_cols)["score_borda"].sum().reset_index()
    agg["relative_score"] = agg.groupby("time")["score_borda"].transform(lambda x: x / x.sum()) * 100

    fig = px.line(
        agg,
        x="time",
        y="relative_score",
        color="classification",
        labels={"relative_score": "Relative Borda Share (%)", "time": granularity.capitalize()},
        title=f"Category Share of Borda Scores ({granularity.capitalize()})"
    )

    fig.update_layout(height=600, legend_title="Category")
    fig.update_yaxes(ticksuffix="%")
    return fig

