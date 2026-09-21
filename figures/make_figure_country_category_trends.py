"""Figure 1. Monthly category composition of free EdTech app rankings, by country.

Line-graph version (replaces the earlier stacked-area rendering).
Usage:  .venv/bin/python figures/make_figure_country_category_trends.py [--smooth] [--caption]
"""
import glob
import sys
import textwrap
from pathlib import Path
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "pdf.fonttype": 42,   # embed as TrueType so the PDF is editable/searchable
    "ps.fonttype": 42,
    "axes.linewidth": 0.6,
})

COUNTRY_NAMES = {
    "be": "Belgium", "dk": "Denmark", "fr": "France", "de": "Germany",
    "it": "Italy", "jp": "Japan", "no": "Norway", "pl": "Poland",
    "es": "Spain", "ch": "Switzerland", "gb": "United Kingdom",
    "us": "United States",
}

# Order: descending mean share. Colors are Plotly's default qualitative sequence
# assigned in alphabetical category order, matching the earlier draft figure that
# the manuscript text already describes.
CATEGORIES = [
    ("Subject Learning",      "#B6E880"),
    ("Non-Education",         "#AB63FA"),
    ("Teaching and Learning", "#FF97FF"),
    ("Preschool",             "#19D3F3"),
    ("Licensing Exam",        "#00CC96"),
    ("Education Management",  "#EF553B"),
    ("Parents",               "#FFA15A"),
    ("Cognitive Development", "#636EFA"),
    ("Professional & Career", "#FF6692"),
]

# Paths resolve from this file, so the script runs from any working directory.
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data" / "by_country_year"

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"

# Landscape layout gives each panel the width to carry every year label.
LABEL_YEARS = list(range(2017, 2024))

# Raw monthly values, matching the RQ2 dashboard (pages/app_rq2.py).
# Pass --smooth for the superseded 3-month centered rolling mean.
SMOOTH = "--smooth" in sys.argv
SUFFIX = "_lines_smoothed" if SMOOTH else "_lines"

# The caption lives in the manuscript text, not in the figure file. Kept here
# so the two stay in sync; pass --caption to draw it onto the figure.
CAPTION = (
    "Figure 1. Monthly category composition of free EdTech app rankings, by country, 2017-2023. "
    "Each panel shows the share of total monthly Borda score accounted for by each of nine app "
    "categories among free apps in one country. Shares sum to 100% within each country-month. "
    "Apps with an unknown category label are excluded. Countries are ordered alphabetically; the "
    "vertical axis is fixed at 0-60% across panels to permit direct comparison."
)
SHOW_CAPTION = "--caption" in sys.argv


def load_shares():
    cols = ["date", "country", "app_type", "classification", "score_borda"]
    df = pd.concat(
        [pd.read_csv(f, usecols=cols) for f in sorted(DATA_DIR.glob("*.csv"))],
        ignore_index=True,
    )
    df = df[df.app_type == "Free"].copy()
    # "Professional" (29 obs, 3 apps) is an inconsistent label for "Professional & Career".
    df["classification"] = df.classification.replace({"Professional": "Professional & Career"})
    df = df[df.classification != "Unknown"]
    df["month"] = df.date.str.slice(0, 7)

    g = df.groupby(["country", "month", "classification"], observed=True).score_borda.sum().reset_index()
    g["share"] = 100 * g.score_borda / g.groupby(["country", "month"], observed=True).score_borda.transform("sum")
    wide = g.pivot_table(index=["country", "month"], columns="classification", values="share").fillna(0)
    # 3-month centered rolling mean, computed within country on a complete monthly index
    months = pd.period_range("2017-01", "2023-12", freq="M").astype(str)
    out = {}
    for c in wide.index.get_level_values(0).unique():
        sub = wide.loc[c].reindex(months)
        sm = sub.rolling(3, center=True, min_periods=1).mean() if SMOOTH else sub
        out[c] = sm.where(sub.notna().any(axis=1))
    return out, months


def main():
    data, months = load_shares()
    x = pd.to_datetime(months)

    fig, axes = plt.subplots(3, 4, figsize=(10.0, 7.25), sharex=True, sharey=True)
    for ax, code in zip(axes.ravel(), sorted(COUNTRY_NAMES, key=lambda c: COUNTRY_NAMES[c])):
        sub = data[code]
        for name, color in CATEGORIES:
            if name in sub:
                ax.plot(x, sub[name], color=color, lw=1.2, solid_capstyle="round")
        ax.set_title(COUNTRY_NAMES[code], fontsize=9, color=INK, pad=4, loc="left")
        # Pin the time axis to the data range: matplotlib's default 5% margin
        # leaves a blank gap before Jan 2017 and after Dec 2023.
        ax.set_xlim(x[0], x[-1])
        ax.margins(x=0)
        ax.set_ylim(0, 60)
        ax.set_yticks([0, 20, 40, 60])
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=7.5, colors=MUTED, length=2)
        # Tick marks at year boundaries, labels centered on each year's span.
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mticker.NullFormatter())
        ax.xaxis.set_minor_locator(mticker.FixedLocator(
            [mdates.date2num(datetime(y, 7, 1)) for y in LABEL_YEARS]))
        ax.xaxis.set_minor_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(axis="x", which="major", length=2, labelbottom=False)
        ax.tick_params(axis="x", which="minor", length=0, labelbottom=True,
                       labelsize=7, colors=MUTED)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")

    # A per-column ylabel steals width from column 1, putting its time axis on a
    # different scale from the other two; one figure-level label keeps all 12 equal.
    fig.supylabel("Share of Borda score (%)", fontsize=8, color=MUTED, x=0.012)

    handles = [plt.Line2D([], [], color=c, lw=2) for _, c in CATEGORIES]
    fig.legend(handles, [n for n, _ in CATEGORIES], loc="lower center", ncol=5,
               frameon=False, fontsize=8, labelcolor=INK,
               bbox_to_anchor=(0.5, 0.05 if SHOW_CAPTION else 0.015),
               handlelength=1.6, columnspacing=1.4)

    if SHOW_CAPTION:
        fig.text(0.008, 0.005, textwrap.fill(CAPTION, 168), ha="left", va="bottom",
                 fontsize=8, color=INK, linespacing=1.45)

    # Leave clear air between the bottom row of panels and the legend.
    fig.tight_layout(rect=(0, 0.155 if SHOW_CAPTION else 0.105, 1, 1))
    for ext in ("pdf", "png"):
        fig.savefig(HERE / f"figure_country_category_trends{SUFFIX}.{ext}",
                    dpi=300, bbox_inches="tight")

    # Companion table: satisfies the low-contrast "relief" rule and aids replication.
    tidy = pd.concat({c: d for c, d in data.items()}, names=["country", "month"])
    tidy.round(2).to_csv(HERE / f"figure_country_category_trends{SUFFIX}.csv")
    print(f"wrote figure_country_category_trends{SUFFIX}.{{pdf,png,csv}} (smoothed={SMOOTH})")


if __name__ == "__main__":
    main()
