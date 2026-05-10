"""Shared styling helpers for the Toulouse plot scripts."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
FIG_DIR = HERE / "figures"

LOCATION = "Toulouse"
METRIC_LABEL = "Days above 35 °C per year"
BASELINE = (1850, 1900)
ROLLING_WINDOW = 20
RECENT_HISTORICAL_GWL = 1.0


def scenario_colors(scenarios: list[str]) -> dict[str, tuple]:
    cmap = plt.get_cmap("tab10")
    return {sc: cmap(i) for i, sc in enumerate(sorted(scenarios))}


def gwl_colors(gwls: list[float]) -> dict[float, tuple]:
    cmap = plt.get_cmap("plasma")
    gwls = sorted(gwls)
    if len(gwls) == 1:
        return {gwls[0]: cmap(0.4)}
    return {g: cmap(0.15 + 0.6 * i / (len(gwls) - 1)) for i, g in enumerate(gwls)}


def gwl_label(g: float) -> str:
    if g == RECENT_HISTORICAL_GWL:
        return f"+{g}°C (recent hist.)"
    return f"+{g}°C"


def save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / name
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    return out
