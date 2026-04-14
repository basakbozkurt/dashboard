import pandas as pd
import plotly.express as px
import os
from dash import dcc, html, Input, Output, callback
import dash
import dash_bootstrap_components as dbc


# === Load Data ===
data_dir = os.path.join(os.path.dirname(__file__), "../data")

borda_file = os.path.join(data_dir, "global_borda_monthly.csv")
mean_file = os.path.join(data_dir, "global_borda_mean_monthly.csv")
median_file = os.path.join(data_dir, "global_borda_median_monthly.csv")


borda_df = pd.read_csv(borda_file)
mean_df = pd.read_csv(mean_file)
median_df = pd.read_csv(median_file)

# Label and format
borda_df["method"] = "Borda"
mean_df["method"] = "Mean"
median_df["method"] = "Median"

for df in [borda_df, mean_df, median_df]:
    df["month"] = pd.to_datetime(df["month"])
    df.dropna(subset=["classification"], inplace=True)
    df = df[~df["classification"].str.lower().str.startswith("exclusion criteria")]
    df = df[df["classification"] != "Unknown"]

# Combine all
all_df = pd.concat([borda_df, mean_df, median_df], ignore_index=True)

# === Initialize Dash App ===
dash.register_page(__name__, path="/dash_method_trends",
                    name="Compare Category Trends by Aggregation Method",
                    order=5)

# === Layout ===
layout = dbc.Container([
    html.H2("📊 Compare Category Trends by Aggregation Method", className="my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Aggregation Methods"),
            dcc.Dropdown(
                id="method-dropdown",
                options=[{"label": m, "value": m} for m in ["Borda", "Mean", "Median"]],
                value=["Borda", "Mean", "Median"],
                multi=True,
                clearable=False
            )
        ], width=3),

        dbc.Col([
            html.Label("Select Year(s)"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(all_df["month"].dt.year.unique())],
                value=[2022],
                multi=True
            )
        ], width=3),

        dbc.Col([
            html.Label("Category"),
            dcc.Dropdown(
                id="category-dropdown",
                options=[{"label": c, "value": c} for c in sorted(all_df['classification'].dropna().unique())],
                value="Education",
                clearable=False
            )
        ], width=4),
    ], className="mb-4"),

    dcc.Graph(id="trend-graphx")
])

# === Callback ===
@callback(
    Output("trend-graphx", "figure"),
    Input("method-dropdown", "value"),
    Input("year-dropdown", "value"),
    Input("category-dropdown", "value")
)
def update_graph(methods, selected_years, category):
    if not selected_years or not methods:
        return px.line(title="⚠️ Please select year(s) and method(s).")

    filtered = all_df[
        (all_df["app_type"] == "Free") &
        (all_df["classification"] == category) &
        (all_df["method"].isin(methods)) &
        (all_df["month"].dt.year.isin(selected_years))
    ]

    if filtered.empty:
        return px.line(title="⚠️ No data available for selected filters.")

    fig = px.line(
        filtered,
        x="month",
        y="relative_score",
        color="method",
        markers=True,
        title=f"{category} – Free Apps – Aggregation Method Comparison",
        labels={"month": "Month", "relative_score": "Relative Share (%)"}
    )
    fig.update_layout(height=600, legend_title="Aggregation Method")
    fig.update_yaxes(ticksuffix="%")
    return fig
