"""
Shared `draw_*` functions for the Toulouse step plots.

Each function takes a matplotlib axis and the relevant pandas DataFrame(s)
and renders a single panel. The thin `2_plot_*.py` scripts and
`2_plot_combined.py` both import from here.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from _style import (
    BASELINE,
    METRIC_LABEL,
    RECENT_HISTORICAL_GWL,
    ROLLING_WINDOW,
    gwl_colors,
    gwl_label,
    scenario_colors,
)


def draw_raw_tasmax(ax, df: pd.DataFrame) -> None:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    scenarios = sorted(df["scenario"].unique())
    colors = scenario_colors(scenarios)
    for sc in scenarios:
        sub = df[df["scenario"] == sc]
        ax.scatter(sub["date"], sub["tasmax_C"],
                   s=1.5, alpha=0.05, color=colors[sc])
        annual_max = sub.groupby("year")["tasmax_C"].max()
        ax.plot(pd.to_datetime(annual_max.index, format="%Y"), annual_max.values,
                color=colors[sc], lw=1.6, label=sc.upper())
    ax.axhline(35, color="black", ls=":", lw=1, alpha=0.7,
               label="35 °C threshold")
    ax.set_title("Raw daily tasmax (annual max overlaid)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily tasmax (°C)")
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)


def draw_step1(ax, df: pd.DataFrame) -> None:
    scenarios = sorted(df["scenario"].unique())
    colors = scenario_colors(scenarios)
    for sc in scenarios:
        sub = df[df["scenario"] == sc].sort_values("year")
        ax.plot(sub["year"], sub["gmst_C"], color=colors[sc], lw=1.4,
                label=sc.upper())
    ax.set_title("Step 1 — Annual mean GMST per scenario")
    ax.set_xlabel("Year")
    ax.set_ylabel("GMST (°C)")
    ax.set_xlim(1850, 2105)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)


def draw_step2(ax, df: pd.DataFrame) -> None:
    scenarios = sorted(df["scenario"].unique())
    colors = scenario_colors(scenarios)
    for sc in scenarios:
        sub = df[df["scenario"] == sc].sort_values("year")
        ax.plot(sub["year"], sub["anomaly_C"], color=colors[sc], lw=1.7,
                label=sc.upper())
    ax.axhline(0, color="black", lw=0.7)
    ax.axvspan(BASELINE[0], BASELINE[1], color="grey", alpha=0.22,
               label=f"Baseline {BASELINE[0]}–{BASELINE[1]}")
    ax.axhline(RECENT_HISTORICAL_GWL, color="black", ls=":", lw=1.0,
               label=f"+{RECENT_HISTORICAL_GWL}°C (recent hist.)")
    ax.set_title(
        f"Step 2 — {ROLLING_WINDOW}-yr rolling anomaly vs {BASELINE[0]}–{BASELINE[1]}"
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("ΔT (°C)")
    ax.set_xlim(1850, 2105)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)


def draw_step3(ax, anomaly_df: pd.DataFrame, crossings_df: pd.DataFrame) -> None:
    scenarios = sorted(anomaly_df["scenario"].unique())
    gwls = sorted(crossings_df["gwl"].unique())
    sc_color = scenario_colors(scenarios)
    g_color = gwl_colors(gwls)

    for sc in scenarios:
        sub = anomaly_df[anomaly_df["scenario"] == sc].sort_values("year")
        ax.plot(sub["year"], sub["anomaly_C"], color=sc_color[sc], lw=1.5,
                alpha=0.9)
    for g in gwls:
        ax.axhline(g, color=g_color[g], ls="--", lw=1.1, alpha=0.9)
        ax.text(0.985, g, gwl_label(g), color=g_color[g], fontsize=9,
                va="center", ha="right",
                transform=ax.get_yaxis_transform())
    for _, row in crossings_df.dropna(subset=["crossing_year"]).iterrows():
        ax.scatter([row["crossing_year"]], [row["gwl"]],
                   color=sc_color[row["scenario"]], s=58,
                   edgecolor="black", linewidths=0.7, zorder=5)

    ax.set_title("Step 3 — First-crossing year per scenario × GWL")
    ax.set_xlabel("Year")
    ax.set_ylabel("ΔT (°C)")
    ax.set_xlim(1850, 2105)
    legend = [Line2D([0], [0], color=sc_color[sc], lw=2, label=sc.upper())
              for sc in scenarios]
    legend.append(Line2D([0], [0], color="grey", ls="--", lw=1, label="GWL threshold"))
    legend.append(Line2D([0], [0], marker="o", color="w",
                         markerfacecolor="white", markeredgecolor="black",
                         markersize=7, label="Crossing year"))
    ax.legend(handles=legend, fontsize=9, frameon=False, loc="upper left")
    ax.grid(alpha=0.25)


def draw_step4(ax, windows_df: pd.DataFrame) -> None:
    scenarios = sorted(windows_df["scenario"].unique())
    gwls = sorted(windows_df["gwl"].unique())
    sc_color = scenario_colors(scenarios)
    g_color = gwl_colors(gwls)

    box_data, box_labels, plotted = [], [], []
    for g in gwls:
        sub = windows_df[windows_df["gwl"] == g]
        if sub.empty:
            continue
        plotted.append(g)
        n_scen = sub["scenario"].nunique()
        box_data.append(sub["hot_days"].to_numpy())
        box_labels.append(f"{gwl_label(g)}\nn={len(sub)}\n({n_scen} scen.)")

    if box_data:
        bp = ax.boxplot(
            box_data, tick_labels=box_labels, showmeans=True, patch_artist=True,
            meanprops=dict(marker="D", markerfacecolor="white",
                           markeredgecolor="black", markersize=6),
        )
        for patch, g in zip(bp["boxes"], plotted):
            patch.set_facecolor(g_color[g])
            patch.set_alpha(0.55)

        for x_idx, g in enumerate(plotted, start=1):
            for sc in scenarios:
                vals = windows_df[(windows_df["gwl"] == g) &
                                  (windows_df["scenario"] == sc)]["hot_days"]
                if vals.empty:
                    continue
                ax.scatter([x_idx], [float(np.mean(vals))], color=sc_color[sc],
                           s=42, edgecolor="black", linewidths=0.6, zorder=4)
    else:
        ax.text(0.5, 0.5, "No GWL crossed in any scenario",
                transform=ax.transAxes, ha="center", va="center")

    ax.set_title(f"Step 4 — {METRIC_LABEL} at each GWL (all scenarios pooled)")
    ax.set_ylabel(METRIC_LABEL)
    legend = [Line2D([0], [0], marker="o", color="w",
                     markerfacecolor=sc_color[sc], markeredgecolor="black",
                     markersize=7, label=f"{sc.upper()} mean")
              for sc in scenarios]
    legend.append(Line2D([0], [0], marker="D", color="w",
                         markerfacecolor="white", markeredgecolor="black",
                         markersize=7, label="pooled mean"))
    ax.legend(handles=legend, fontsize=9, frameon=False, loc="upper left")
    ax.grid(alpha=0.25, axis="y")
