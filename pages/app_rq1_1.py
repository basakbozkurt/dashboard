import pandas as pd
import os
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import dash
from dash import html, dcc, callback, Input, Output

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

# === Initialize Dash App ===
if __name__ != "__main__":
    dash.register_page(__name__, path="/rq1_1",
                        name="RQ1.1: Monthly Category Share as Stacked Bar Chart",
                        order=2)

layout = dbc.Container([
    html.H2("RQ1: Monthly Category Share as Stacked Bar Chart (Sorted)", className="my-3"),

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
        ], width=4),

        dbc.Col([
            html.Label("Year(s)"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": str(y), "value": y} for y in sorted(daily_df['year'].unique())],
                value=[2022],
                multi=True
            )
        ], width=8),
    ], className="mb-4"),
            html.P(
            "This stacked bar chart visualizes the relative distribution of educational app categories over time, using normalized Borda scores aggregated across countries. Each bar represents a time unit (day or month), with segments showing the relative prominence of each category.",
            className="text-muted"
            ),
    dcc.Graph(id="stacked-bar-chart")
])

@callback(
    Output("stacked-bar-chart", "figure"),
    Input("granularity-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_chart(granularity, selected_years):
    if not selected_years:
        return px.bar(title="⚠️ Please select a year.")

    df = daily_df if granularity == "daily" else monthly_df
    time_col = "date" if granularity == "daily" else "month"

    filtered = df[
        (df["app_type"] == "Free") &
        (df["year"].isin(selected_years)) &
        (df["classification"] != "Unknown")
    ].copy()

    filtered["time"] = filtered[time_col]

    agg = filtered.groupby(["time", "classification"])["score_borda"].sum().reset_index()
    agg["relative_score"] = agg.groupby("time")["score_borda"].transform(lambda x: x / x.sum()) * 100

    # Sort categories within each time for stacked display
    agg = agg.sort_values(["time", "relative_score"], ascending=[True, False])

    fig = px.bar(
        agg,
        x="time",
        y="relative_score",
        color="classification",
        labels={"relative_score": "Relative Share (%)", "time": granularity.capitalize()},
        title=f"RQ1: {granularity.capitalize()} Category Share as Stacked Bar Chart (Sorted)",
        color_discrete_sequence=px.colors.qualitative.Set3  # 12-color pastel palette

    )

    fig.update_layout(
        barmode="stack",
        height=600,
        legend_title="Category"
    )
    fig.update_yaxes(ticksuffix="%")
    return fig


