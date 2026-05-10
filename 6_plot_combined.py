"""Combined 2x2 figure of the four GWL workflow steps."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from _plots import draw_step1, draw_step2, draw_step3, draw_step4
from _style import DATA_DIR, LOCATION, METRIC_LABEL, save


def main() -> None:
    gmst = pd.read_csv(DATA_DIR / "gmst_annual.csv")
    anomaly = pd.read_csv(DATA_DIR / "gmst_anomaly_20yr.csv")
    crossings = pd.read_csv(DATA_DIR / "crossings.csv")
    windows = pd.read_csv(DATA_DIR / "hot_days_at_gwl.csv")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))
    draw_step1(axes[0, 0], gmst)
    draw_step2(axes[0, 1], anomaly)
    draw_step3(axes[1, 0], anomaly, crossings)
    draw_step4(axes[1, 1], windows)

    fig.suptitle(f"GWL workflow — {METRIC_LABEL} at {LOCATION}",
                 fontsize=14, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    save(fig, "gwl_toulouse_hotdays.png")


if __name__ == "__main__":
    main()
