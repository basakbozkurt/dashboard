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
                   name="RQ2: App Category Trends Based on Country-Level Rankings", order=2)

# === Layout ===
layout = dbc.Container([
    html.H2("📱 App Category Trends Based on Country-Level Rankings", className="my-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Granularity"),
            dcc.Dropdown(
                id="granularity-dropdown",
                options=[
                    {"label": "Daily", "value": "daily"},
                    {"label": "Monthly", "value": "monthly"},
                ],
                value="monthly",
                clearable=False
            )
        ], width=2),

        dbc.Col([
            html.Label("Country(ies)"),
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c.upper(), "value": c} for c in all_countries],
                value=[all_countries[0]],
                multi=True,
                clearable=False
            )
        ], width=2),

        dbc.Col([
            html.Label("Year(s)"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in all_years],
                value=[all_years[-1]],
                multi=True,
                clearable=False
            )
        ], width=2),
    ], className="mb-4"),
        html.P(
        "This line chart visualizes the temporal distribution of normalised Borda scores across educational app categories. For each country and time point, category-level Borda scores are computed from national app rankings.",
        "The resulting relative shares capture each category’s prominence within the marketplace over time.",
        className="text-muted"),
    dcc.Graph(id="trend-graph")
])

# === Main Graph Callback ===
@callback(
    Output("trend-graph", "figure"),
    Input("granularity-dropdown", "value"),
    Input("country-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_graph(granularity, selected_countries, selected_years):
    if not selected_years or not selected_countries:
        return px.line(title="⚠️ Please select valid filters.")

    if not isinstance(selected_years, list):
        selected_years = [selected_years]
    if not isinstance(selected_countries, list):
        selected_countries = [selected_countries]

    # Load only the needed data
    dfs = []
    for country in selected_countries:
        for year in selected_years:
            file_path = os.path.join(base_path, f"{country}_{year}.csv")
            if os.path.exists(file_path):
                df_country_year = pd.read_csv(file_path)
                df_country_year["country"] = country.upper()
                df_country_year["year"] = year
                dfs.append(df_country_year)

    if not dfs:
        return px.line(title="⚠️ No data found for selection.")

    df = pd.concat(dfs, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["month"].astype(str)
    df = df[df["app_type"] == "Free"]
    df = df[df["classification"] != "Unknown"]

    if granularity == "daily":
        df["time"] = df["date"]
    else:
        # For monthly, use the month column which is already in YYYY-MM format
        df["time"] = pd.to_datetime(df["month"])

    group_cols = ["time", "year", "country", "classification"]
    agg = df.groupby(group_cols)["score_borda"].sum().reset_index()
    agg["relative_score"] = agg.groupby(["time", "year", "country"])["score_borda"].transform(lambda x: x / x.sum()) * 100
    agg["country_year"] = agg["country"] + " " + agg["year"].astype(str)

    fig = px.line(
        agg,
        x="time",
        y="relative_score",
        color="country_year",
        facet_col="classification",
        facet_col_wrap=3,
        labels={"relative_score": "Relative Borda Share (%)", "time": granularity.capitalize()},
        title=f"Country Comparison of Category Share ({granularity.capitalize()}, Free Apps)"
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(height=800, legend_title="Country-Year")
    
    if granularity == "daily":
        fig.update_xaxes(title_text="Daily", tickformat="%Y-%m-%d", nticks=10)
    else:
        fig.update_xaxes(title_text="Monthly", tickformat="%m/%y", nticks=12, tickangle=45)
    
    fig.update_yaxes(ticksuffix="%")
    return fig

